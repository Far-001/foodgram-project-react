import csv

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from app.models import Ingredient


class Command(BaseCommand):
    """Добавление ингридиентов из csv-файла в базу данных."""
    help = 'Загрузка данных из csv-файла.'

    def handle(self, *args, **kwargs):
        try:
            with open(
                f'{settings.BASE_DIR}/data/ingredients.csv',
                'r',
                encoding='utf-8'
            ) as csv_file:
                rows = csv.reader(csv_file)
                for row in rows:
                    name, units = row
                    Ingredient.objects.get_or_create(
                        name=name,
                        units=units
                    )
        except FileNotFoundError:
            raise CommandError('Нет файла ingredients.csv в каталоге data')
