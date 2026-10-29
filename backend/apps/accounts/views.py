from rest_framework import status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.utils.text import slugify
from django.conf import settings
import uuid

from .serializers import UserSerializer, RegisterSerializer, LoginSerializer, ChangePasswordSerializer
from apps.workspaces.models import Workspace, WorkspaceMembership, WorkspaceRole
from apps.workspaces.serializers import WorkspaceSerializer
from apps.activity.models import ActivityLog

from django.views.decorators.csrf import ensure_csrf_cookie
from django.utils.decorators import method_decorator

User = get_user_model()

class CsrfTokenView(APIView):
    authentication_classes = []
    permission_classes = [permissions.AllowAny]

    @method_decorator(ensure_csrf_cookie)
    def get(self, request):
        return Response({'detail': 'CSRF cookie established'})

class RegisterView(APIView):
    authentication_classes = []
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data
        user = User.objects.create_user(
            username=data['username'],
            email=data['email'],
            password=data['password'],
            full_name=data.get('full_name', '')
        )

        ws_name = data.get('workspace_name') or f"{user.full_name or user.username}'s Vault"
        unique_slug = f"{slugify(ws_name)}-{uuid.uuid4().hex[:6]}"
        workspace = Workspace.objects.create(
            name=ws_name,
            slug=unique_slug,
            storage_limit_bytes=settings.DEFAULT_WORKSPACE_QUOTA_BYTES
        )
        WorkspaceMembership.objects.create(
            workspace=workspace,
            user=user,
            role=WorkspaceRole.OWNER
        )

        login(request, user)

        ActivityLog.objects.create(
            workspace=workspace,
            user=user,
            action='REGISTER',
            target_type='USER',
            target_id=str(user.id),
            description=f"User {user.email} registered account and created workspace {workspace.name}"
        )

        return Response({
            'user': UserSerializer(user).data,
            'active_workspace': WorkspaceSerializer(workspace).data
        }, status=status.HTTP_201_CREATED)


class LoginView(APIView):
    authentication_classes = []
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        login_input = serializer.validated_data['email'].strip()
        password = serializer.validated_data['password']

        user = None
        # Support either email or username input
        try:
            if '@' in login_input:
                target_user = User.objects.get(email__iexact=login_input)
            else:
                target_user = User.objects.get(username__iexact=login_input)
            user = authenticate(request, username=target_user.email, password=password)
        except User.DoesNotExist:
            user = authenticate(request, username=login_input, password=password)

        if not user:
            return Response({'detail': 'Invalid email or password.'}, status=status.HTTP_401_UNAUTHORIZED)

        login(request, user)

        # Get first workspace
        membership = WorkspaceMembership.objects.filter(user=user).select_related('workspace').first()
        workspace = membership.workspace if membership else None

        return Response({
            'user': UserSerializer(user).data,
            'active_workspace': WorkspaceSerializer(workspace).data if workspace else None
        })


class LogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        logout(request)
        return Response({'detail': 'Successfully logged out.'})


class MeView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        memberships = WorkspaceMembership.objects.filter(user=user).select_related('workspace')
        workspaces = [m.workspace for m in memberships]
        active_ws = workspaces[0] if workspaces else None

        return Response({
            'user': UserSerializer(user).data,
            'workspaces': WorkspaceSerializer(workspaces, many=True).data,
            'active_workspace': WorkspaceSerializer(active_ws).data if active_ws else None
        })

    def patch(self, request):
        serializer = UserSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ChangePasswordView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        user = request.user
        if not user.check_password(serializer.validated_data['old_password']):
            return Response({'old_password': ['Incorrect current password.']}, status=status.HTTP_400_BAD_REQUEST)

        user.set_password(serializer.validated_data['new_password'])
        user.save()
        return Response({'detail': 'Password updated successfully.'})
