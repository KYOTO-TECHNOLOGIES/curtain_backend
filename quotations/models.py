from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal


class Quotation(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('pending', 'Pending'),
        ('sent', 'Sent'),
        ('accepted', 'Accepted'),
        ('cancelled', 'Cancelled'),
    ]
    QUOTE_TYPE_CHOICES = [
        ('b2c', 'B2C (Retail)'),
        ('b2b', 'B2B (Trade)'),
    ]

    id = models.CharField(max_length=20, primary_key=True)
    customer = models.ForeignKey('customers.Customer', on_delete=models.CASCADE, related_name='quotations')
    appointment = models.ForeignKey('appointments.Appointment', on_delete=models.SET_NULL, null=True, related_name='quotations')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    quote_type = models.CharField(max_length=10, choices=QUOTE_TYPE_CHOICES, default='b2c')
    work_type = models.ForeignKey('catalog.WorkType', on_delete=models.PROTECT, related_name='quotations')

    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0'))
    vat = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0'))
    total = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0'))
    discount_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('0'), validators=[MinValueValidator(0), MaxValueValidator(100)])
    discount_amount = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0'))

    valid_until = models.DateField()
    issued_date = models.DateField(auto_now_add=True)
    sent_date = models.DateTimeField(null=True, blank=True)
    sent_via = models.CharField(max_length=20, choices=[('email', 'Email'), ('whatsapp', 'WhatsApp'), ('sms', 'SMS')], blank=True)

    prepared_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='quotations_prepared')
    accepted_date = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.id:
            last = Quotation.objects.order_by('id').last()
            if last:
                num = int(last.id.split('-')[1]) + 1
            else:
                num = 90214
            self.id = f"QT-{num}"
        super().save(*args, **kwargs)

    def recalc_totals(self):
        """Calculate subtotal, vat, discount, total from children"""
        total_raw = Decimal('0')
        for area in self.areas.all():
            for surface in area.surfaces.all():
                if hasattr(surface, 'spec'):
                    total_raw += surface.spec.line_item_total or Decimal('0')
        
        self.subtotal = total_raw
        self.discount_amount = (self.subtotal * self.discount_percentage) / Decimal('100')
        net = self.subtotal - self.discount_amount
        self.vat = net * Decimal('0.05')
        self.total = net + self.vat
        self.save(update_fields=['subtotal', 'discount_amount', 'vat', 'total'])

    def __str__(self):
        return self.id

    class Meta:
        db_table = 'quotations'
        ordering = ['-issued_date']


class QuotationArea(models.Model):
    quotation = models.ForeignKey(Quotation, on_delete=models.CASCADE, related_name='areas')
    area_type = models.CharField(max_length=100)
    display_name = models.CharField(max_length=200)
    sort_order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        db_table = 'quotation_areas'
        ordering = ['sort_order']

    def __str__(self):
        return self.display_name


class QuotationSurface(models.Model):
    SURFACE_TYPE_CHOICES = [
        ('window_curtain_path', 'Window (Curtain Path)'),
        ('wall_to_wall_track', 'Wall-to-Wall Track'),
        ('bay_window', 'Bay Window'),
        ('sliding_door', 'Sliding Door'),
    ]
    OPENING_DIRECTION_CHOICES = [
        ('one_way', 'One Way'),
        ('two_way', 'Two Way'),
    ]

    area = models.ForeignKey(QuotationArea, on_delete=models.CASCADE, related_name='surfaces')
    surface_name = models.CharField(max_length=100, default='Surface 01')
    surface_type = models.CharField(max_length=30, choices=SURFACE_TYPE_CHOICES)
    width_cm = models.DecimalField(max_digits=8, decimal_places=2, validators=[MinValueValidator(0)])
    height_cm = models.DecimalField(max_digits=8, decimal_places=2, validators=[MinValueValidator(0)])
    calculated_area_m2 = models.DecimalField(max_digits=10, decimal_places=4, default=Decimal('0'), editable=False)
    opening_direction = models.CharField(max_length=20, choices=OPENING_DIRECTION_CHOICES, default='one_way')
    special_requirements = models.TextField(blank=True)
    sort_order = models.PositiveSmallIntegerField(default=0)

    def save(self, *args, **kwargs):
        work_type = self.area.quotation.work_type
        width = Decimal(str(self.width_cm or 0))
        height = Decimal(str(self.height_cm or 0))
        
        if work_type.pricing_unit == 'm':
            self.calculated_area_m2 = width / Decimal('100')
        else:
            self.calculated_area_m2 = (width / Decimal('100')) * (height / Decimal('100'))
        super().save(*args, **kwargs)

    class Meta:
        db_table = 'quotation_surfaces'
        ordering = ['sort_order']

    def __str__(self):
        return f"{self.area.display_name} - {self.surface_name}"


class SurfaceSpec(models.Model):
    surface = models.OneToOneField(QuotationSurface, on_delete=models.CASCADE, related_name='spec')

    # Fabric/Item details
    fabric_type = models.ForeignKey('catalog.FabricType', on_delete=models.PROTECT, null=True, blank=True)
    model = models.ForeignKey('catalog.Model', on_delete=models.PROTECT, null=True, blank=True)
    catalog_item = models.ForeignKey('catalog.CatalogItem', on_delete=models.PROTECT, null=True, blank=True)
    fabric_code = models.CharField(max_length=200, blank=True)
    unit_price_per_m2 = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0'), validators=[MinValueValidator(0)])
    fabric_total = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0'))

    # Motorization
    motor_control_type = models.CharField(max_length=20, choices=[('manual', 'Manual'), ('motorized', 'Motorized')], default='manual')
    motor_type = models.ForeignKey('catalog.MotorType', on_delete=models.PROTECT, null=True, blank=True)
    motor_price_per_unit = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0'))
    motor_charge_total = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0'))

    # Manual control charge
    manual_control_total = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0'))

    # Smart/Alexa
    smart_integration = models.BooleanField(default=False)
    alexa_quantity = models.PositiveIntegerField(default=0)
    alexa_unit_price = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0'))
    alexa_total = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0'))

    # Pelmet
    pelmet_enabled = models.BooleanField(default=False)
    pelmet_width_cm = models.DecimalField(max_digits=8, decimal_places=2, default=Decimal('0'))
    pelmet_price_per_metre = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0'))
    pelmet_total = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0'))

    # Add-on custom charge
    addon_label = models.CharField(max_length=100, blank=True)
    addon_amount = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0'))

    # Line item total (calculated)
    line_item_total = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0'))

    def save(self, *args, **kwargs):
        """Calculate totals before saving"""
        surface = self.surface
        area = surface.calculated_area_m2 or Decimal('0')
        
        # Ensure all values are Decimal
        unit_price = Decimal(str(self.unit_price_per_m2 or 0))
        motor_price = Decimal(str(self.motor_price_per_unit or 0))
        manual_control = Decimal(str(self.manual_control_total or 0))
        alexa_unit = Decimal(str(self.alexa_unit_price or 0))
        alexa_qty = Decimal(str(self.alexa_quantity or 0))
        pelmet_price = Decimal(str(self.pelmet_price_per_metre or 0))
        pelmet_width = Decimal(str(self.pelmet_width_cm or 0))
        addon = Decimal(str(self.addon_amount or 0))
        
        # Fabric total
        self.fabric_total = area * unit_price
        
        # Motor charges
        if self.motor_control_type == 'motorized' and self.motor_type:
            self.motor_price_per_unit = Decimal(str(self.motor_type.price_per_m2))
            self.motor_charge_total = area * self.motor_price_per_unit
        else:
            self.motor_charge_total = Decimal('0')
        
        # Manual control total
        if self.motor_control_type == 'manual':
            # Keep existing value or set to 0
            self.manual_control_total = manual_control
        else:
            self.manual_control_total = Decimal('0')
        
        # Alexa total
        self.alexa_total = alexa_qty * alexa_unit
        
        # Pelmet total
        if self.pelmet_enabled and pelmet_width > 0:
            self.pelmet_total = (pelmet_width / Decimal('100')) * pelmet_price
        else:
            self.pelmet_total = Decimal('0')
        
        # Add-on amount
        self.addon_amount = addon
        
        # Line item total
        self.line_item_total = (
            self.fabric_total + 
            self.motor_charge_total + 
            self.manual_control_total +
            self.alexa_total + 
            self.pelmet_total + 
            self.addon_amount
        )
        
        super().save(*args, **kwargs)

    class Meta:
        db_table = 'surface_specs'