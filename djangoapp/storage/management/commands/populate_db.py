from django.core.management.base import BaseCommand
from django.core.exceptions import ValidationError
from django.db import transaction, IntegrityError
from django.contrib.auth.models import User

from storage.models import Node, Connection

class Command(BaseCommand):
    help = 'The Zen of Python'

    def handle(self, *args, **options):
        try:
            user = User.objects.create_superuser("root", 'admin@123.ru', 'qwerty')
        except IntegrityError:
            pass
        try:
            with transaction.atomic():
                operator1 = Node.objects.create(
                    name='operator1',
                    type='operator',
                    glass_total_capacity=50,
                    plastic_total_capacity=50,
                    biowastes_total_capacity=50,
                )

                operator2 = Node.objects.create(
                    name='operator2',
                    type='operator',
                    glass_total_capacity=100,
                    plastic_total_capacity=100,
                    biowastes_total_capacity=100,
                )

                storage1_1 = Node.objects.create(
                    name='storage1_1',
                    type='storage',
                    glass_total_capacity=20,
                    plastic_total_capacity=20,
                    biowastes_total_capacity=20,
                )

                storage1_2 = Node.objects.create(
                    name='storage1_2',
                    type='storage',
                    glass_total_capacity=20,
                    plastic_total_capacity=20,
                    biowastes_total_capacity=20,
                )

                storage1_3 = Node.objects.create(
                    name='storage1_3',
                    type='storage',
                    glass_total_capacity=15,
                    plastic_total_capacity=15,
                    biowastes_total_capacity=15,
                )

                storage2_1 = Node.objects.create(
                    name='storage2_1',
                    type='storage',
                    glass_total_capacity=20,
                    plastic_total_capacity=20,
                    biowastes_total_capacity=20,
                )

                storage2_2 = Node.objects.create(
                    name='storage2_2',
                    type='storage',
                    glass_total_capacity=20,
                    plastic_total_capacity=20,
                    biowastes_total_capacity=20,
                )

                storage2_3 = Node.objects.create(
                    name='storage2_3',
                    type='storage',
                    glass_total_capacity=15,
                    plastic_total_capacity=15,
                    biowastes_total_capacity=15,
                )

                Connection.objects.create(node_from=operator1, node_to=storage1_1, distance=100)
                Connection.objects.create(node_from=storage1_1, node_to=storage1_2, distance=200)
                Connection.objects.create(node_from=storage1_1, node_to=storage1_3, distance=100)

                Connection.objects.create(node_from=operator2, node_to=storage2_1, distance=100)
                Connection.objects.create(node_from=storage2_1, node_to=storage2_2, distance=200)
                Connection.objects.create(node_from=storage2_1, node_to=storage2_3, distance=100)

                operator1.glass_current_occupancy += 50
                operator1.plastic_current_occupancy += 50
                operator1.biowastes_current_occupancy += 50
                operator1.save()
        except ValidationError:
            print('Пожалуйста, очистите базу данных, перед тем, как загружать в нее информацию с помощью этой команды.')
