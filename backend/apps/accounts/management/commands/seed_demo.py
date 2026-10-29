import os
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from apps.workspaces.models import Workspace, WorkspaceMembership, WorkspaceRole
from apps.folders.models import Folder
from apps.files.models import FileAsset, UploadStatus
from apps.albums.models import Album, AlbumAsset
from apps.sharing.models import ShareLink, ShareTargetType
from apps.activity.models import ActivityLog

User = get_user_model()

class Command(BaseCommand):
    help = 'Seeds initial demonstration photographer data for LensVault'

    def handle(self, *args, **options):
        self.stdout.write("Seeding LensVault demo data...")

        user, created = User.objects.get_or_create(
            email='demo@lensvault.com',
            defaults={
                'username': 'elenarostova',
                'full_name': 'Elena Rostova',
                'bio': 'Fine Art Wedding & Editorial Photographer based in Milan and London.',
                'timezone': 'Europe/Rome'
            }
        )
        if created:
            user.set_password('Password123!')
            user.save()
            self.stdout.write(self.style.SUCCESS("Created demo user: demo@lensvault.com (Password: Password123!)"))
        else:
            self.stdout.write("Demo user already exists.")

        workspace, ws_created = Workspace.objects.get_or_create(
            slug='elena-rostova-photography',
            defaults={
                'name': 'Elena Rostova Photography',
                'storage_limit_bytes': 21474836480,  # 20 GB
                'storage_used_bytes': 0
            }
        )
        WorkspaceMembership.objects.get_or_create(
            workspace=workspace,
            user=user,
            defaults={'role': WorkspaceRole.OWNER}
        )

        # Folders
        weddings_folder, _ = Folder.objects.get_or_create(
            workspace=workspace,
            name="Weddings",
            parent=None,
            defaults={'created_by': user, 'color': '#3b82f6'}
        )
        lake_como_folder, _ = Folder.objects.get_or_create(
            workspace=workspace,
            name="Sarah & James - Lake Como",
            parent=weddings_folder,
            defaults={'created_by': user, 'color': '#10b981'}
        )
        portraits_folder, _ = Folder.objects.get_or_create(
            workspace=workspace,
            name="Portraits & Editorial",
            parent=None,
            defaults={'created_by': user, 'color': '#f59e0b'}
        )
        raw_folder, _ = Folder.objects.get_or_create(
            workspace=workspace,
            name="RAW Archives",
            parent=None,
            defaults={'created_by': user, 'color': '#6366f1'}
        )

        # Photography assets
        sample_photos = [
            {
                'name': 'Sarah_James_Ceremony_0142.jpg',
                'display': 'Lake Como Villa Balbianello Ceremony',
                'folder': lake_como_folder,
                'size': 18452000,
                'mime': 'image/jpeg',
                'ext': 'jpg',
                'width': 6000,
                'height': 4000,
                'make': 'Sony',
                'model': 'ILCE-7RM5',
                'lens': 'FE 50mm F1.2 GM',
                'iso': 100,
                'f_stop': 'f/1.4',
                'shutter': '1/2000s',
                'focal': '50mm',
                'starred': True
            },
            {
                'name': 'Sarah_James_Sunset_Gondola_0881.jpg',
                'display': 'Golden Hour Wooden Riva Boat',
                'folder': lake_como_folder,
                'size': 24105000,
                'mime': 'image/jpeg',
                'ext': 'jpg',
                'width': 6000,
                'height': 4000,
                'make': 'Sony',
                'model': 'ILCE-7RM5',
                'lens': 'FE 85mm F1.4 GM',
                'iso': 160,
                'f_stop': 'f/1.8',
                'shutter': '1/1250s',
                'focal': '85mm',
                'starred': True
            },
            {
                'name': 'Sarah_James_Reception_Dancing_1204.jpg',
                'display': 'First Dance under Venetian Chandeliers',
                'folder': lake_como_folder,
                'size': 16200000,
                'mime': 'image/jpeg',
                'ext': 'jpg',
                'width': 6000,
                'height': 4000,
                'make': 'Sony',
                'model': 'ILCE-7RM5',
                'lens': 'FE 35mm F1.4 GM',
                'iso': 1600,
                'f_stop': 'f/1.4',
                'shutter': '1/400s',
                'focal': '35mm',
                'starred': False
            },
            {
                'name': 'Vogue_Editorial_Milan_Look_04.jpg',
                'display': 'Milan Fashion Week Editorial Portrait',
                'folder': portraits_folder,
                'size': 31200000,
                'mime': 'image/jpeg',
                'ext': 'jpg',
                'width': 8192,
                'height': 5464,
                'make': 'Canon',
                'model': 'EOS R5',
                'lens': 'RF 85mm F1.2 L USM',
                'iso': 100,
                'f_stop': 'f/1.2',
                'shutter': '1/800s',
                'focal': '85mm',
                'starred': True
            },
            {
                'name': 'Lake_Como_Master_RAW_0142.CR3',
                'display': 'Lake Como Master RAW (Original Uncompressed)',
                'folder': raw_folder,
                'size': 58400000,
                'mime': 'application/x-canon-cr3',
                'ext': 'cr3',
                'width': 8192,
                'height': 5464,
                'make': 'Canon',
                'model': 'EOS R5',
                'lens': 'RF 50mm F1.2 L USM',
                'iso': 100,
                'f_stop': 'f/1.4',
                'shutter': '1/2000s',
                'focal': '50mm',
                'starred': False
            }
        ]

        total_bytes = 0
        created_file_assets = []

        for p in sample_photos:
            obj_key = f"workspaces/{workspace.id}/originals/demo/{p['name']}"
            asset, _ = FileAsset.objects.get_or_create(
                object_key=obj_key,
                defaults={
                    'workspace': workspace,
                    'folder': p['folder'],
                    'original_filename': p['name'],
                    'safe_display_name': p['display'],
                    'mime_type': p['mime'],
                    'file_size': p['size'],
                    'file_extension': p['ext'],
                    'upload_status': UploadStatus.UPLOADED,
                    'width': p['width'],
                    'height': p['height'],
                    'camera_make': p['make'],
                    'camera_model': p['model'],
                    'lens_model': p['lens'],
                    'iso': p['iso'],
                    'f_stop': p['f_stop'],
                    'shutter_speed': p['shutter'],
                    'focal_length': p['focal'],
                    'date_taken': timezone.now(),
                    'is_starred': p['starred'],
                    'uploaded_by': user
                }
            )
            total_bytes += p['size']
            created_file_assets.append(asset)

        workspace.storage_used_bytes = total_bytes
        workspace.save(update_fields=['storage_used_bytes'])

        # Create Client Album
        album, _ = Album.objects.get_or_create(
            workspace=workspace,
            title="Sarah & James — Villa Balbianello",
            defaults={
                'description': 'Official wedding proofing gallery and high-resolution master collection.',
                'client_name': 'Sarah & James Sterling',
                'client_email': 'sarah.sterling@example.com',
                'event_date': timezone.now().date(),
                'cover_asset': created_file_assets[0] if created_file_assets else None,
                'created_by': user,
                'is_starred': True
            }
        )

        for idx, asset in enumerate(created_file_assets[:3]):
            AlbumAsset.objects.get_or_create(
                album=album,
                file_asset=asset,
                defaults={'sort_order': idx, 'is_favorite': (idx == 0)}
            )

        # Create Client Proofing Share Link
        share_link, _ = ShareLink.objects.get_or_create(
            token='lake-como-sarah-james-2026',
            defaults={
                'workspace': workspace,
                'title': 'Sarah & James — Lake Como Wedding Collection',
                'target_type': ShareTargetType.ALBUM,
                'album': album,
                'allow_downloads': True,
                'allow_favorites': True,
                'is_active': True
            }
        )

        ActivityLog.objects.create(
            workspace=workspace,
            user=user,
            action='SEED_DATA',
            target_type='WORKSPACE',
            target_id=str(workspace.id),
            description='Initialized photography portfolio and demo client gallery'
        )

        self.stdout.write(self.style.SUCCESS(f"Successfully seeded demo data! Client gallery token: {share_link.token}"))
