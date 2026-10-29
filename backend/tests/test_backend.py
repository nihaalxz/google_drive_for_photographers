import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from apps.workspaces.models import Workspace, WorkspaceMembership, WorkspaceRole
from apps.folders.models import Folder
from apps.files.models import FileAsset, UploadStatus
from apps.storage.models import UploadSession
from apps.sharing.models import ShareLink, ShareTargetType
from apps.albums.models import Album, AlbumAsset

User = get_user_model()

@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def user_a():
    return User.objects.create_user(
        username='photographer_a',
        email='a@lensvault.com',
        password='Password123!',
        full_name='Elena Rostova'
    )

@pytest.fixture
def workspace_a(user_a):
    ws = Workspace.objects.create(
        name="Elena Rostova Studio",
        slug="elena-rostova-studio",
        storage_limit_bytes=10000000  # 10 MB limit for test
    )
    WorkspaceMembership.objects.create(
        workspace=ws,
        user=user_a,
        role=WorkspaceRole.OWNER
    )
    return ws

@pytest.fixture
def user_b():
    return User.objects.create_user(
        username='photographer_b',
        email='b@lensvault.com',
        password='Password123!',
        full_name='Marcus Chen'
    )

@pytest.fixture
def workspace_b(user_b):
    ws = Workspace.objects.create(
        name="Marcus Chen Photography",
        slug="marcus-chen-photography",
        storage_limit_bytes=10000000
    )
    WorkspaceMembership.objects.create(
        workspace=ws,
        user=user_b,
        role=WorkspaceRole.OWNER
    )
    return ws


@pytest.mark.django_db
class TestAuthenticationAndIsolation:
    def test_user_registration(self, api_client):
        res = api_client.post('/api/v1/auth/register/', {
            'email': 'newuser@test.com',
            'username': 'newuser',
            'password': 'StrongPassword123!',
            'full_name': 'New Photographer',
            'workspace_name': 'Apex Photo Lab'
        }, format='json')
        assert res.status_code == 201
        assert res.data['user']['email'] == 'newuser@test.com'
        assert res.data['active_workspace']['name'] == 'Apex Photo Lab'

    def test_workspace_isolation(self, api_client, user_a, workspace_a, user_b, workspace_b):
        # Create folder in workspace A
        folder_a = Folder.objects.create(
            workspace=workspace_a,
            name="Private Wedding 2026",
            created_by=user_a
        )

        # Authenticate as User B
        api_client.force_authenticate(user=user_b)

        # User B lists folders - should NOT see User A's folder
        res = api_client.get(f'/api/v1/folders/?workspace_id={workspace_a.id}')
        assert res.data['count'] == 0

        # User B directly tries to access User A's folder by ID
        res_detail = api_client.get(f'/api/v1/folders/{folder_a.id}/')
        assert res_detail.status_code == 404


@pytest.mark.django_db
class TestFoldersAndHierarchy:
    def test_nested_folders_and_breadcrumbs(self, api_client, user_a, workspace_a):
        api_client.force_authenticate(user=user_a)

        # Create parent folder
        res1 = api_client.post('/api/v1/folders/', {
            'workspace_id': str(workspace_a.id),
            'name': 'Weddings'
        }, format='json')
        assert res1.status_code == 201
        parent_id = res1.data['id']

        # Create child folder
        res2 = api_client.post('/api/v1/folders/', {
            'workspace_id': str(workspace_a.id),
            'name': 'Sarah & James',
            'parent': parent_id
        }, format='json')
        assert res2.status_code == 201
        child_id = res2.data['id']

        # Check breadcrumbs
        res_child = api_client.get(f'/api/v1/folders/{child_id}/')
        crumbs = res_child.data['breadcrumbs']
        assert len(crumbs) == 2
        assert crumbs[0]['name'] == 'Weddings'
        assert crumbs[1]['name'] == 'Sarah & James'

    def test_prevent_moving_into_self(self, api_client, user_a, workspace_a):
        api_client.force_authenticate(user=user_a)
        folder = Folder.objects.create(workspace=workspace_a, name="RootFolder", created_by=user_a)

        res = api_client.post(f'/api/v1/folders/{folder.id}/move/', {'parent_id': str(folder.id)}, format='json')
        assert res.status_code == 400


@pytest.mark.django_db
class TestStorageAndUploadSession:
    def test_upload_session_and_quota_check(self, api_client, user_a, workspace_a):
        api_client.force_authenticate(user=user_a)

        # 1. Successful upload session within quota
        res = api_client.post('/api/v1/storage/upload-session/', {
            'workspace_id': str(workspace_a.id),
            'original_filename': 'portrait_sample.jpg',
            'file_size': 2048576,  # ~2MB
            'mime_type': 'image/jpeg'
        }, format='json')
        assert res.status_code == 201
        session_id = res.data['session_id']
        assert 'upload_url' in res.data['presigned_data']

        # 2. Complete the upload
        from unittest.mock import patch
        with patch('apps.storage.views.b2_service.verify_object', return_value={'exists': True, 'size': 2048576, 'etag': 'test-etag-123'}):
            res_comp = api_client.post('/api/v1/storage/upload-complete/', {
                'session_id': session_id,
                'etag': 'test-etag-123',
                'metadata': {
                    'camera_make': 'Sony',
                    'camera_model': 'ILCE-7RM4',
                    'iso': 100,
                    'f_stop': 'f/1.8'
                }
            }, format='json')
            assert res_comp.status_code == 201
            assert res_comp.data['camera_make'] == 'Sony'
            assert res_comp.data['is_image'] is True

        # Check workspace ledger updated
        workspace_a.refresh_from_db()
        assert workspace_a.storage_used_bytes > 0

        # 3. Reject upload session when exceeding quota
        res_exceed = api_client.post('/api/v1/storage/upload-session/', {
            'workspace_id': str(workspace_a.id),
            'original_filename': 'huge_raw_batch.zip',
            'file_size': 50000000,  # 50 MB, exceeds 10MB limit
            'mime_type': 'application/zip'
        }, format='json')
        assert res_exceed.status_code == 400
        assert 'quota exceeded' in res_exceed.data['detail'].lower()


@pytest.mark.django_db
class TestSharingAndClientGalleries:
    def test_album_and_password_share_link(self, api_client, user_a, workspace_a):
        api_client.force_authenticate(user=user_a)

        # Create album
        album = Album.objects.create(
            workspace=workspace_a,
            title="Highland Wedding 2026",
            created_by=user_a
        )

        # Create file and attach to album
        file_asset = FileAsset.objects.create(
            workspace=workspace_a,
            original_filename="bride_arrival.jpg",
            safe_display_name="Bride Arrival",
            object_key="workspaces/test/originals/1/bride_arrival.jpg",
            mime_type="image/jpeg",
            file_size=1024,
            upload_status=UploadStatus.UPLOADED,
            uploaded_by=user_a
        )
        AlbumAsset.objects.create(album=album, file_asset=file_asset)

        # Create password-protected share link
        res_link = api_client.post('/api/v1/sharing/links/', {
            'workspace_id': str(workspace_a.id),
            'title': 'Client Proofing Gallery',
            'target_type': 'ALBUM',
            'album': str(album.id),
            'password': 'clientSecretPassword'
        }, format='json')
        assert res_link.status_code == 201
        token = res_link.data['token']

        # Unauthenticated client accesses link without password -> 401
        client_anon = APIClient()
        res_anon = client_anon.get(f'/api/v1/sharing/public/{token}/')
        assert res_anon.status_code == 401
        assert res_anon.data['is_password_protected'] is True

        # Client accesses with correct password -> 200 with gallery assets
        res_authed = client_anon.get(f'/api/v1/sharing/public/{token}/?password=clientSecretPassword')
        assert res_authed.status_code == 200
        assert len(res_authed.data['assets']) == 1

        # Client favorites the photo
        res_fav = client_anon.post(f'/api/v1/sharing/public/{token}/', {
            'action': 'favorite',
            'file_id': str(file_asset.id)
        }, format='json')
        assert res_fav.status_code == 200
        assert res_fav.data['is_favorite'] is True


@pytest.mark.django_db
class TestFileOperationsAndBulkActions:
    def test_file_trash_restore_and_permanent_delete(self, api_client, user_a, workspace_a):
        api_client.force_authenticate(user=user_a)

        file_asset = FileAsset.objects.create(
            workspace=workspace_a,
            original_filename="golden_hour.jpg",
            safe_display_name="Golden Hour",
            object_key="workspaces/test/originals/2/golden_hour.jpg",
            mime_type="image/jpeg",
            file_size=2000000,
            upload_status=UploadStatus.UPLOADED,
            uploaded_by=user_a
        )
        workspace_a.storage_used_bytes = 2000000
        workspace_a.save()

        # 1. Trash file
        res_del = api_client.delete(f'/api/v1/files/{file_asset.id}/')
        assert res_del.status_code == 204
        file_asset.refresh_from_db()
        assert file_asset.is_deleted is True

        # 2. Restore file
        res_restore = api_client.post(f'/api/v1/files/{file_asset.id}/restore/')
        assert res_restore.status_code == 200
        file_asset.refresh_from_db()
        assert file_asset.is_deleted is False

        # 3. Permanent delete decreases storage used
        res_perm = api_client.delete(f'/api/v1/files/{file_asset.id}/permanent_delete/')
        assert res_perm.status_code == 204
        workspace_a.refresh_from_db()
        assert workspace_a.storage_used_bytes == 0
        assert not FileAsset.objects.filter(id=file_asset.id).exists()

    def test_bulk_actions(self, api_client, user_a, workspace_a):
        api_client.force_authenticate(user=user_a)
        f1 = FileAsset.objects.create(
            workspace=workspace_a,
            original_filename="pic1.jpg",
            safe_display_name="Pic 1",
            object_key="key1",
            upload_status=UploadStatus.UPLOADED,
            uploaded_by=user_a
        )
        f2 = FileAsset.objects.create(
            workspace=workspace_a,
            original_filename="pic2.jpg",
            safe_display_name="Pic 2",
            object_key="key2",
            upload_status=UploadStatus.UPLOADED,
            uploaded_by=user_a
        )

        # Bulk star
        res_star = api_client.post('/api/v1/files/bulk_action/', {
            'action': 'star',
            'file_ids': [str(f1.id), str(f2.id)]
        }, format='json')
        assert res_star.status_code == 200
        f1.refresh_from_db()
        f2.refresh_from_db()
        assert f1.is_starred is True
        assert f2.is_starred is True

