import csv

from django.apps import apps  # Replace with your actual model
from django.core.management.base import BaseCommand

from recipes.models import Ingredient

PATH = 'data/'

class Command(BaseCommand):
    help = 'Populate the database with data from a CSV file'

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str, help='Path to the CSV file')

    def handle(self, *args, **options):
        csv_file_path = options['csv_file']

        with open(csv_file_path, 'r', encoding='utf-8') as file:
            reader = csv.reader(file)
            for row in reader:
                name = row[0]
                measurement_unit = row[1]

                # Create Ingredient object
                Ingredient.objects.create(
                    name=name,
                    measurement_unit=measurement_unit,
                )

        self.stdout.write(self.style.SUCCESS('Data imported successfully!'))
