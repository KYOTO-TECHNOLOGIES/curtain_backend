from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models
from users.models import BaseModel


class Supplier(BaseModel):
    name = models.CharField(max_length=255)
    contact_person = models.CharField(max_length=150, blank=True)
    phone = models.CharField(max_length=30, blank=True)
    email = models.EmailField(blank=True)
    address = models.TextField(blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        db_table = 'inventory_suppliers'
        ordering = ['name']

    def __str__(self):
        return self.name


class InventoryItem(BaseModel):
    CATEGORY_CHOICES = [
        ('fabric', 'Fabric'),
        ('track', 'Track'),
        ('motor', 'Motor'),
        ('accessory', 'Accessory'),
        ('other', 'Other'),
    ]
    UNIT_CHOICES = [
        ('roll', 'Roll'),
        ('m', 'Metre'),
        ('m2', 'Square Metre'),
        ('pcs', 'Pieces'),
        ('box', 'Box'),
        ('set', 'Set'),
    ]

    sku = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=255)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='fabric')
    unit = models.CharField(max_length=10, choices=UNIT_CHOICES, default='pcs')
    quantity_on_hand = models.DecimalField(
        max_digits=12, decimal_places=2, default=0, validators=[MinValueValidator(0)]
    )
    reorder_level = models.DecimalField(
        max_digits=12, decimal_places=2, default=0, validators=[MinValueValidator(0)]
    )
    reorder_quantity = models.DecimalField(
        max_digits=12, decimal_places=2, default=0, validators=[MinValueValidator(0)]
    )
    unit_cost = models.DecimalField(
        max_digits=12, decimal_places=2, default=0, validators=[MinValueValidator(0)]
    )
    location = models.CharField(max_length=100, blank=True)
    supplier = models.ForeignKey(
        Supplier,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='items',
    )
    catalog_item = models.ForeignKey(
        'catalog.CatalogItem',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='inventory_items',
    )
    notes = models.TextField(blank=True)

    class Meta:
        db_table = 'inventory_items'
        ordering = ['name', 'sku']

    def __str__(self):
        return f"{self.sku} — {self.name}"

    @property
    def is_low_stock(self):
        return self.quantity_on_hand <= self.reorder_level


class StockMovement(BaseModel):
    MOVEMENT_CHOICES = [
        ('in', 'Stock In'),
        ('out', 'Stock Out'),
        ('adjust', 'Adjustment'),
    ]

    item = models.ForeignKey(InventoryItem, on_delete=models.CASCADE, related_name='movements')
    movement_type = models.CharField(max_length=10, choices=MOVEMENT_CHOICES)
    quantity = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(0.01)])
    reference = models.CharField(max_length=100, blank=True)
    notes = models.TextField(blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='stock_movements',
    )

    class Meta:
        db_table = 'inventory_stock_movements'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.movement_type} {self.quantity} — {self.item.sku}"


class ReorderRequest(BaseModel):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('ordered', 'Ordered'),
        ('received', 'Received'),
        ('cancelled', 'Cancelled'),
    ]

    item = models.ForeignKey(InventoryItem, on_delete=models.CASCADE, related_name='reorders')
    supplier = models.ForeignKey(
        Supplier,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reorders',
    )
    quantity = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(0.01)])
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    notes = models.TextField(blank=True)
    ordered_at = models.DateTimeField(null=True, blank=True)
    received_at = models.DateTimeField(null=True, blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reorder_requests',
    )

    class Meta:
        db_table = 'inventory_reorder_requests'
        ordering = ['-created_at']

    def __str__(self):
        return f"Reorder {self.item.sku} x {self.quantity} ({self.status})"
