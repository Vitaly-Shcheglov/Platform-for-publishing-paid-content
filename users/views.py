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
    """
    Представление для регистрации пользователей.

    Это представление обрабатывает POST-запросы для регистрации новых пользователей.
    После успешной регистрации пользователю отправляется приветственное письмо.

    Атрибуты:
        permission_classes (list): Список классов разрешений, которые определяют, кто
            может получить доступ к этому представлению. В данном случае доступ открыт
            для всех (permissions.AllowAny).
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        """
        Обрабатывает POST-запрос для регистрации нового пользователя.

        Принимает данные пользователя, проверяет их валидность с помощью сериализатора
        и создает нового пользователя. При успешном создании отправляется приветственное
        письмо на указанный электронный адрес.

        Параметры:
            request (Request): Объект запроса, содержащий данные для регистрации.

        Возвращает:
            Response: Сообщение об успешной регистрации или ошибки валидации
            с соответствующим статусом HTTP.
        """
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
    """
    Представление для входа пользователей.

    Это представление обрабатывает POST-запросы для аутентификации пользователей
    по номеру телефона и паролю. При успешной аутентификации возвращает токены доступа.

    Атрибуты:
        permission_classes (list): Список классов разрешений, которые определяют, кто
            может получить доступ к этому представлению. В данном случае доступ открыт
            для всех (permissions.AllowAny).
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        """
        Обрабатывает POST-запрос для входа пользователя.

        Принимает номер телефона и пароль, а затем аутентифицирует пользователя.
        Если аутентификация успешна, возвращает токены доступа.

        Параметры:
            request (Request): Объект запроса, содержащий номер телефона и пароль.

        Возвращает:
            Response: Токены доступа или сообщение об ошибке с соответствующим статусом HTTP.
        """
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
    """
    Представление для получения профиля пользователя.

    Это представление обрабатывает GET-запросы для получения информации о пользователе.
    Если userid не указан, возвращает информацию о текущем аутентифицированном пользователе.

    Атрибуты:
        permissionclasses (list): Список классов разрешений, которые определяют, кто
            может получить доступ к этому представлению. В данном случае доступ открыт
            только для аутентифицированных пользователей (IsAuthenticated).
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, user_id=None):
        """
        Обрабатывает GET-запрос для получения данных профиля пользователя.

        Если userid не указан, возвращает данные текущего аутентифицированного пользователя.
        В противном случае возвращает данные указанного пользователя.

        Параметры:
            request (Request): Объект запроса.
            userid (int): Идентификатор пользователя (по желанию).

        Возвращает:
            Response: Данные профиля пользователя.
        """
        if user_id is None:
            user = request.user
        else:
            user = get_object_or_404(CustomUser, id=user_id)

        serializer = UserProfileSerializer(user)
        return Response(serializer.data)


class ProfileEditView(APIView):
    """
    Представление для редактирования профиля пользователя.

    Это представление обрабатывает GET- и POST-запросы для отображения формы редактирования
    профиля и обработки обновления данных профиля.

    Атрибуты:
        permissionclasses (list): Список классов разрешений, которые определяют, кто
            может получить доступ к этому представлению. В данном случае доступ открыт
            только для аутентифицированных пользователей (IsAuthenticated).
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """
        Обрабатывает GET-запрос для отображения формы редактирования профиля пользователя.

        Этот метод создает экземпляр формы `UserProfileForm`, инициализированной текущим
        пользователем (request.user), что позволяет пользователю видеть и редактировать
        свои данные. Форма отображается в виде HTML, готовая для рендеринга.

        Параметры:
            request (Request): Объект запроса, содержащий информацию о текущем запросе,
                            включая аутентифицированного пользователя.

        Возвращает:
            Response: Объект ответа, содержащий HTML-код формы редактирования профиля
                    в виде словаря. Форматируется для последующего рендеринга на клиенте.
                    Статус ответа по умолчанию 200 (OK).

        Примечания:
            - Метод предполагает, что пользователь уже аутентифицирован и имеет доступ
            к редактированию своего профиля.
            - Форма будет отображена с текущими значениями полей, что позволяет
            пользователю видеть свои данные перед редактированием.
        """
        form = UserProfileForm(instance=request.user)
        return Response({"form": form.as_p()})

    def post(self, request):
        """
        Обрабатывает POST-запрос для редактирования данных профиля пользователя.

        Этот метод принимает данные, отправленные пользователем через форму редактирования
        профиля. Если данные валидны, они сохраняются, и пользователю возвращается
        сообщение об успешном обновлении профиля. В противном случае возвращаются ошибки
        валидации.

        Параметры:
            request (Request): Объект запроса, содержащий данные формы, отправленные
                            пользователем, а также информацию о текущем запросе.

        Возвращает:
            Response: Объект ответа, содержащий сообщение об успешном обновлении или
                    ошибки валидации. Статус ответа 200 (OK) при успешном обновлении
                    или 400 (Bad Request) при ошибках валидации.

        Примечания:
            - Метод использует `UserProfileForm` для обработки данных пользователя.
            - Если форма не валидна, возвращается словарь с ошибками, что позволяет
            клиенту отобразить их пользователю.
            - Необходимо убедиться, что пользователь аутентифицирован и имеет право
            на редактирование своего профиля перед вызовом этого метода.
        """
        form = UserProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            return Response({"message": "Профиль успешно обновлен."}, status=status.HTTP_200_OK)
        return Response(form.errors, status=status.HTTP_400_BAD_REQUEST)


@method_decorator(login_required, name='dispatch')
class UserListView(APIView):
    """
    Представление для получения списка пользователей.

    Это представление обрабатывает GET-запросы для получения списка всех
    пользователей, исключая суперпользователей и пользователей в группе
    модераторов постов.

    Атрибуты:
        permission_classes (list): Список классов разрешений, которые определяют
            доступ к этому представлению. В данном случае доступ открыт только
            для аутентифицированных пользователей.

    Методы:
        get(request): Обрабатывает GET-запрос и возвращает список пользователей.
    """
    def get(self, request):
        """
        Обрабатывает GET-запрос для получения списка пользователей.

        Возвращает список пользователей, исключая суперпользователей и
        пользователей, относящихся к группе модераторов постов.

        Параметры:
            request (Request): Объект запроса, который содержит информацию о текущем
                                запросе, включая аутентифицированного пользователя.

        Возвращает:
            Response: Объект ответа, содержащий список пользователей в формате JSON.
                        Статус ответа 200 (OK).
        """
        users = CustomUser.objects.exclude(is_superuser=True)
        users = users.exclude(groups__name__in=['Post moderator group'])
        return Response({"users": users.values()})

def is_post_manager(user):
    """
    Проверяет, является ли пользователь менеджером постов.

    Эта функция проверяет, входит ли указанный пользователь в группу
    "Post moderator group".

    Параметры:
        user (CustomUser): Пользователь, которого нужно проверить.

    Возвращает:
        bool: True, если пользователь является менеджером постов, иначе False.
    """
    return user.groups.filter(name="Post moderator group").exists()

@login_required
def profile_view(request):
    """
    Отображает профиль текущего аутентифицированного пользователя.

    Этот метод обрабатывает GET-запрос и возвращает страницу профиля
    текущего пользователя.

    Параметры:
        request (HttpRequest): Объект запроса.

    Возвращает:
        HttpResponse: Отображает страницу профиля текущего пользователя.
    """
    return render(request, "users/profile.html", {"user": request.user})

@login_required
def user_profile_view(request, user_id):
    """
    Просмотр профиля другого пользователя.

    Этот метод обрабатывает GET-запрос для отображения профиля указанного
    пользователя. Если пользователь с указанным user_id не найден, возвращается
    ошибка 404.

    Параметры:
        request (HttpRequest): Объект запроса.
        user_id (int): Идентификатор пользователя, профиль которого нужно просмотреть.

    Возвращает:
        HttpResponse: Отображает страницу профиля другого пользователя или
                      возвращает ошибку 404, если пользователь не найден.
    """
    user = get_object_or_404(CustomUser, id=user_id)
    return render(request, "users/user_profile.html", {"user": user})

def block_user(request, user_id):
    """
    "Блокирует или разблокирует пользователя.

    "Этот метод обрабатывает POST-запрос для изменения статуса блокировки
    "пользователя с указанным user_id. Если пользователь заблокирован, он
    "будет разблокирован, и наоборот.

    "Параметры:
        "request (HttpRequest): Объект запроса.
    "user_id (int): Идентификатор пользователя, которого нужно заблокировать
                    "или разблокировать.

    Возвращает:
        HttpResponse: Перенаправляет на страницу списка пользователей после
                      изменения статуса блокировки.
    """
    user = get_object_or_404(CustomUser, id=user_id)
    user.is_blocked = not user.is_blocked
    user.save()
    return redirect("user_list")

def register_view(request):
    """
    Представление для регистрации нового пользователя.

    Этот метод обрабатывает GET- и POST-запросы для регистрации нового
    пользователя. При успешной регистрации отправляется приветственное письмо
    на указанный адрес электронной почты.

    Параметры:
        request (HttpRequest): Объект запроса.

    Возвращает
        HttpResponse: Отображает страницу с формой регистрации или
                        перенаправляет на страницу входа при успешной регистрации.
    """
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
    """
    Представление для входа пользователей.

    Обрабатывает GET и POST запросы для аутентификации пользователей по номеру
    телефона и паролю. При успешной аутентификации пользователь перенаправляется
    на домашнюю страницу, и отображается сообщение об успешном входе. Если
    аутентификация не удалась, выводится сообщение об ошибке.

    Параметры:
        request (HttpRequest): Объект запроса, содержащий информацию о текущем
                                запросе, включая данные формы.

    Возвращает:
        HttpResponse: Отображает страницу с формой входа, или перенаправляет на
                        домашнюю страницу при успешном входе.

    Примечания:
        - Доступ к этому представлению открыт для всех пользователей, включая
            неаутентифицированных.
        - Ожидается, что данные формы содержат поля "phone_number" и "password".
    """
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
    """
    Представление для редактирования профиля пользователя.

    Обрабатывает GET и POST запросы для отображения и обработки формы редактирования
    профиля текущего аутентифицированного пользователя. При успешном обновлении
    данных профиля пользователя происходит перенаправление на страницу профиля.

    Параметры:
        request (HttpRequest): Объект запроса, содержащий информацию о текущем
                                запросе, включая данные формы.

    Возвращает:
        HttpResponse: Отображает страницу с формой редактирования профиля или
                        перенаправляет на страницу профиля при успешном обновлении.

    Примечания:
        - Доступ к этому представлению открыт только для аутентифицированных
            пользователей.
        - Если метод запроса GET, отображается форма с текущими данными пользователя.
        - Если метод запроса POST, данные формы проверяются на валидность и
            сохраняются, если они корректны.
    """
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
    Представление для получения JWT токена.

    Позволяет пользователям получать токен для аутентификации с использованием
    протокола JSON Web Token (JWT). Это представление доступно как для
    аутентифицированных, так и для неаутентифицированных пользователей.

    Атрибуты:
        permission_classes (list): Список классов разрешений, определяющий доступ
            к этому представлению. В данном случае доступ открыт для всех
            пользователей.

    Методы:
        post(request): Обрабатывает POST-запрос для получения токена JWT.
    """
    permission_classes = []
