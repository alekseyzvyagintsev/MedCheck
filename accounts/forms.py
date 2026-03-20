from django import forms
from django.contrib.auth.forms import UserChangeForm, UserCreationForm
from django.db.models import BooleanField

from accounts.models import User
from accounts.validators import validate_extensions, validate_max_size_mb


class StileFormMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if isinstance(field, BooleanField):
                field.widget.attrs["class"] = "form-check-input"
            else:
                field.widget.attrs["class"] = "form-control"


class UserRegistrationForm(StileFormMixin, UserCreationForm):
    username = forms.CharField(
        max_length=50,
        required=True,
        widget=forms.TextInput(attrs={"placeholder": "Введите имя пользователя"}),
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={"placeholder": "Введите email"})
    )
    first_name = forms.CharField(
        max_length=50,
        required=False,
        help_text="Необязательное поле.",
        widget=forms.TextInput(attrs={"placeholder": "Введите своё имя"}),
    )
    last_name = forms.CharField(
        max_length=50,
        required=False,
        help_text="Необязательное поле.",
        widget=forms.TextInput(attrs={"placeholder": "Введите свою фамилию"}),
    )
    phone = forms.CharField(
        max_length=15,
        required=False,
        help_text="Необязательное поле. Введите ваш номер телефона.",
        widget=forms.TextInput(attrs={"placeholder": "Введите номер телефона"}),
    )
    address = forms.CharField(
        max_length=100,
        required=False,
        help_text="Необязательное поле. Введите ваш адрес.",
        widget=forms.TextInput(attrs={"placeholder": "Введите адрес"}),
    )
    date_of_birth = forms.DateField(
        required=True,
        help_text="Обязательное поле. Введите вашу дату рождения.",
        widget=forms.DateInput(
            attrs={"placeholder": "Введите дату рождения", "type": "date"}
        ),
    )
    image = forms.ImageField(
        required=False,
        help_text="Необязательное поле. Выберите файл для загрузки Вашего фото.",
    )
    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={"placeholder": "Введите пароль"})
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={"placeholder": "Подтвердите пароль"})
    )
    usable_password = None

    class Meta:
        model = User
        fields = [
            "username",
            "email",
            "first_name",
            "last_name",
            "phone",
            "image",
            "password1",
            "password2",
        ]

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
        return user

    def clean_phone(self):
        phone = self.cleaned_data.get("phone")
        if phone and not phone.isdigit():
            raise forms.ValidationError("Номер телефона должен содержать только цифры.")
        return phone

    def clean_image(self):
        """Метод очистки и проверки поля 'image'"""
        image_field = self.cleaned_data["image"]
        # пропускаем пустое поле
        if not image_field:
            return None
        # Проверяем файлы на соответствие допустимым расширениям
        valid_extensions = ["jpeg", "png", "webp"]
        validate_extensions(valid_extensions, image_field)
        # Проверяем, что размер файла не превышает допустимый размер
        max_size_mb = 5
        validate_max_size_mb(max_size_mb, image_field)

        return image_field


class UserProfileForm(StileFormMixin, UserChangeForm):
    password = None  # Чтобы убрать пароль из формы редактирования

    username = forms.CharField(
        max_length=50,
        required=True,
        widget=forms.TextInput(attrs={"placeholder": "Введите имя пользователя"}),
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={"placeholder": "Введите email"})
    )
    first_name = forms.CharField(
        max_length=50,
        required=False,
        help_text="Необязательное поле.",
        widget=forms.TextInput(attrs={"placeholder": "Введите своё имя"}),
    )
    last_name = forms.CharField(
        max_length=50,
        required=False,
        help_text="Необязательное поле.",
        widget=forms.TextInput(attrs={"placeholder": "Введите свою фамилию"}),
    )
    phone = forms.CharField(
        max_length=15,
        required=False,
        help_text="Необязательное поле. Введите ваш номер телефона.",
        widget=forms.TextInput(attrs={"placeholder": "Введите номер телефона"}),
    )
    address = forms.CharField(
        max_length=100,
        required=False,
        help_text="Необязательное поле. Введите ваш адрес.",
        widget=forms.TextInput(attrs={"placeholder": "Введите адрес"}),
    )
    date_of_birth = forms.DateField(
        required=True,
        help_text="Обязательное поле. Введите вашу дату рождения.",
        widget=forms.DateInput(
            attrs={"placeholder": "Введите дату рождения", "type": "date"}
        ),
    )
    image = forms.ImageField(
        required=False,
        help_text="Необязательное поле. Выберите файл для загрузки Вашего фото.",
    )

    class Meta:
        model = User
        fields = ("username", "email", "first_name", "last_name", "phone", "image")

    def clean_phone(self):
        phone = self.cleaned_data.get("phone")
        if phone and not phone.isdigit():
            raise forms.ValidationError("Номер телефона должен содержать только цифры.")
        return phone

    def clean_image(self):
        """Метод очистки и проверки поля 'image'"""
        image_field = self.cleaned_data["image"]
        # пропускаем пустое поле
        if not image_field:
            return None
        # Проверяем файлы на соответствие допустимым расширениям
        valid_extensions = ["jpeg", "png"]
        validate_extensions(valid_extensions, image_field)
        # Проверяем, что размер файла не превышает допустимый размер
        max_size_mb = 5
        validate_max_size_mb(max_size_mb, image_field)

        return image_field


# class CustomAuthenticationForm(StileFormMixin, AuthenticationForm):
#     username = forms.CharField(
#         widget=forms.TextInput(attrs={'placeholder': 'Введите имя пользователя'})
#     )
#     password = forms.CharField(
#         widget=forms.PasswordInput(attrs={'placeholder': 'Введите пароль'})
#     )
#
#     class Meta:
#         model = User
#         fields = ('username', 'password')
