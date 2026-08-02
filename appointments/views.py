from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db import transaction
from django.utils import timezone
from .models import Appointment, AppointmentLocation
from customers.models import Customer
from .serializers import (
    AppointmentListSerializer,
    AppointmentDetailSerializer,
    AppointmentCreateUpdateSerializer,
    AppointmentStatusUpdateSerializer,
    AppointmentAssignSerializer
)


class AppointmentViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = Appointment.objects.select_related('customer', 'assigned_to', 'created_by').all()
    
    def get_serializer_class(self):
        if self.action == 'list':
            return AppointmentListSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return AppointmentCreateUpdateSerializer
        else:
            return AppointmentDetailSerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        if self.request.user.role and self.request.user.role.name == 'Salesman':
            queryset = queryset.filter(assigned_to=self.request.user)
        
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        assigned_to = self.request.query_params.get('assigned_to')
        if assigned_to:
            queryset = queryset.filter(assigned_to_id=assigned_to)
        
        date_from = self.request.query_params.get('date_from')
        if date_from:
            queryset = queryset.filter(appointment_date__gte=date_from)
        date_to = self.request.query_params.get('date_to')
        if date_to:
            queryset = queryset.filter(appointment_date__lte=date_to)
        
        customer = self.request.query_params.get('customer')
        if customer:
            queryset = queryset.filter(customer_id=customer)
        
        return queryset.order_by('appointment_date', 'appointment_time')
    
    @transaction.atomic
    def perform_create(self, serializer):
        data = self.request.data
        
        customer = None
        customer_phone = data.get('customer_phone')
        customer_email = data.get('customer_email')
        
        if customer_phone:
            customer = Customer.objects.filter(phone=customer_phone).first()
        
        if not customer and customer_email:
            customer = Customer.objects.filter(email__iexact=customer_email).first()
        
        if not customer:
            customer = Customer.objects.create(
                first_name=data.get('customer_first_name', ''),
                last_name=data.get('customer_last_name', ''),
                phone=customer_phone or '',
                email=customer_email or '',
                address_line_1=data.get('customer_address', ''),
                city=data.get('customer_city', ''),
                country=data.get('customer_country', 'UAE'),
                notes=data.get('customer_notes', ''),
                created_by=self.request.user
            )
        
        appointment = serializer.save(
            customer=customer,
            created_by=self.request.user
        )
        
        location_data = {
            'appointment': appointment,
            'building_name': data.get('location_building', ''),
            'unit_number': data.get('location_unit', ''),
            'full_address': data.get('location_full_address', ''),
            'coordinates': data.get('location_coordinates'),
            'additional_instructions': data.get('location_instructions', ''),
            'location_status': data.get('location_status', 'not_set')
        }
        AppointmentLocation.objects.create(**location_data)
        
        return appointment
        
    def perform_update(self, serializer):
        """Custom update logic"""
        appointment = serializer.save()
        # Handle location update if provided
        data = self.request.data
        if hasattr(appointment, 'location'):
            location = appointment.location
            if 'location_building' in data:
                location.building_name = data.get('location_building', location.building_name)
            if 'location_unit' in data:
                location.unit_number = data.get('location_unit', location.unit_number)
            if 'location_full_address' in data:
                location.full_address = data.get('location_full_address', location.full_address)
            if 'location_coordinates' in data:
                location.coordinates = data.get('location_coordinates', location.coordinates)
            if 'location_instructions' in data:
                location.additional_instructions = data.get('location_instructions', location.additional_instructions)
            location.save()    
    @action(detail=True, methods=['patch'], url_path='status')
    def update_status(self, request, pk=None):
        appointment = self.get_object()
        
        if request.user.role and request.user.role.name == 'Salesman' and appointment.assigned_to != request.user:
            return Response({
                'error': 'You can only update status for appointments assigned to you.'
            }, status=status.HTTP_403_FORBIDDEN)
        
        serializer = AppointmentStatusUpdateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        data = serializer.validated_data
        new_status = data['status']
        
        if new_status == 'cancelled':
            appointment.cancellation_reason = data.get('cancellation_reason', 'No reason provided')
            appointment.cancelled_at = timezone.now()
            appointment.cancelled_by = request.user
        else:
            appointment.cancellation_reason = ''
            appointment.cancelled_at = None
            appointment.cancelled_by = None
        
        appointment.status = new_status
        appointment.save()
        
        detail_serializer = AppointmentDetailSerializer(appointment)
        return Response(detail_serializer.data)
    
    @action(detail=True, methods=['patch'], url_path='assign')
    def assign_salesman(self, request, pk=None):
        appointment = self.get_object()
        serializer = AppointmentAssignSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        appointment.assigned_to = serializer.validated_data['assigned_to']
        appointment.save()
        
        detail_serializer = AppointmentDetailSerializer(appointment)
        return Response(detail_serializer.data)
    
    @action(detail=False, methods=['get'], url_path='my')
    def my_appointments(self, request):
        queryset = Appointment.objects.filter(assigned_to=request.user).order_by('appointment_date', 'appointment_time')
        
        status_filter = request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        serializer = AppointmentListSerializer(queryset, many=True)
        # Return list directly since we're not using pagination
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'], url_path='stats')
    def stats(self, request):
        queryset = self.get_queryset()
        
        status_counts = {}
        for status_choice in Appointment.STATUS_CHOICES:
            status_code = status_choice[0]
            count = queryset.filter(status=status_code).count()
            if count > 0:
                status_counts[status_code] = count
        
        return Response({
            'total': queryset.count(),
            'by_status': status_counts,
            'today': queryset.filter(appointment_date=timezone.now().date()).count(),
            'upcoming': queryset.filter(
                appointment_date__gte=timezone.now().date(),
                status__in=['pending', 'scheduled', 'in_progress']
            ).count()
        })
    
    @action(detail=True, methods=['post'], url_path='reschedule')
    def reschedule(self, request, pk=None):
        appointment = self.get_object()
        
        new_date = request.data.get('appointment_date')
        new_time = request.data.get('appointment_time')
        new_end_time = request.data.get('end_time')
        
        if not new_date or not new_time:
            return Response({
                'error': 'appointment_date and appointment_time are required.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        appointment.appointment_date = new_date
        appointment.appointment_time = new_time
        if new_end_time:
            appointment.end_time = new_end_time
        
        appointment.status = 'rescheduled'
        appointment.save()
        
        detail_serializer = AppointmentDetailSerializer(appointment)
        return Response(detail_serializer.data)
    
    def destroy(self, request, *args, **kwargs):
        appointment = self.get_object()
        appointment.status = 'cancelled'
        appointment.cancelled_at = timezone.now()
        appointment.cancelled_by = request.user
        appointment.cancellation_reason = 'Deleted by user'
        appointment.save()
        
        return Response({
            'message': f'Appointment {appointment.id} has been cancelled.',
            'appointment': AppointmentDetailSerializer(appointment).data
        }, status=status.HTTP_200_OK)