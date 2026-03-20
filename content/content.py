from content.models import Fragment

"""
Модуль для передачи контента на все страницы проекта
"""


def get_common_context() -> dict[str, Fragment]:
    """
    Возвращает общий контекст для всех вьюх
    """
    content = Fragment.objects.all()
    fragments_dict = {f.id: f for f in content}
    return {
        "description": fragments_dict.get(1),
        "useful_info": fragments_dict.get(2),
        "address": fragments_dict.get(3),
        "phones": fragments_dict.get(4),
        "email": fragments_dict.get(5),
        "opening": fragments_dict.get(6),
        "payment": fragments_dict.get(7),
        "basement_label": fragments_dict.get(8),
        "description_big": fragments_dict.get(9),
        "patient_care": fragments_dict.get(10),
        "professionalism": fragments_dict.get(11),
        "accuracy": fragments_dict.get(12),
        "chief_medic": fragments_dict.get(13),
        "senior_nurse": fragments_dict.get(14),
        "chief_surgery": fragments_dict.get(15),
    }
