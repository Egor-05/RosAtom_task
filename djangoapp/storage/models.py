from django.core.exceptions import ValidationError
from django.db import models


TYPES_OF_NODES = [
    ('operator', 'Оператор'),
    ('storage', 'Хранилище')
]


class Node(models.Model):
    name = models.CharField(max_length=50, unique=True)
    type = models.CharField(max_length=50, choices=TYPES_OF_NODES)
    glass_total_capacity = models.FloatField()
    glass_current_occupancy = models.FloatField(default=0)
    plastic_total_capacity = models.FloatField()
    plastic_current_occupancy = models.FloatField(default=0)
    biowastes_total_capacity = models.FloatField()
    biowastes_current_occupancy = models.FloatField(default=0)

    def clean(self):
        super().clean()
        if self.glass_current_occupancy > self.glass_total_capacity:
             raise ValidationError('Значение количества отходов не может превышать максимальную вместимость')
        if self.plastic_current_occupancy > self.plastic_total_capacity:
            raise ValidationError('Значение количества отходов не может превышать максимальную вместимость')
        if self.biowastes_current_occupancy > self.biowastes_total_capacity:
             raise ValidationError('Значение количества отходов не может превышать максимальную вместимость')

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

class Connection(models.Model):
    node_from = models.ForeignKey(Node, on_delete=models.CASCADE, related_name='node_from')
    node_to = models.ForeignKey(Node, on_delete=models.CASCADE, related_name='node_to')
    distance = models.FloatField()