from rest_framework import serializers

from .models import CustomUser


class UserRegistrationSerializer(serializers.ModelSerializer):
    """
    Сериализатор для регистрации нового пользователя.

    Этот сериализатор позволяет пользователю вводить данные для создания нового аккаунта,
    включая номер телефона, адрес электронной почты и пароль. Он также выполняет валидацию
    данных и создает нового пользователя.

    Атрибуты:
        password (CharField): Поле для ввода пароля, скрытое от глаз пользователя.
    """

    password = serializers.CharField(write_only=True)

    class Meta:
        model = CustomUser
        fields = ["phone_number", "email", "password", "avatar", "country"]

    def create(self, validated_data):
        """
        Создает нового пользователя на основе валидированных данных.

        Этот метод переопределяет стандартный метод создания для сериализатора и
        устанавливает зашифрованный пароль для нового пользователя.

        Args:
            validated_data (dict): Валидированные данные, полученные из формы.
                Содержит поля, необходимые для создания пользователя.

        Returns:
            CustomUser: Созданный объект пользователя.
        """
        user = CustomUser(
            phone_number=validated_data["phone_number"],
            email=validated_data["email"],
            avatar=validated_data.get("avatar"),
            country=validated_data.get("country"),
        )
        user.set_password(validated_data["password"])
        user.save()
        return user

    def validate(self, data):
        """
        Проверяет валидность данных перед созданием пользователя.

        Этот метод проверяет, существует ли уже пользователь с данным номером телефона
        или адресом электронной почты, и вызывает ошибку валидации, если это так.

        Args:
            data (dict): Данные, полученные из формы.

        Returns:
            dict: Валидированные данные.

        Raises:
            serializers.ValidationError: Если номер телефона или адрес электронной почты уже зарегистрированы.
        """
        if CustomUser.objects.filter(phone_number=data["phone_number"]).exists():
            raise serializers.ValidationError({"phone_number": "Этот номер телефона уже зарегистрирован."})
        if CustomUser.objects.filter(email=data["email"]).exists():
            raise serializers.ValidationError({"email": "Этот email уже зарегистрирован."})

        return data


class UserProfileSerializer(serializers.ModelSerializer):
    """
    Сериализатор для представления и валидации данных профиля пользователя.

    Этот сериализатор используется для преобразования данных профиля пользователя
    в формат, подходящий для передачи через API, и для валидации входящих данных
    при обновлении профиля пользователя.

    Атрибуты:
        avatar (ImageField): Поле для загрузки изображения аватара пользователя.
        phone_number (CharField): Поле для ввода номера телефона пользователя.
        country (CharField): Поле для указания страны пользователя.

    Мета-класс:
        Meta: В этом классе определяются модель и поля, которые будут сериализованы.
    """

    class Meta:
        model = CustomUser
        fields = ["avatar", "phone_number", "country"]

    def update(self, instance, validated_data):
        """
        Обновляет экземпляр пользователя с переданными данными.

        Этот метод обновляет только те поля, которые были переданы в validated_data.

        Параметры:
            instance (CustomUser): Экземпляр пользователя, который будет обновлен.
            validated_data (dict): Словарь с данными для обновления.

        Returns:
            CustomUser: Обновленный экземпляр пользователя.
        """
        for field, value in validated_data.items():
            setattr(instance, field, value)
        instance.save()
        return instance
