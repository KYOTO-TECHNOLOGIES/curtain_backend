from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator
from decimal import Decimal

class Order(models.Model):
    STATUS_CHOICES = [
        ('pending_production', 'Pending Production'),
        ('in_production', 'In Production'),
        ('shipped', 'Shipped'),
        ('installed', 'Installed'),
        ('closed', 'Closed'),
    ]
    quotation = models.OneToOneField('quotations.Quotation', on_delete=models.CASCADE, related_name='order')
    customer = models.ForeignKey('customers.Customer', on_delete=models.CASCADE, related_name='orders')
    order_status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='pending_production')
    estimated_production_days = models.PositiveIntegerField(default=21)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Order for {self.quotation.id}"

    class Meta:
        db_table = 'orders'


class Invoice(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('sent', 'Sent'),
        ('overdue', 'Overdue'),
        ('paid', 'Paid'),
        ('partially_paid', 'Partially Paid'),
    ]
    id = models.CharField(max_length=20, primary_key=True)  # INV-2041
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='invoice')
    customer = models.ForeignKey('customers.Customer', on_delete=models.CASCADE, related_name='invoices')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(0)])
    amount_paid = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    due_date = models.DateField()
    issued_date = models.DateField(auto_now_add=True)
    payment_terms = models.CharField(max_length=255, blank=True)
    payment_url = models.URLField(blank=True, help_text="Link to payment gateway")
    sent_date = models.DateTimeField(null=True, blank=True)
    sent_via = models.CharField(max_length=20, choices=[('email', 'Email'), ('whatsapp', 'WhatsApp')], blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    @property
    def balance_due(self):
        """Calculate balance due"""
        return Decimal(str(self.total_amount)) - Decimal(str(self.amount_paid))


    def save(self, *args, **kwargs):
        if not self.id:
            last = Invoice.objects.order_by('id').last()
            if last:
                num = int(last.id.split('-')[1]) + 1
            else:
                num = 2041
            self.id = f"INV-{num}"
        super().save(*args, **kwargs)

    def __str__(self):
        return self.id

    class Meta:
        db_table = 'invoices'
        ordering = ['-issued_date']


class Payment(models.Model):
    METHOD_CHOICES = [
        ('cash', 'Cash'),
        ('card', 'Card'),
        ('bank_transfer', 'Bank Transfer'),
        ('cheque', 'Cheque'),
    ]
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(0)])
    method = models.CharField(max_length=20, choices=METHOD_CHOICES)
    reference = models.CharField(max_length=100, blank=True, help_text="Bank ref, cheque number, etc.")
    payment_date = models.DateField()
    notes = models.TextField(blank=True)

    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='payments_created')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.invoice.id} - {self.amount}"

    class Meta:
        db_table = 'payments'
        ordering = ['-payment_date']

    def save(self, *args, **kwargs):
        """Save payment and update invoice amount_paid"""
        super().save(*args, **kwargs)
        
        # Update invoice amount_paid
        if self.invoice:
            from django.db.models import Sum
            total_paid = self.invoice.payments.aggregate(total=Sum('amount'))['total'] or Decimal('0')
            self.invoice.amount_paid = Decimal(str(total_paid))
            
            # Update invoice status based on payments
            if total_paid >= self.invoice.total_amount:
                self.invoice.status = 'paid'
            elif total_paid > 0:
                self.invoice.status = 'partially_paid'
            else:
                self.invoice.status = 'sent'
            
            self.invoice.save(update_fields=['amount_paid', 'status'])