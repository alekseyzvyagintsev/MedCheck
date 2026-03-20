"""
Модуль для утилит и бизнес-логики сервисов.
"""

# Импортируем функции из основного файла utils.py
# Импортируем основные функции для удобства использования
from .appointments import (create_appointment_logic, delete_appointment_logic,
                           parse_datetime_string, render_appointment_step,
                           render_error, validate_appointment_time)
from .diagnostic_results import (create_diagnostic_result,
                                 update_diagnostic_result)

# Экспортируем все необходимые функции
__all__ = [
    "create_appointment_logic",
    "delete_appointment_logic",
    "create_diagnostic_result",
    "update_diagnostic_result",
    "parse_datetime_string",
    "validate_appointment_time",
    "render_appointment_step",
    "render_error",
]
