from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

from services.models import ServiceCategory, Service


class Command(BaseCommand):
    help = 'Заполняет базу данных тестовыми данными'

    def handle(self, *args, **options):
        User = get_user_model()

        # Создаем пользователей
        admin, created = User.objects.get_or_create(
            username='admin',
            defaults={'is_staff': True, 'is_superuser': True}
        )
        if created:
            admin.set_password('admin')
            admin.save()
            self.stdout.write(self.style.SUCCESS('Создан суперпользователь admin'))

        manager, created = User.objects.get_or_create(
            username='manager',
            defaults={'is_staff': True, 'is_superuser': False}
        )
        if created:
            manager.set_password('manager')
            manager.save()
            self.stdout.write(self.style.SUCCESS('Создан пользователь manager'))

        user, created = User.objects.get_or_create(
            username='user',
            defaults={'is_staff': False, 'is_superuser': False}
        )
        if created:
            user.set_password('user')
            user.save()
            self.stdout.write(self.style.SUCCESS('Создан пользователь user'))

        # Создаем категории услуг
        categories_data = [
            {
                'name': 'Терапия',
                'description': 'Основные терапевтические услуги и консультации'
            },
            {
                'name': 'Диагностика',
                'description': 'Диагностические процедуры и обследования'
            },
            {
                'name': 'Лаборатория',
                'description': 'Лабораторные анализы и исследования'
            }
        ]

        categories = []
        for cat_data in categories_data:
            category, created = ServiceCategory.objects.get_or_create(
                name=cat_data['name'],
                defaults={
                    'description': cat_data['description'],
                    'order': categories_data.index(cat_data)
                }
            )
            if created:
                self.stdout.write(f'Создана категория: {category.name}')
            categories.append(category)

        # Создаем услуги
        services_data = [
            {
                'name': 'Первичный прием терапевта',
                'category': 'Терапия',
                'description': 'Консультация терапевта для первичного осмотра и диагностики.',
                'short_description': 'Консультация терапевта для первичного осмотра.',
                'price': 2500,
                'duration': 30,
                'preparation': 'Рекомендуется прийти натощак, иметь при себе паспорт и медицинский полис.',
                'results_time': 'Результаты консультации известны сразу'
            },
            {
                'name': 'Повторный прием терапевта',
                'category': 'Терапия',
                'description': 'Повторная консультация терапевта для оценки динамики лечения.',
                'short_description': 'Повторная консультация терапевта.',
                'price': 2000,
                'duration': 20,
                'preparation': 'Иметь при себе результаты предыдущих обследований.',
                'results_time': 'Результаты консультации известны сразу'
            },
            {
                'name': 'Консультация врача-терапевта на дому',
                'category': 'Терапия',
                'description': 'Выезд терапевта на дом для консультации и осмотра.',
                'short_description': 'Выезд терапевта на дом для консультации.',
                'price': 4000,
                'duration': 45,
                'preparation': 'Обеспечить спокойную обстановку для приема, иметь при себе паспорт.',
                'results_time': 'Результаты консультации известны сразу'
            },
            {
                'name': 'Ультразвуковое исследование (УЗИ) органов брюшной полости',
                'category': 'Диагностика',
                'description': 'Ультразвуковое исследование печени, желчного пузыря, поджелудочной железы, селезенки и почек.',
                'short_description': 'УЗИ органов брюшной полости.',
                'price': 3500,
                'duration': 30,
                'preparation': 'Исследование проводится натощак (не менее 8 часов голодания).',
                'results_time': 'Результаты готовы сразу после исследования'
            },
            {
                'name': 'Рентгенография легких',
                'category': 'Диагностика',
                'description': 'Рентгеновское исследование органов грудной клетки для диагностики заболеваний легких.',
                'short_description': 'Рентген легких.',
                'price': 2800,
                'duration': 15,
                'preparation': 'Снять одежду до пояса и удалить все металлические предметы.',
                'results_time': 'Результаты готовы через 30 минут'
            },
            {
                'name': 'Электрокардиография (ЭКГ)',
                'category': 'Диагностика',
                'description': 'Регистрация электрической активности сердца для оценки его работы.',
                'short_description': 'ЭКГ сердца.',
                'price': 2200,
                'duration': 10,
                'preparation': 'Рекомендуется прийти в спокойном состоянии, избегать физических нагрузок перед исследованием.',
                'results_time': 'Результаты готовы сразу после исследования'
            },
            {
                'name': 'Общий анализ крови',
                'category': 'Лаборатория',
                'description': 'Исследование крови, включающее определение количества эритроцитов, лейкоцитов, гемоглобина и других показателей.',
                'short_description': 'Клинический анализ крови.',
                'price': 1200,
                'duration': 5,
                'preparation': 'Сдавать кровь натощак (не менее 8 часов голодания), можно пить воду.',
                'results_time': 'Результаты готовы через 1-2 дня'
            },
            {
                'name': 'Биохимический анализ крови',
                'category': 'Лаборатория',
                'description': 'Комплексное исследование крови для оценки функций различных органов и систем.',
                'short_description': 'Биохимия крови.',
                'price': 3800,
                'duration': 5,
                'preparation': 'Сдавать кровь натощак (не менее 8 часов голодания), избегать жирной пищи накануне.',
                'results_time': 'Результаты готовы через 1-2 дня'
            },
            {
                'name': 'Анализ мочи общий',
                'category': 'Лаборатория',
                'description': 'Исследование мочи для оценки функции почек и диагностики различных заболеваний.',
                'short_description': 'Общий анализ мочи.',
                'price': 800,
                'duration': 5,
                'preparation': 'Собирать утреннюю порцию мочи в чистую сухую емкость.',
                'results_time': 'Результаты готовы через 1 день'
            }
        ]

        for service_data in services_data:
            category = next((c for c in categories if c.name == service_data['category']), None)
            if category:
                service, created = Service.objects.get_or_create(
                    name=service_data['name'],
                    category=category,
                    defaults={
                        'description': service_data['description'],
                        'short_description': service_data['short_description'],
                        'price': service_data['price'],
                        'duration': service_data['duration'],
                        'preparation': service_data['preparation'],
                        'results_time': service_data['results_time'],
                        'order': services_data.index(service_data)
                    }
                )
                if created:
                    self.stdout.write(f'Создана услуга: {service.name}')

        self.stdout.write(self.style.SUCCESS('База данных успешно заполнена тестовыми данными!'))
