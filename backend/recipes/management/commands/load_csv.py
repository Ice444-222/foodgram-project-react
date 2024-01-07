import csv

from django.core.management.base import BaseCommand

from recipes.models import Ingredient

PATH = 'data/'


class Command(BaseCommand):
    help = 'Импортирование данных из CSV файла'

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str, help='Путь к CSV файлу')

    def handle(self, *args, **options):
        csv_file_path = options['csv_file']

        with open(csv_file_path, 'r', encoding='utf-8') as file:
            reader = csv.reader(file)
            for row in reader:
                name = row[0]
                measurement_unit = row[1]

                Ingredient.objects.create(
                    name=name,
                    measurement_unit=measurement_unit,
                )

        self.stdout.write(self.style.SUCCESS('Данные импортированы!'))
