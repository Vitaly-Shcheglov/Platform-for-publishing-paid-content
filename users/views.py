from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required, user_passes_test
from .forms import  UserProfileForm, UserRegistrationForm
from django.core.mail import BadHeaderError
from smtplib import SMTPAuthenticationError
from .models import CustomUser
from django.contrib.auth import get_user_model
from rest_framework import permissions
from rest_framework.views import APIView
from django.utils.decorators import method_decorator
from rest_framework.permissions import IsAuthenticated
from django.core.mail import send_mail
from .serializers import UserRegistrationSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib import messages


User = get_user_model()

class UserRegisterView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)

        if serializer.is_valid():
            user = serializer.save()

            try:
                send_mail(
                    "Добро пожаловать!",
                    "Спасибо за регистрацию на нашем сайте.",
                    "from@example.com",  # Замените на ваш реальный адрес
                    [user.email],
                    fail_silently=False,
                )
            except SMTPAuthenticationError:
                print("Ошибка аутентификации SMTP: неверный пользователь или пароль.")
            except BadHeaderError:
                print("Некорректный заголовок письма.")
            except Exception as e:
                print(f"Ошибка при отправке письма: {e}")

            return Response({"message": "Пользователь успешно зарегистрирован."}, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        phone_number = request.data.get("phone_number")
        password = request.data.get("password")
        user = authenticate(request, phone_number=phone_number, password=password)

        if user is not None:
            refresh = RefreshToken.for_user(user)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            })
        return Response({"error": "Неверные учетные данные"}, status=status.HTTP_401_UNAUTHORIZED)


class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, user_id=None):
        if user_id is None:
            user = request.user
        else:
            user = get_object_or_404(CustomUser, id=user_id)

        serializer = UserProfileSerializer(user)
        return Response(serializer.data)


class ProfileEditView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Отображает форму редактирования профиля."""
        form = UserProfileForm(instance=request.user)
        return Response({"form": form.as_p()})

    def post(self, request):
        """Обрабатывает редактирование профиля."""
        form = UserProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            return Response({"message": "Профиль успешно обновлен."}, status=status.HTTP_200_OK)
        return Response(form.errors, status=status.HTTP_400_BAD_REQUEST)


@method_decorator(login_required, name='dispatch')
class UserListView(APIView):
    def get(self, request):
        users = CustomUser.objects.exclude(is_superuser=True)
        users = users.exclude(groups__name__in=['Post moderator group'])
        return Response({"users": users.values()})

def is_post_manager(user):
    return user.groups.filter(name="Post moderator group").exists()

@login_required
def profile_view(request):
    return render(request, "users/profile.html", {"user": request.user})

@login_required
def user_profile_view(request, user_id):
    """Просмотр профиля другого пользователя."""
    user = get_object_or_404(CustomUser, id=user_id)
    return render(request, "users/user_profile.html", {"user": user})

def block_user(request, user_id):
    user = get_object_or_404(CustomUser, id=user_id)
    user.is_blocked = not user.is_blocked
    user.save()
    return redirect("user_list")

def register_view(request):
    if request.method == "POST":
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()

            try:
                send_mail(
                    "Добро пожаловать!",
                    "Спасибо за регистрацию на нашем сайте.",
                    "from@example.com",
                    [user.email],
                    fail_silently=False,
                )
            except SMTPAuthenticationError:
                print("Ошибка аутентификации SMTP: неверный пользователь или пароль.")
            except BadHeaderError:
                print("Некорректный заголовок письма.")
            except Exception as e:
                print(f"Ошибка при отправке письма: {e}")

            return redirect("login")
    else:
        form = UserRegistrationForm()

    return render(request, "users/register.html", {"form": form})

def login_view(request):
    if request.method == "POST":
        phone_number = request.POST.get("phone_number")
        password = request.POST.get("password")
        user = authenticate(request, phone_number=phone_number, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, "Успешный вход в систему!")
            return redirect("home")
        else:
            messages.error(request, "Неверные учетные данные.")

    return render(request, "users/login.html")

@login_required
def profile_edit(request):
    if request.method == "POST":
        form = UserProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect("profile")
    else:
        form = UserProfileForm(instance=request.user)
    return render(request, "users/profile_edit.html", {"form": form})


class CustomTokenObtainPairView(TokenObtainPairView):
    """
    View для получения JWT токена.

    Позволяет пользователям получать токен для аутентификации.
    Доступен для всех пользователей (включая неаутентифицированных).
    """
    permission_classes = []
