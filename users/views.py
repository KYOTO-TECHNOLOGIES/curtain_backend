from django.conf import settings
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken

from .models import AppPermission, Role, User
from .permissions import IsAdminOrSelf
from .serializers import (
    AppPermissionSerializer,
    ChangePasswordSerializer,
    LoginSerializer,
    RoleSerializer,
    UserCreateSerializer,
    UserSerializer,
)


def set_auth_cookies(response, access_token=None, refresh_token=None):
    cookie_common = {
        "httponly": True,
        "secure": settings.AUTH_COOKIE_SECURE,
        "samesite": settings.AUTH_COOKIE_SAMESITE,
        "path": "/",
    }
    if access_token:
        response.set_cookie(
            settings.AUTH_COOKIE_ACCESS,
            access_token,
            max_age=settings.AUTH_COOKIE_ACCESS_MAX_AGE,
            **cookie_common,
        )
    if refresh_token:
        response.set_cookie(
            settings.AUTH_COOKIE_REFRESH,
            refresh_token,
            max_age=settings.AUTH_COOKIE_REFRESH_MAX_AGE,
            **cookie_common,
        )
    return response


def clear_auth_cookies(response):
    response.delete_cookie(settings.AUTH_COOKIE_ACCESS, path="/")
    response.delete_cookie(settings.AUTH_COOKIE_REFRESH, path="/")
    return response


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]

        refresh = RefreshToken.for_user(user)
        access = str(refresh.access_token)

        response = Response(
            {
                "user": UserSerializer(user).data,
                "access": access,
                "refresh": str(refresh),
            },
            status=status.HTTP_200_OK,
        )
        return set_auth_cookies(response, access_token=access, refresh_token=str(refresh))


class RefreshView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        refresh_token = request.data.get("refresh") or request.COOKIES.get(settings.AUTH_COOKIE_REFRESH)
        if not refresh_token:
            return Response({"detail": "Refresh token is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            token = RefreshToken(refresh_token)
            user = User.objects.get(id=token["user_id"], is_active=True)
        except (TokenError, KeyError, User.DoesNotExist):
            response = Response({"detail": "Invalid or expired refresh token."}, status=status.HTTP_401_UNAUTHORIZED)
            return clear_auth_cookies(response)

        access = str(token.access_token)
        response = Response(
            {
                "access": access,
                "refresh": refresh_token,
                "user": UserSerializer(user).data,
            },
            status=status.HTTP_200_OK,
        )
        return set_auth_cookies(response, access_token=access)


class LogoutView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        refresh_token = request.data.get("refresh") or request.COOKIES.get(settings.AUTH_COOKIE_REFRESH)

        if refresh_token:
            try:
                RefreshToken(refresh_token).blacklist()
            except TokenError:
                pass

        response = Response({"detail": "Logged out successfully."}, status=status.HTTP_200_OK)
        return clear_auth_cookies(response)


class MeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(UserSerializer(request.user).data)


class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"detail": "Password changed successfully."}, status=status.HTTP_200_OK)


class UserListCreateView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        users = User.objects.select_related("role").all()
        return Response(UserSerializer(users, many=True).data)

    def post(self, request):
        serializer = UserCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)


class UserDetailView(APIView):
    permission_classes = [IsAuthenticated, IsAdminOrSelf]

    def get_object(self, pk):
        return get_object_or_404(User.objects.select_related("role"), pk=pk)

    def get(self, request, pk):
        user = self.get_object(pk)
        self.check_object_permissions(request, user)
        return Response(UserSerializer(user).data)

    def patch(self, request, pk):
        user = self.get_object(pk)
        self.check_object_permissions(request, user)
        serializer = UserSerializer(user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def delete(self, request, pk):
        user = self.get_object(pk)
        self.check_object_permissions(request, user)
        user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class RoleListCreateView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        roles = Role.objects.prefetch_related("permissions").all()
        return Response(RoleSerializer(roles, many=True).data)

    def post(self, request):
        serializer = RoleSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        role = serializer.save()
        return Response(RoleSerializer(role).data, status=status.HTTP_201_CREATED)


class RoleDetailView(APIView):
    permission_classes = [IsAdminUser]

    def get_object(self, pk):
        return get_object_or_404(Role.objects.prefetch_related("permissions"), pk=pk)

    def get(self, request, pk):
        role = self.get_object(pk)
        return Response(RoleSerializer(role).data)

    def patch(self, request, pk):
        role = self.get_object(pk)
        serializer = RoleSerializer(role, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(RoleSerializer(role).data)

    def delete(self, request, pk):
        role = self.get_object(pk)
        role.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class PermissionListCreateView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        permissions = AppPermission.objects.all()
        return Response(AppPermissionSerializer(permissions, many=True).data)

    def post(self, request):
        serializer = AppPermissionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        permission = serializer.save()
        return Response(AppPermissionSerializer(permission).data, status=status.HTTP_201_CREATED)


class PermissionDetailView(APIView):
    permission_classes = [IsAdminUser]

    def get_object(self, pk):
        return get_object_or_404(AppPermission, pk=pk)

    def get(self, request, pk):
        permission = self.get_object(pk)
        return Response(AppPermissionSerializer(permission).data)

    def patch(self, request, pk):
        permission = self.get_object(pk)
        serializer = AppPermissionSerializer(permission, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(AppPermissionSerializer(permission).data)

    def delete(self, request, pk):
        permission = self.get_object(pk)
        permission.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)