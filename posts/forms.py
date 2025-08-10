from django import forms
from .models import Post, Category, Subcategory, Subscription
from django.core.exceptions import ValidationError

FORBIDDEN_WORDS = [
    "Деньги", "легкие деньги", "заработок", "быстрый заработок", "миллионы",
    "ставки", "казино", "выигрыш", "купить", "продажа", "бесплатно", "акция",
    "скидка", "дешево", "низкие цены", "быстрый доход", "гарантированный доход",
    "заработать за день", "выйти из бедности", "богатство", "финансовая свобода",
    "удвоить доход", "sale", "Гарантия", "100% результат", "никаких усилий",
    "легко", "без вложений", "хайп", "вирусный", "кеш", "накрутка", "лайки",
    "подписки", "за подписку", "подпишись", "репостни", "пиши комментарий",
    "розыгрыш", "разыгрываю", "марафон", "лотерея", "колесо фортуны", "приз",
    "выиграй", "взаимные лайки", "комментарии", "пиар", "единственный",
    "похудение", "диета", "лечение", "секс", "эротика", "голый", "насилие",
    "суицид", "абьюз", "убийство", "убить", "избить", "аборт", "терроризм",
    "алкоголь", "алкоголизм", "взрыв", "бомба", "разбомбить", "обман", "фейк",
    "хакер", "кража", "украсть", "негр", "гей", "лесбиянка", "магия", "шок",
    "не поверите!", "срочно", "немедленно"
]


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'content', 'category', 'subcategory', 'is_paid', 'image']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 10}),
        }

    def clean_name(self):
        name = self.cleaned_data["name"]
        if any(word in name.lower() for word in FORBIDDEN_WORDS):
            raise ValidationError("Название записи содержит запрещенные слова.")
        return name

    def clean_description(self):
        description = self.cleaned_data["description"]
        if any(word in description.lower() for word in FORBIDDEN_WORDS):
            raise ValidationError("Запись содержит запрещенные слова.")
        return description

    def __init__(self, *args, **kwargs):
        super(PostForm, self).__init__(*args, **kwargs)
        self.fields['category'].queryset = Category.objects.all()
        self.fields['subcategory'].queryset = Subcategory.objects.none()

        if 'category' in self.data:
            try:
                category_id = int(self.data.get('category'))
                self.fields['subcategory'].queryset = Subcategory.objects.filter(parent_id=category_id).order_by('name')
            except (ValueError, TypeError):
                pass
        elif self.instance.pk:
            self.fields['subcategory'].queryset = self.instance.category.subcategories.order_by('name')


class SubscriptionForm(forms.ModelForm):
    class Meta:
        model = Subscription
        fields = ['plan', 'end_date']
