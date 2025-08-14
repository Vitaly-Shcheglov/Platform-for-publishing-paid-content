from django import forms
from django.core.exceptions import ValidationError

from .models import Category, Post, Subcategory, Subscription

FORBIDDEN_WORDS = [
    "Деньги",
    "легкие деньги",
    "заработок",
    "быстрый заработок",
    "миллионы",
    "ставки",
    "казино",
    "выигрыш",
    "купить",
    "продажа",
    "бесплатно",
    "акция",
    "скидка",
    "дешево",
    "низкие цены",
    "быстрый доход",
    "гарантированный доход",
    "заработать за день",
    "выйти из бедности",
    "богатство",
    "финансовая свобода",
    "удвоить доход",
    "sale",
    "Гарантия",
    "100% результат",
    "никаких усилий",
    "легко",
    "без вложений",
    "хайп",
    "вирусный",
    "кеш",
    "накрутка",
    "лайки",
    "подписки",
    "за подписку",
    "подпишись",
    "репостни",
    "пиши комментарий",
    "розыгрыш",
    "разыгрываю",
    "марафон",
    "лотерея",
    "колесо фортуны",
    "приз",
    "выиграй",
    "взаимные лайки",
    "комментарии",
    "пиар",
    "единственный",
    "похудение",
    "диета",
    "лечение",
    "секс",
    "эротика",
    "голый",
    "насилие",
    "суицид",
    "абьюз",
    "убийство",
    "убить",
    "избить",
    "аборт",
    "терроризм",
    "алкоголь",
    "алкоголизм",
    "взрыв",
    "бомба",
    "разбомбить",
    "обман",
    "фейк",
    "хакер",
    "кража",
    "украсть",
    "негр",
    "гей",
    "лесбиянка",
    "магия",
    "шок",
    "не поверите!",
    "срочно",
    "немедленно",
]


class PostForm(forms.ModelForm):
    """
    Форма для создания и редактирования постов.

    Позволяет пользователям вводить данные для создания или редактирования поста,
    включая заголовок, содержание, категорию, подкатегорию и изображение.
    Также выполняет валидацию данных.

    Атрибуты:
        Meta (class): Внутренний класс, который определяет модель и поля формы.
    """

    class Meta:
        model = Post
        fields = ["title", "content", "category", "subcategory", "is_paid", "image"]
        widgets = {
            'title': forms.TextInput(attrs={'id': 'id_title'}),
            'content': forms.Textarea(attrs={'id': 'id_content'}),
            'image': forms.FileInput(attrs={'id': 'id_image'}),
        }

    def clean_title(self):
        """
        Проверяет заголовок поста на наличие запрещенных слов.

        Args:
            None

        Returns:
            str: Проверенный заголовок, если он валиден.

        Raises:
            ValidationError: Если заголовок содержит запрещенные слова.
        """
        title = self.cleaned_data["title"]
        if any(word in title.lower() for word in FORBIDDEN_WORDS):
            raise ValidationError("Название записи содержит запрещенные слова.")
        return title

    def clean_content(self):
        """
        Проверяет содержание поста на наличие запрещенных слов.

        Args:
            None

        Returns:
            str: Проверенное содержание, если оно валидно.

        Raises:
            ValidationError: Если содержание содержит запрещенные слова.
        """
        content = self.cleaned_data["content"]
        if any(word in content.lower() for word in FORBIDDEN_WORDS):
            raise ValidationError("Запись содержит запрещенные слова.")
        return content

    def __init__(self, *args, **kwargs):
        """
        Инициализирует форму и настраивает доступные подкатегории в зависимости от выбранной категории.

        Args:
            *args: Позиционные аргументы.
            **kwargs: Именованные аргументы.

        Returns:
            None
        """
        super(PostForm, self).__init__(*args, **kwargs)
        self.fields["category"].queryset = Category.objects.all()
        self.fields["subcategory"].queryset = Subcategory.objects.none()

        if "category" in self.data:
            try:
                category_id = int(self.data.get("category"))
                self.fields["subcategory"].queryset = Subcategory.objects.filter(category_id=category_id).order_by(
                    "name"
                )
            except (ValueError, TypeError):
                pass
        elif self.instance.pk:
            self.fields["subcategory"].queryset = self.instance.category.subcategories.order_by("name")


class SubscriptionForm(forms.ModelForm):
    """
    Форма для создания и редактирования подписок.

    Позволяет пользователям вводить данные для создания или редактирования подписки,
    включая план и дату окончания подписки.

    Атрибуты:
        Meta (class): Внутренний класс, который определяет модель и поля формы.
    """

    class Meta:
        model = Subscription
        fields = ["plan", "end_date"]
