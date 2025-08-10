from django.urls import path
from .views import UserRegisterView, login_view, profile_edit, profile_view, user_list, block_user
from django.contrib.auth.views import (
    LogoutView,
    PasswordResetView,
    PasswordResetDoneView,
    PasswordResetConfirmView,
    PasswordResetCompleteView,
)


urlpatterns = [
    path("register/", UserRegisterView.as_view(), name="register"),
    path("login/", login_view, name="login"),
    path("profile/edit/", profile_edit, name="profile_edit"),
    path("logout/", LogoutView.as_view(next_page="home"), name="logout"),
    path("profile/", profile_view, name="profile"),
    path("users/", user_list, name="user_list"),
    path("users/block/<int:user_id>/", block_user, name="block_user"),
    path("password_reset/", PasswordResetView.as_view(), name="password_reset"),
    path("password_reset/done/", PasswordResetDoneView.as_view(), name="password_reset_done"),
    path("reset/<uidb64>/<token>/", PasswordResetConfirmView.as_view(), name="password_reset_confirm"),
    path("reset/done/", PasswordResetCompleteView.as_view(), name="password_reset_complete"),
]
