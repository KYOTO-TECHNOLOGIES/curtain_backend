from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils import timezone

class Appointment(models.Model):
    JOB_TYPES = [
        ('measurement', 'Measurement'),
        ('installation', 'Installation'),
        ('consultation', 'Consultation'),
        ('repair', 'Repair'),
    ]
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('scheduled', 'Scheduled'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('rescheduled', 'Rescheduled'),
    ]

    id = models.CharField(max_length=20, primary_key=True)  # e.g., APT-1001
    customer = models.ForeignKey('customers.Customer', on_delete=models.CASCADE, related_name='appointments')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    appointment_date = models.DateField()
    appointment_time = models.TimeField()
    end_time = models.TimeField(null=True, blank=True, help_text="Optional duration end")
    job_type = models.CharField(max_length=20, choices=JOB_TYPES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    assigned_to = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_appointments')
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='created_appointments')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Cancellation details
    cancellation_reason = models.TextField(blank=True)
    cancelled_at = models.DateTimeField(null=True, blank=True)
    cancelled_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='cancelled_appointments')

    def clean(self):
        if self.end_time and self.end_time <= self.appointment_time:
            raise ValidationError("End time must be after start time.")

    def save(self, *args, **kwargs):
        # Auto-generate ID if not set (e.g., APT-1001)
        if not self.id:
            last = Appointment.objects.order_by('id').last()
            if last:
                num = int(last.id.split('-')[1]) + 1
            else:
                num = 1001
            self.id = f"APT-{num}"
        super().save(*args, **kwargs)

    def __str__(self):
        return self.id

    class Meta:
        db_table = 'appointments'
        ordering = ['-appointment_date', '-appointment_time']
        indexes = [
            models.Index(fields=['customer', 'status']),
            models.Index(fields=['assigned_to', 'status']),
            models.Index(fields=['appointment_date']),
        ]


class AppointmentLocation(models.Model):
    LOCATION_STATUS_CHOICES = [
        ('not_set', 'Not Set'),
        ('shared_by_customer', 'Shared by Customer'),
        ('confirmed', 'Confirmed'),
    ]

    appointment = models.OneToOneField(Appointment, on_delete=models.CASCADE, related_name='location')
    building_name = models.CharField(max_length=100, blank=True)
    unit_number = models.CharField(max_length=50, blank=True)
    full_address = models.TextField()
    coordinates = models.JSONField(null=True, blank=True, help_text="{'lat': 25.0805, 'lng': 55.1403}")
    additional_instructions = models.TextField(blank=True)
    location_status = models.CharField(max_length=30, choices=LOCATION_STATUS_CHOICES, default='not_set')

    def __str__(self):
        return f"Location for {self.appointment.id}"

    class Meta:
        db_table = 'appointment_locations'