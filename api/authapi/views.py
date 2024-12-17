from rest_framework import status, permissions, viewsets
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken
from django.contrib.auth import authenticate
from .models import CustomUser, Company
from .serializers import UserRegistrationSerializer, CompanySerializer
from django.contrib.auth.hashers import check_password

class CompanyViewSet(viewsets.ModelViewSet):
    queryset = Company.objects.all()
    serializer_class = CompanySerializer
    permission_classes = [permissions.IsAuthenticated]


class RegisterViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            company = request.user.company

            user = serializer.save(company=company)
            return Response(
                {
                    "status": True,
                    "message": "User registered successfully.",
                    "data": {
                        "id": user.id,
                        "email": user.email,
                        "username": user.username,
                        "phone_number": user.phone_number,
                        "role": user.role,
                        "company_id": user.company.id,
                    }
                },
                status=status.HTTP_201_CREATED,
            )
        return Response(
            {
                "status": False,
                "message": "Registration failed.",
                "data": serializer.errors
            },
            status=status.HTTP_400_BAD_REQUEST,
        )


class LoginViewSet(viewsets.ViewSet):
    permission_classes = [permissions.AllowAny]

    def create(self, request):
        identifier = request.data.get("email")
        password = request.data.get("password")

        if not identifier:
            return Response(
                {
                    "status": False,
                    "message": "Email/Phone number is required.",
                    "data": 'Null',
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not password:
            return Response(
                {
                    "status": False,
                    "message": "Password is required.",
                    "data": 'Null',
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = CustomUser.objects.filter(email=identifier).first() or CustomUser.objects.filter(phone_number=identifier).first()

        if user and authenticate(request, email=user.email, password=password):
            refresh = RefreshToken.for_user(user)
            return Response(
                {
                    "status": True,
                    "message": "Login successful.",
                    "data": {
                        "refresh": str(refresh),
                        "access": str(refresh.access_token),
                        "user": {
                            "id": user.id,
                            "email": user.email,
                            "username": user.username,
                            "phone_number": user.phone_number,
                            "role": user.role,
                            "company_id": user.company.id,
                        },
                    },
                },
                status=status.HTTP_200_OK,
            )

        return Response(
            {
                "status": False,
                "message": "Invalid credentials.",
                "data": 'Null',
            },
            status=status.HTTP_401_UNAUTHORIZED,
        )


class TokenRefreshViewSet(viewsets.ViewSet):
    permission_classes = [permissions.AllowAny]

    def create(self, request):
        refresh_token = request.data.get("refresh")

        if not refresh_token:
            return Response(
                {
                    "status": False,
                    "message": "Refresh token is required.",
                    "data": 'Null',
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            refresh = RefreshToken(refresh_token)
            access_token = str(refresh.access_token)
            return Response(
                {
                    "status": True,
                    "message": "Access token refreshed successfully.",
                    "data": {
                        "access": access_token,
                    },
                },
                status=status.HTTP_200_OK,
            )
        except (TokenError, InvalidToken) as e:
            return Response(
                {
                    "status": False,
                    "message": f"Invalid refresh token: {str(e)}",
                    "data": 'Null',
                },
                status=status.HTTP_401_UNAUTHORIZED,
            )


class LogoutViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request):
        refresh_token = request.data.get("refresh")

        if not refresh_token:
            return Response(
                {
                    "status": False,
                    "message": "Refresh token is required.",
                    "data": None,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response(
                {
                    "status": True,
                    "message": "Logout successful.",
                    "data": None,
                },
                status=status.HTTP_200_OK,
            )
        except Exception:
            return Response(
                {
                    "status": False,
                    "message": "Invalid token or token already blacklisted.",
                    "data": None,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )


class ChangePasswordViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request):
        user = request.user
        old_password = request.data.get("old_password")
        new_password = request.data.get("new_password")
        confirm_password = request.data.get("confirm_password")

        if not old_password or not new_password or not confirm_password:
            return Response(
                {
                    "status": False,
                    "message": "All fields (old_password, new_password, confirm_password) are required.",
                    "data": None,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not check_password(old_password, user.password):
            return Response(
                {
                    "status": False,
                    "message": "Old password is incorrect.",
                    "data": None,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        if new_password != confirm_password:
            return Response(
                {
                    "status": False,
                    "message": "New password and confirm password do not match.",
                    "data": None,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        user.set_password(new_password)
        user.save()

        return Response(
            {
                "status": True,
                "message": "Password changed successfully.",
                "data": None,
            },
            status=status.HTTP_200_OK,
        )


class ResetPasswordViewSet(viewsets.ViewSet):
    permission_classes = [permissions.AllowAny]

    def create(self, request):
        email = request.data.get("email")
        new_password = request.data.get("password")
        confirm_password = request.data.get("confirm_password")

        # Validate inputs
        if not email or not new_password or not confirm_password:
            return Response(
                {
                    "status": False,
                    "message": "All fields (email, password, confirm_password) are required.",
                    "data": None,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        if new_password != confirm_password:
            return Response(
                {
                    "status": False,
                    "message": "Password and confirm password do not match.",
                    "data": None,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            user = CustomUser.objects.get(email=email)
            user.set_password(new_password)
            user.save()

            return Response(
                {
                    "status": True,
                    "message": "Password reset successfully.",
                    "data": None,
                },
                status=status.HTTP_200_OK,
            )

        except CustomUser.DoesNotExist:
            return Response(
                {
                    "status": False,
                    "message": "User with the given email does not exist.",
                    "data": None,
                },
                status=status.HTTP_404_NOT_FOUND,
            )
