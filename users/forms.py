from django import forms

from .models import CustomUser


class UserRegistrationForm(forms.ModelForm):
    """
    Форма для регистрации нового пользователя.

    Эта форма позволяет пользователю вводить данные для создания нового аккаунта.
    Включает поле для ввода пароля с использованием защищенного поля ввода.

    Атрибуты:
        password1 (CharField): Поле для ввода пароля.
        password2 (CharField): Поле для подтверждения пароля.

    Метаданные:
        Meta: Определяет модель и поля, которые будут использоваться в форме.
    """

    password1 = forms.CharField(
        label="Пароль",
        widget=forms.PasswordInput,
        help_text="Введите пароль, который будет использоваться для вашей учетной записи."
    )
    password2 = forms.CharField(
        label="Подтверждение пароля",
        widget=forms.PasswordInput,
        help_text="Введите тот же пароль еще раз для подтверждения."
    )

    class Meta:
        model = CustomUser
        fields = ('phone_number', 'avatar')

    def clean_password2(self):
        """
        Проверяет, чтобы введенные пароли совпадали.

        Если пароли не совпадают, вызывается ошибка валидации.

        Returns:
            str: Второй введенный пароль, если он совпадает с первым.

        Raises:
            ValidationError: Если пароли не совпадают.
        """
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Пароли не совпадают.")
        return password2

    def clean_phone_number(self):
        """
        Проверяет, существует ли пользователь с таким номером телефона.

        Если номер телефона уже используется, вызывается ошибка валидации.

        Returns:
            str: Номер телефона, введенный пользователем.

        Raises:
            ValidationError: Если номер телефона уже существует в базе данных.
        """
        phone = self.cleaned_data.get('phone_number')
        if CustomUser.objects.filter(phone_number=phone).exists():
            raise forms.ValidationError("Пользователь с таким номером телефона уже существует.")
        return phone

    def save(self, commit=True):
        """
        Сохраняет новый объект пользователя.

        Устанавливает пароль для пользователя, если он был введен.

        Параметры:
            commit (bool): Если True, сохраняет объект в базе данных. По умолчанию True.

        Returns:
            CustomUser: Созданный объект пользователя.
        """
        user = super().save(commit=False)
        password = self.cleaned_data.get('password1')
        if password:
            user.set_password(password)
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
        fields = ["avatar", "phone_number"]
