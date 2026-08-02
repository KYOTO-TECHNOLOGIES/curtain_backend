from django.db import models
from django.core.validators import MinValueValidator

class WorkType(models.Model):
    PRICING_UNIT_CHOICES = [
        ('m2', 'Square Metre (m²)'),
        ('m', 'Running Metre (m)'),
    ]
    name = models.CharField(max_length=50, unique=True)
    pricing_unit = models.CharField(max_length=2, choices=PRICING_UNIT_CHOICES, default='m2')
    features = models.JSONField(default=dict, blank=True,
                                help_text="e.g., {'motor': true, 'charges': true, 'images': true, 'draw': false, 'pelmet': true}")

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'catalog_work_types'
        ordering = ['name']


class FabricType(models.Model):
    work_type = models.ForeignKey(WorkType, on_delete=models.CASCADE, related_name='fabric_types')
    name = models.CharField(max_length=50)

    class Meta:
        db_table = 'catalog_fabric_types'
        unique_together = [['work_type', 'name']]

    def __str__(self):
        return f"{self.work_type.name} - {self.name}"


class Model(models.Model):
    fabric_type = models.ForeignKey(FabricType, on_delete=models.CASCADE, related_name='models')
    name = models.CharField(max_length=50)

    class Meta:
        db_table = 'catalog_models'
        unique_together = [['fabric_type', 'name']]

    def __str__(self):
        return f"{self.fabric_type.name} - {self.name}"


class CatalogItem(models.Model):
    model = models.ForeignKey(Model, on_delete=models.CASCADE, related_name='items')
    name = models.CharField(max_length=50)
    price_per_unit = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    image = models.ImageField(upload_to='catalog_items/', blank=True, null=True)

    class Meta:
        db_table = 'catalog_items'
        unique_together = [['model', 'name']]

    def __str__(self):
        return f"{self.model.name} - {self.name}"


class MotorType(models.Model):
    name = models.CharField(max_length=100, unique=True)
    price_per_m2 = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'catalog_motor_types'


class ChargeTemplate(models.Model):
    """Global charges like manual control, motorized control, Alexa, pelmet."""
    name = models.CharField(max_length=100, unique=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    unit = models.CharField(max_length=20, default='flat', help_text="flat, /m², /m")

    def __str__(self):
        return f"{self.name} ({self.price})"

    class Meta:
        db_table = 'catalog_charges'