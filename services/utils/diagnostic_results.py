"""
Модуль для обработки результатов диагностики.
"""

from typing import Any, Dict, Optional

from django.core.files.uploadedfile import UploadedFile

from services.models import Appointment, DiagnosisResult


def create_diagnostic_result(appointment: Appointment) -> DiagnosisResult:
    """
    Создает результат диагностики при переводе приёма в статус "в работе".

    Args:
        appointment: Запись на приём

    Returns:
        Созданный результат диагностики
    """
    diagnostic_result = DiagnosisResult.objects.create(
        appointment=appointment, status="processing", description=""
    )

    return diagnostic_result


def update_diagnostic_result(
    appointment: Appointment,
    files: Optional[list] = None,
    description: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Обновляет результат диагностики при переводе приёма в статус "завершён".

    Args:
        appointment: Запись на приём
        files: Список файлов с результатами
        description: Описание результатов

    Returns:
        Словарь с результатами операции
    """
    # Получаем или создаем результат диагностики
    diagnostic_result, created = DiagnosisResult.objects.get_or_create(
        appointment=appointment, defaults={"status": "processing", "description": ""}
    )

    # Проверяем, что предоставлены файлы или описание
    if not files and not description:
        return {
            "success": False,
            "error": "Необходимо загрузить файлы с результатами или заполнить описание",
        }

    # Обновляем файлы, если они предоставлены
    if files:
        for file in files:
            if isinstance(file, UploadedFile):
                # Сохраняем файл и обновляем ссылку в diagnostic_result
                diagnostic_result.file.save(file.name, file, save=False)

    # Обновляем описание
    if description:
        diagnostic_result.description = description

    # Обновляем статус
    diagnostic_result.status = "completed"
    diagnostic_result.save()

    # Деактивируем запись на прием
    appointment.is_active = False
    appointment.save()

    return {"success": True, "diagnostic_result_id": diagnostic_result.id}
