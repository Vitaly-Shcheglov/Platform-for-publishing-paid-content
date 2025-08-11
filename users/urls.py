from django.urls import path
from .views import (
    UserRegisterView,
    LoginView,
    ProfileEditView,
    UserProfileView,
    UserListView,
    block_user,
    register_view,
    login_view,
    profile_view,
    profile_edit,
)
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from django.contrib.auth.views import (
    LogoutView,
    PasswordResetView,
    PasswordResetDoneView,
    PasswordResetConfirmView,
    PasswordResetCompleteView,
)

urlpatterns = [
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path("register/", register_view, name="register"),
    path("api/register/", UserRegisterView.as_view(), name="api_register"),
    path("login/", login_view, name="login"),
    path("api/login/", LoginView.as_view(), name="api_login"),
    path("profile/edit/", profile_edit, name="profile_edit"),
    path("api/profile/edit/", ProfileEditView.as_view(), name="api_profile_edit"),
    path("logout/", LogoutView.as_view(next_page="home"), name="logout"),
    path("profile/", profile_view, name="profile"),
    path("api/profile/", UserProfileView.as_view(), name="api_profile"),
    path("users/", UserListView.as_view(), name="user_list"),
    path("users/block/<int:user_id>/", block_user, name="block_user"),
    path("password_reset/", PasswordResetView.as_view(), name="password_reset"),
    path("password_reset/done/", PasswordResetDoneView.as_view(), name="password_reset_done"),
    path("reset/<uidb64>/<token>/", PasswordResetConfirmView.as_view(), name="password_reset_confirm"),
    path("reset/done/", PasswordResetCompleteView.as_view(), name="password_reset_complete"),
    path('users/<int:user_id>/', UserProfileView.as_view(), name='user_profile'),
]
