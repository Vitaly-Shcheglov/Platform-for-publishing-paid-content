from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.shortcuts import render, get_object_or_404, redirect
from .forms import PostForm, SubscriptionForm
from django.urls import reverse_lazy
from .models import Post, Category, Subcategory
from django.http import HttpResponse, HttpResponseForbidden
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin, UserPassesTestMixin
from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from .services import PostService
from users.models import CustomUser
from django.views.generic import ListView
from django.db import connection
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from .models import Subscription
from .serializers import SubscriptionSerializer
from drf_yasg.utils import swagger_auto_schema
from django.shortcuts import render, get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from drf_yasg.utils import swagger_auto_schema
from .models import Subscription
from .serializers import SubscriptionSerializer
from .forms import PostForm, SubscriptionForm


class HomeView(ListView):
    model = Post
    template_name = "posts/home.html"
    context_object_name = "posts"
    paginate_by = 5

    def get_queryset(self):
        return Post.objects.filter(is_published=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        with connection.cursor() as cursor:
            cursor.execute("SELECT category, subcategory FROM categories")
            categories = cursor.fetchall()

        category_dict = {}
        for category, subcategory in categories:
            if category not in category_dict:
                category_dict[category] = []
            category_dict[category].append(subcategory)

        context['categories'] = category_dict

        return context


class ContactView(View):
    def get(self, request):
        return render(request, "posts/contacts.html")

    def post(self, request):
        name = request.POST.get("name")
        phone = request.POST.get("phone")
        message = request.POST.get("message")

        if name and phone and message:
            return HttpResponse(f"Спасибо, {name}! Ваше сообщение получено.")
        else:
            return HttpResponse("Пожалуйста, заполните все поля!", status=400)


@method_decorator(cache_page(60 * 15), name="dispatch")
class PostDetailView(LoginRequiredMixin, DetailView):
    model = Post
    form_class = PostForm
    template_name = "posts/post_detail.html"
    context_object_name = "post"


class AddPostView(CreateView):
    model = Post
    form_class = PostForm
    template_name = "posts/add_post.html"
    success_url = reverse_lazy("post_list")

    def form_valid(self, form):
        if self.request.user.is_authenticated:
            form.instance.author = self.request.user
            form.instance.is_paid = form.cleaned_data.get('is_paid', False)
        else:
            form.instance.is_paid = False

        form.instance.subcategory = form.cleaned_data.get('subcategory')

        return super().form_valid(form)


class PostListView(ListView):
    model = Post
    form_class = PostForm
    template_name = "posts/post_list.html"
    context_object_name = "posts"

    def get_queryset(self):
        return Post.objects.all()


class PostUpdateView(LoginRequiredMixin, UpdateView):
    model = Post
    form_class = PostForm
    template_name = "posts/post_form.html"
    success_url = reverse_lazy("post_list")

    def test_func(self):
        post = self.get_object()
        return (
            self.request.user == post.owner
            or self.request.user.groups.filter(name="Post moderator group").exists()
        )


class PostDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = Post
    template_name = "posts/post_confirm_delete.html"
    success_url = reverse_lazy("post_list")
    permission_required = "posts.can_delete_post"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["post"] = self.object
        return context

    def test_func(self):
        product = self.get_object()
        return (
            self.request.user == product.owner
            or self.request.user.groups.filter(name="Post moderator group").exists()
        )


class PublishPostView(View):
    def post(self, request, pk):
        product = get_object_or_404(Post, pk=pk, owner=request.user)
        product.is_published = True
        product.save()
        return redirect("product_list")


class UnpublishPostView(LoginRequiredMixin, UserPassesTestMixin, View):
    permission_required = "catalog.can_unpublish_post"

    def post(self, request, pk):
        post = get_object_or_404(Post, pk=pk)

        if request.user == post.owner or request.user.groups.filter(name="Post moderator group").exists():
            product.is_published = False
            product.save()
            return redirect("post_list")
        else:
            return HttpResponseForbidden("У вас нет прав для отмены публикации этой записи.")

    def test_func(self):
        post = get_object_or_404(Post, pk=self.kwargs["pk"])
        return (
            self.request.user == post.owner
            or self.request.user.groups.filter(name="Product moderator group").exists()
        )


class PostsInCategoryView(ListView):
    model = Post
    template_name = "posts/poss_in_category.html"
    context_object_name = "posts"

    def get_queryset(self):
        """Возвращает список всех записей в указанной категории."""
        category_pk = self.kwargs["pk"]
        return PostService.get_posts_by_category(category_pk)

    def get_context_data(self, **kwargs):
        """Добавляет объект категории в контекст."""
        context = super().get_context_data(**kwargs)
        category_pk = self.kwargs["pk"]
        context["category"] = get_object_or_404(Category, pk=category_pk)
        return context


@login_required
def create_post(request):
    if request.method == "POST":
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect('home')
    else:
        form = PostForm()
    return render(request, 'posts/create_post.html', {'form': form})

class PostsFreeListView(ListView):
    model = Post
    template_name = "posts/posts_free.html"
    context_object_name = "posts_free"

    def get_queryset(self):
        return Post.objects.filter(is_paid=False)


class PostsPaidListView(LoginRequiredMixin, ListView):
    model = Post
    template_name = "posts/posts_paid.html"
    context_object_name = "posts"

    def get_queryset(self):
        return Post.objects.filter(is_paid=True)


class CategoryListView(LoginRequiredMixin, ListView):
    model = Category
    template_name = 'categories/category_list.html'
    context_object_name = 'categories'

    def get_queryset(self):
        """Возвращает только корневые категории."""
        return Category.objects.filter(parent=None)

    def get_context_data(self, **kwargs):
        """Добавляет информацию о пользователе в контекст."""
        context = super().get_context_data(**kwargs)
        user = self.request.user

        if isinstance(user, CustomUser):
            context['user'] = user
            context['has_paid_subscription'] = user.has_paid_subscription

        return context


class GetSubcategoriesView(View):
    def get(self, request, *args, **kwargs):
        category_id = request.GET.get('category')
        subcategories = Subcategory.objects.filter(category_id=category_id).values('id', 'name')
        return JsonResponse(list(subcategories), safe=False)


class SubscriptionView(APIView):
    """
    View для создания и получения подписок пользователя.
    """

    @method_decorator(csrf_exempt)
    @swagger_auto_schema(
        request_body=SubscriptionSerializer,
        responses={201: 'Подписка создана', 400: 'Ошибка валидации'}
    )
    def post(self, request):
        """Создает новую подписку."""
        data = request.data.copy()
        data['user'] = request.user.id
        serializer = SubscriptionSerializer(data=data)

        if serializer.is_valid():
            subscription = serializer.save()
            return Response({'status': 'subscribed', 'subscription_id': subscription.id}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        responses={200: SubscriptionSerializer(many=False)}
    )
    def get(self, request):
        """Возвращает информацию о текущей подписке пользователя."""
        subscription = get_object_or_404(Subscription, user=request.user)
        serializer = SubscriptionSerializer(subscription)
        return Response(serializer.data)

    def get_template(self, request):
        """Возвращает шаблон для управления подписками."""
        return render(request, 'subscription.html')


@login_required
def subscription_view(request):
    if request.method == "POST":
        form = SubscriptionForm(request.POST)
        if form.is_valid():
            subscription_data = form.cleaned_data

            subscription, created = Subscription.objects.get_or_create(
                user=request.user,
                defaults={
                    'plan': subscription_data['plan'],
                    'end_date': subscription_data['end_date'],
                    'is_active': True
                }
            )

            if not created:
                subscription.plan = subscription_data['plan']
                subscription.end_date = subscription_data['end_date']
                subscription.is_active = True
                subscription.save()

            return redirect("subscription_success")
    else:
        form = SubscriptionForm()

    return render(request, "posts/subscription.html", {"form": form})

def subscription_success_view(request):
    """Страница успеха после подписки."""
    return render(request, "subscription_success.html")
