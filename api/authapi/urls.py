from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    LoginViewSet,
    TokenRefreshViewSet,
    RegisterViewSet,
    LogoutViewSet,
    ChangePasswordViewSet,
    ResetPasswordViewSet,
    CompanyViewSet,
)

router = DefaultRouter()
router.register(r'login', LoginViewSet, basename='token-login')
router.register(r'refresh', TokenRefreshViewSet, basename='token-refresh')
router.register(r'register', RegisterViewSet, basename='register')
router.register(r'logout', LogoutViewSet, basename='logout')
router.register(r'change-password', ChangePasswordViewSet, basename='change-password')
router.register(r'reset-password', ResetPasswordViewSet, basename='reset-password')
router.register(r'companies', CompanyViewSet, basename='company')  # Company endpoints

urlpatterns = [
    path('', include(router.urls)),
]

