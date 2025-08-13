from django import forms

from .models import CustomUser


class UserRegistrationForm(forms.ModelForm):
    """
    Форма для регистрации нового пользователя.

    Эта форма позволяет пользователю вводить данные для создания нового аккаунта.
    Включает поле для ввода пароля с использованием защищенного поля ввода.

    Атрибуты:
        password (CharField): Поле для ввода пароля, скрытое от глаз пользователя.
    """

    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = CustomUser
        fields = ["phone_number", "password", "avatar", "email", "country"]

    def save(self, commit=True):
        """
        Сохраняет нового пользователя с установленным паролем.

        Этот метод переопределяет стандартный метод сохранения, чтобы установить
        пароль пользователя в зашифрованном виде.

        Args:
            commit (bool): Указывает, следует ли немедленно сохранять пользователя в базе данных.
                            По умолчанию True.

        Returns:
            CustomUser: Объект пользователя, который был создан или обновлен.
        """
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user


class UserProfileForm(forms.ModelForm):
    """
    Форма для редактирования профиля пользователя.

    Эта форма позволяет пользователям обновлять свои данные профиля,
    такие как аватар, номер телефона и страну.

    Атрибуты:
        None
    """

    class Meta:
        model = CustomUser
        fields = ["avatar", "phone_number", "country"]
