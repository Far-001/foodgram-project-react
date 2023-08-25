import csv

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from recipes.models import Ingredient


class Command(BaseCommand):
    """Добавление ингридиентов из csv-файла в базу данных."""
    help = 'Загрузка данных из csv-файла.'

    def handle(self, *args, **kwargs):
        try:
            with open(
                f'{settings.BASE_DIR}/../data/ingredients.csv',
                'r',
                encoding='utf-8'
            ) as csv_file:
                rows = csv.reader(csv_file)
                for row in rows:
                    name, measurement_unit = row
                    Ingredient.objects.get_or_create(
                        name=name,
                        measurement_unit=measurement_unit
                    )
        except FileNotFoundError:
            raise CommandError('Нет файла ingredients.csv в каталоге data')
