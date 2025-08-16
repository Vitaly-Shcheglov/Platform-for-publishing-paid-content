from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin, UserPassesTestMixin
from django.db import connection
from django.http import HttpResponse, HttpResponseForbidden, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.cache import cache_page
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from users.models import CustomUser

from .forms import PostForm, SubscriptionForm
from .models import Category, Post, Subcategory, Subscription
from .serializers import SubscriptionSerializer
from .services import PostService


class HomeView(ListView):
    """
    View для отображения главной страницы с публикациями.

    Этот класс отображает список всех опубликованных постов,
    поддерживает пагинацию и предоставляет список категорий для фильтрации.

    Атрибуты:
        model (Model): Модель, с которой работает данный view (Post).
        template_name (str): Шаблон, используемый для рендеринга страницы.
        context_object_name (str): Имя контекста, под которым будут доступны посты в шаблоне.
        paginate_by (int): Количество постов на странице.
    """

    model = Post
    template_name = "posts/home.html"
    context_object_name = "posts"
    paginate_by = 5

    def get_queryset(self):
        """
        Возвращает отфильтрованный список опубликованных постов.

        Returns:
            QuerySet: Список опубликованных постов.
        """
        return Post.objects.filter(is_published=True)

    def get_context_data(self, **kwargs):
        """
        Добавляет дополнительные данные в контекст, передаваемый в шаблон.

        Args:
            **kwargs: Дополнительные параметры, переданные в метод.

        Returns:
            dict: Обновленный контекст с добавленными категориями.
        """
        context = super().get_context_data(**kwargs)

        with connection.cursor() as cursor:
            cursor.execute("SELECT category, subcategory FROM categories")
            categories = cursor.fetchall()

        category_dict = {}
        for category, subcategory in categories:
            if category not in category_dict:
                category_dict[category] = []
            category_dict[category].append(subcategory)

        context["categories"] = category_dict

        return context


class ContactView(View):
    """
    View для обработки контактной формы.

    Этот класс обрабатывает GET и POST запросы на страницу контактов.
    Позволяет пользователю отправлять сообщения через форму обратной связи.
    """

    def get(self, request):
        """
        Обрабатывает GET-запрос.

        Возвращает страницу контактов.

        Args:
            request (HttpRequest): Объект запроса.

        Returns:
            HttpResponse: Ответ с отображением страницы контактов.
        """
        return render(request, "posts/contacts.html")

    def post(self, request):
        """
        Обрабатывает POST-запрос.

        Получает данные из формы и отправляет ответ пользователю.

        Args:
            request (HttpRequest): Объект запроса с данными формы.

        Returns:
            HttpResponse: Ответ с сообщением о получении сообщения или об ошибке.
        """
        name = request.POST.get("name")
        phone = request.POST.get("phone")
        message = request.POST.get("message")

        if name and phone and message:
            return HttpResponse(f"Спасибо, {name}! Ваше сообщение получено.")
        else:
            return HttpResponse("Пожалуйста, заполните все поля!", status=400)


class PostDetailView(LoginRequiredMixin, DetailView):
    """
    View для отображения деталей поста.

    Этот класс отображает информацию о конкретном посте и требует,
    чтобы пользователь был авторизован.

    Атрибуты:
        model (Model): Модель, с которой работает данный view (Post).
        form_class (ModelForm): Форма, используемая для редактирования поста.
        template_name (str): Шаблон, используемый для рендеринга страницы.
        context_object_name (str): Имя контекста, под которым будет доступен пост в шаблоне.
    """

    model = Post
    form_class = PostForm
    template_name = "posts/posts_detail.html"
    context_object_name = "post"

    def get_queryset(self):
        post_pk = self.kwargs["pk"]
        return Post.objects.filter(id=post_pk)


class AddPostView(CreateView):
    """
    View для добавления нового поста.

    Этот класс позволяет пользователю добавлять новый пост с указанием всех необходимых
    атрибутов и автоматически связывает пост с авторизованным пользователем.

    Атрибуты:
        model (Model): Модель, с которой работает данный view (Post).
        form_class (ModelForm): Форма, используемая для создания поста.
        template_name (str): Шаблон, используемый для рендеринга страницы добавления поста.
        success_url (str): URL, на который будет перенаправлен пользователь после успешного создания поста.
    """

    model = Post
    form_class = PostForm
    template_name = "posts/add_post.html"
    success_url = reverse_lazy("post_list")

    def form_valid(self, form):
        """
        Обрабатывает валидную форму и связывает пост с текущим авторизованным пользователем.

        Args:
            form (ModelForm): Объект формы, содержащий данные для создания поста.

        Returns:
            Response: Ответ с перенаправлением на success_url после успешного создания поста.
        """
        if self.request.user.is_authenticated:
            form.instance.owner = self.request.user
            form.instance.is_paid = form.cleaned_data.get("is_paid", False)
        else:
            form.instance.is_paid = False

        form.instance.subcategory = form.cleaned_data.get("subcategory")

        return super().form_valid(form)


class PostListView(ListView):
    """
    View для отображения списка всех постов.

    Этот класс предоставляет API для получения списка всех постов.
    Позволяет пользователям просматривать все посты, которые могут быть
    опубликованы или неопубликованы.

    Атрибуты:
        model (Model): Модель, с которой работает данный view (Post).
        template_name (str): Шаблон, используемый для отображения списка постов.
        context_object_name (str): Имя контекста, под которым будут доступны посты в шаблоне.
    """

    model = Post
    form_class = PostForm
    template_name = "posts/post_list.html"
    context_object_name = "posts"

    def get_queryset(self):
        """
        Возвращает список всех постов.

        Returns:
            QuerySet: Список всех объектов модели Post.
        """
        return Post.objects.all()


class PostUpdateView(LoginRequiredMixin, UpdateView):
    """
    View для обновления информации о посте.

    Этот класс позволяет авторизованным пользователям обновлять существующие посты.

    Атрибуты:
        model (Model): Модель, с которой работает данный view (Post).
        form_class (ModelForm): Форма, используемая для редактирования поста.
        template_name (str): Шаблон, используемый для отображения формы редактирования поста.
        success_url (str): URL, на который будет перенаправлен пользователь после успешного обновления поста.
    """

    model = Post
    form_class = PostForm
    template_name = "posts/posts_form.html"
    success_url = reverse_lazy("post_list")

    def test_func(self):
        """
        Проверяет, имеет ли пользователь право обновить пост.

        Returns:
            bool: True, если пользователь является владельцем поста
                         или состоит в группе модераторов постов; иначе False.
        """
        post = self.get_object()
        return (
            self.request.user == post.owner
            or self.request.user.groups.filter(name="Post moderator group").exists()
        )


class PostDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    """
    View для удаления поста.

    Этот класс позволяет авторизованным пользователям удалять свои посты.

    Атрибуты:
        model (Model): Модель, с которой работает данный view (Post).
        template_name (str): Шаблон, используемый для отображения подтверждения удаления.
        success_url (str): URL, на который будет перенаправлен пользователь после успешного удаления поста.
        permission_required (str): Права, необходимые для удаления постов.
    """

    model = Post
    template_name = "posts/post_confirm_delete.html"
    success_url = reverse_lazy("post_list")
    permission_required = "posts.can_delete_post"

    def get_context_data(self, **kwargs):
        """
        Добавляет объект поста в контекст.

        Args:
            **kwargs: Дополнительные параметры, переданные в метод.

        Returns:
            dict: Обновленный контекст с объектом поста.
        """
        context = super().get_context_data(**kwargs)
        context["post"] = self.object
        return context

    def test_func(self):
        """
        Проверяет, имеет ли пользователь право удалить пост.

        Returns:
            bool: True, если пользователь является владельцем поста
                    или состоит в группе модераторов постов; иначе False.
        """
        product = self.get_object()
        return (
            self.request.user == product.owner or self.request.user.groups.filter(name="Post moderator group").exists()
        )


class PublishPostView(View):
    """
    View для публикации поста.

    Этот класс позволяет пользователю опубликовать свой пост, если он является его владельцем.
    """

    def post(self, request, pk):
        """
        Обрабатывает публикацию поста.

        Args:
            request (HttpRequest): Объект запроса, содержащий данные для публикации.
            pk (int): Идентификатор поста, который необходимо опубликовать.

        Returns:
            HttpResponse: Ответ с перенаправлением на список постов после успешной публикации.
        """
        post = get_object_or_404(Post, pk=pk, owner=request.user)
        post.is_published = True
        post.save()
        return redirect("post_list")


class UnpublishPostView(LoginRequiredMixin, UserPassesTestMixin, View):
    """
    View для отмены публикации поста.

    Этот класс позволяет пользователям отменить публикацию своих постов,
    если они являются владельцами этих постов или модераторами.
    """

    permission_required = "posts.can_unpublish_post"

    def post(self, request, pk):
        """
        Обрабатывает отмену публикации поста.

        Args:
            request (HttpRequest): Объект запроса, содержащий данные для отмены публикации.
            pk (int): Идентификатор поста, который необходимо сделать непубликуемым.

        Returns:
            HttpResponse: Ответ с перенаправлением на список постов после успешной отмены публикации.
        """
        post = get_object_or_404(Post, pk=pk)

        if request.user == post.owner or request.user.groups.filter(name="Post moderator group").exists():
            post.is_published = False
            post.save()
            return redirect("post_list")
        else:
            return HttpResponseForbidden("У вас нет прав для отмены публикации этой записи.")

    def test_func(self):
        """
        Проверяет, имеет ли пользователь право отменить публикацию поста.

        Returns:
            bool: True, если пользователь является владельцем поста
                    или состоит в группе модераторов постов; иначе False.
        """
        post = get_object_or_404(Post, pk=self.kwargs["pk"])
        return (
            self.request.user == post.owner
            or self.request.user.groups.filter(name="Post moderator group").exists()
        )


class PostsInCategoryView(ListView):
    """
    View для отображения постов в указанной категории.

    Этот класс предоставляет API для получения списка всех публикаций,
    относящихся к заданной категории.

    Атрибуты:
        model (Model): Модель, с которой работает данный view (Post).
        template_name (str): Шаблон, используемый для отображения постов.
        context_object_name (str): Имя контекста, под которым будут доступны посты в шаблоне.
    """

    model = Post
    template_name = "posts/poss_in_category.html"
    context_object_name = "posts"

    def get_queryset(self):
        """
        Возвращает список всех записей в указанной категории.

        Использует PostService для получения постов из кэшированной категории.

        Returns:
            QuerySet: Список объектов модели Post, относящихся к указанной категории.
        """
        """Возвращает список всех записей в указанной категории."""
        category_pk = self.kwargs["pk"]
        return PostService.get_posts_by_category(category_pk)

    def get_context_data(self, **kwargs):
        """
         Добавляет объект категории в контекст.

        Args:
            **kwargs: Дополнительные параметры, переданные в метод.

        Returns:
            dict: Обновленный контекст с добавленной категорией.
        """
        """Добавляет объект категории в контекст."""
        context = super().get_context_data(**kwargs)
        category_pk = self.kwargs["pk"]
        context["category"] = get_object_or_404(Category, pk=category_pk)
        return context


class PostsFreeListView(ListView):
    """
    View для отображения бесплатных постов.

    Этот класс предоставляет API для получения списка всех бесплатных постов
    (постов, которые не требуют оплаты для доступа).

    Атрибуты:
        model (Model): Модель, с которой работает данный view (Post).
        template_name (str): Шаблон, используемый для отображения бесплатных постов.
        context_object_name (str): Имя контекста, под которым будут доступны бесплатные посты в шаблоне.
    """

    model = Post
    template_name = "posts/posts_free.html"
    context_object_name = "posts_free"

    def get_queryset(self):
        """
        Возвращает список всех бесплатных постов.

        Returns:
            QuerySet: Список объектов модели Post, которые имеют is_paid=False.
        """
        return Post.objects.filter(is_paid=False)


class PostsPaidListView(LoginRequiredMixin, ListView):
    """
    View для отображения платных постов.

    Этот класс предоставляет API для получения списка всех платных постов
    (постов, которые требуют оплаты для доступа).

    Атрибуты:
        model (Model): Модель, с которой работает данный view (Post).
        template_name (str): Шаблон, используемый для отображения платных постов.
        context_object_name (str): Имя контекста, под которым будут доступны платные посты в шаблоне.
    """

    model = Post
    template_name = "posts/posts_paid.html"
    context_object_name = "posts"

    def get_queryset(self):
        """
        Возвращает список всех платных постов.

        Returns:
            QuerySet: Список объектов модели Post, которые имеют is_paid=True.
        """
        return Post.objects.filter(is_paid=True)


class CategoryListView(LoginRequiredMixin, ListView):
    """
    View для отображения списка категорий.

    Этот класс предоставляет API для получения списка всех корневых категорий,
    доступных только для авторизованных пользователей.

    Атрибуты:
        model (Model): Модель, с которой работает данный view (Category).
        template_name (str): Шаблон, используемый для отображения списка категорий.
        context_object_name (str): Имя контекста, под которым будут доступны категории в шаблоне.
    """

    model = Category
    template_name = "categories/category_list.html"
    context_object_name = "categories"

    def get_queryset(self):
        """
        Возвращает только корневые категории.

        Returns:
            QuerySet: Список корневых объектов модели Category, которые не имеют родителя.
        """
        return Category.objects.filter(parent=None)

    def get_context_data(self, **kwargs):
        """
        Добавляет информацию о пользователе в контекст.

        Args:
            **kwargs: Дополнительные параметры, переданные в метод.

        Returns:
            dict: Обновленный контекст с информацией о пользователе.
        """
        context = super().get_context_data(**kwargs)
        user = self.request.user

        if isinstance(user, CustomUser):
            context["user"] = user
            context["has_paid_subscription"] = user.has_paid_subscription

        return context


class GetSubcategoriesView(View):
    """
    View для получения подкатегорий на основе выбранной категории.

    Этот класс обрабатывает GET-запросы, чтобы вернуть список подкатегорий,
    относящихся к указанной категории.

    Атрибуты:
        None
    """

    def get(self, request, *args, **kwargs):
        """
        Обрабатывает GET-запрос для получения подкатегорий.

        Args:
            request (HttpRequest): Объект запроса.

        Returns:
            JsonResponse: Ответ с информацией о подкатегориях в формате JSON.
        """
        category_id = request.GET.get("category")
        subcategories = Subcategory.objects.filter(category_id=category_id).values("id", "name")
        return JsonResponse(list(subcategories), safe=False)


class SubscriptionView(APIView):
    """
    View для создания и получения подписок пользователя.

    Этот класс предоставляет API для управления подписками пользователей, включая
    создание новой подписки и получение информации о текущей подписке.
    """

    @method_decorator(csrf_exempt)
    @swagger_auto_schema(
        request_body=SubscriptionSerializer, responses={201: "Подписка создана", 400: "Ошибка валидации"}
    )
    def post(self, request):
        """
        Создает новую подписку.

        Args:
            request (Request): Объект запроса с данными о подписке.

        Returns:
            Response: Ответ с информацией о созданной подписке или ошибках валидации.
        """
        data = request.data.copy()
        data["user"] = request.user.id
        serializer = SubscriptionSerializer(data=data)

        if serializer.is_valid():
            subscription = serializer.save()
            return Response(
                {"status": "subscribed", "subscription_id": subscription.id}, status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(responses={200: SubscriptionSerializer(many=False)})
    def get(self, request):
        """
        Возвращает информацию о текущей подписке пользователя.

        Args:
            request (Request): Объект запроса.

        Returns:
            Response: Ответ с данными о текущей подписке пользователя.
        """
        subscription = get_object_or_404(Subscription, user=request.user)
        serializer = SubscriptionSerializer(subscription)
        return Response(serializer.data)

    def get_template(self, request):
        """
        Возвращает шаблон для управления подписками.

        Args:
            request (HttpRequest): Объект запроса.

        Returns:
            HttpResponse: Ответ с рендером шаблона для управления подписками.
        """
        return render(request, "subscription.html")


@login_required
def subscription_view(request):
    """
    Обрабатывает создание и обновление подписки через форму.

    Этот view позволяет пользователям создать новую подписку или
    обновить существующую.

    Args:
        request (HttpRequest): Объект запроса.

    Returns:
        HttpResponse: Ответ с рендером шаблона для создания подписки или перенаправление
                        на страницу успеха после успешного создания подписки.
    """
    if request.method == "POST":
        form = SubscriptionForm(request.POST)
        if form.is_valid():
            subscription_data = form.cleaned_data

            subscription, created = Subscription.objects.get_or_create(
                user=request.user,
                defaults={
                    "plan": subscription_data["plan"],
                    "end_date": subscription_data["end_date"],
                    "is_active": True,
                },
            )

            if not created:
                subscription.plan = subscription_data["plan"]
                subscription.end_date = subscription_data["end_date"]
                subscription.is_active = True
                subscription.save()

            return redirect("subscription_success")
    else:
        form = SubscriptionForm()

    return render(request, "posts/subscription.html", {"form": form})


def subscription_success_view(request):
    """
    Страница успеха после подписки.

    Этот view отображает страницу успеха, на которую пользователь
    попадает после успешного создания подписки.

    Args:
        request (HttpRequest): Объект запроса.

    Returns:
        HttpResponse: Ответ с рендером шаблона успеха подписки.
    """
    return render(request, "subscription_success.html")


def category_detail_view(request, category_id):
    """
    Представление для отображения деталей категории.

    Это представление обрабатывает GET-запросы для получения информации о категории
    и ее подкатегориях. Если идентификатор категории не существует, будет возвращена
    страница 404.

    Args:
        request (HttpRequest): Объект запроса, содержащий информацию о текущем запросе.
        category_id (int): Идентификатор категории, для которой нужно отобразить детали.

    Returns:
        HttpResponse:
            Если категория найдена, возвращает страницу с деталями категории и подкатегорий.
            Если категория не найдена, возвращает страницу 404 (Not Found).

    Примечания:
        - В случае успешного получения категории, также будет доступна информация о родительской категории.
        - В шаблоне отображаются название категории, ее описание и список подкатегорий.
    """
    category = get_object_or_404(Category, id=category_id)

    parent_category = category.parent

    context = {
        'category': category,
        'parent_category': parent_category,
    }

    return render(request, 'category_detail.html', context)


def subcategory_detail_view(request, subcategory_id):
    """
    Представление для отображения деталей подкатегории.

    Args:
        request (HttpRequest): Объект запроса.
        subcategory_id (int): Идентификатор подкатегории.

    Returns:
        HttpResponse: Страница с деталями подкатегории.
    """
    subcategory = get_object_or_404(Subcategory, id=subcategory_id)

    context = {
        'subcategory': subcategory,
    }

    return render(request, 'subcategory_detail.html', context)


@login_required
def update_post_status(request, post_id):
    """
    Обновляет статус 'Платная запись' для поста.

    Это представление обрабатывает POST-запросы для обновления статуса платной записи
    конкретного поста. Если запрос является GET, оно возвращает форму редактирования
    поста с текущими данными.

    Args:
        request (HttpRequest): Объект запроса, содержащий данные о текущем запросе.
        post_id (int): Идентификатор поста, для которого нужно обновить статус.

    Returns:
        HttpResponse:
            - Перенаправление на страницу платных публикаций при успешном обновлении статуса.
            - Отображение формы редактирования поста в случае GET-запроса, если пользователь
              имеет доступ к этому представлению.

    Примечания:
        - Доступ к этому представлению ограничен аутентифицированными пользователями,
          поскольку используется декоратор @login_required.
        - Статус 'Платная запись' обновляется на основе значения, полученного из формы,
          где пользователю предлагается выбрать, является ли запись платной или нет.
        - В случае успешного обновления данных, пользователь будет перенаправлен на
          страницу платных публикаций.
    """
    post = get_object_or_404(Post, id=post_id)

    if request.method == "POST":
        is_paid = request.POST.get("is_paid") == "True"
        post.is_paid = is_paid
        post.save()
        return redirect('posts_paid')

    return render(request, 'posts/posts_form.html', {'post': post})
