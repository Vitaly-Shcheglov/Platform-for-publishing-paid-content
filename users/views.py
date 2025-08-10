from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required, user_passes_test
from .forms import UserRegistrationForm, UserProfileForm
from django.views.generic.edit import CreateView
from django.urls import reverse_lazy
from django.core.mail import send_mail
from django.core.mail import BadHeaderError
from smtplib import SMTPAuthenticationError
from .models import CustomUser


class UserRegisterView(CreateView):
    form_class = UserRegistrationForm
    template_name = "users/register.html"
    success_url = reverse_lazy("login")

    def form_valid(self, form):
        user = form.save()

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

        return super().form_valid(form)


def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect("home")
        else:
            return render(request, "users/login.html", {"error": "Неверные учетные данные"})
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


@login_required
def profile_view(request):
    return render(request, "users/profile.html", {"user": request.user})


def is_mailing_manager(user):
    return user.groups.filter(name="Post moderator group").exists()


@login_required
@user_passes_test(is_mailing_manager)
def user_list(request):
    users = CustomUser.objects.exclude(is_superuser=True)
    users = users.exclude(groups__name__in=['Post moderator group'])
    return render(request, "users/user_list.html", {"users": users})

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
