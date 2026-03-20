from django import forms
from django.forms import Select

from .models import DiagnosisResult


class DiagnosisResultForm(forms.ModelForm):
    """
    Форма для создания и редактирования результатов диагностики
    """

    class Meta:
        model = DiagnosisResult
        fields = ["file", "description", "status"]
        widgets = {
            "description": forms.Textarea(
                attrs={
                    "rows": 4,
                    "class": "form-control",
                    "placeholder": "Введите описание результатов диагностики...",
                }
            ),
            "status": Select(
                choices=[
                    ("processing", "В обработке"),
                    ("completed", "Готово"),
                    ("failed", "Ошибка"),
                ],
                attrs={"class": "form-control"},
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["file"].widget.attrs.update({"class": "form-control-file"})
