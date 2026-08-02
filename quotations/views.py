from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q, Sum, Count
from django.utils import timezone
from django.shortcuts import get_object_or_404
from datetime import datetime, timedelta
from .models import Quotation, QuotationArea, QuotationSurface,SurfaceSpec  
from .serializers import (
    QuotationListSerializer,
    QuotationDetailSerializer,
    QuotationCreateUpdateSerializer,
    QuotationStatusUpdateSerializer,
    QuotationStatsSerializer
)


class QuotationViewSet(viewsets.ModelViewSet):
    """
    Quotation ViewSet with full CRUD operations and custom actions.
    
    Provides:
    - list: GET /api/quotations/
    - create: POST /api/quotations/
    - retrieve: GET /api/quotations/{id}/
    - update: PUT /api/quotations/{id}/
    - partial_update: PATCH /api/quotations/{id}/
    - destroy: DELETE /api/quotations/{id}/
    
    Custom Actions:
    - status: PATCH /api/quotations/{id}/status/
    - stats: GET /api/quotations/stats/
    - duplicate: POST /api/quotations/{id}/duplicate/
    - send: PATCH /api/quotations/{id}/send/
    - accept: PATCH /api/quotations/{id}/accept/
    - cancel: PATCH /api/quotations/{id}/cancel/
    """
    permission_classes = [IsAuthenticated]
    queryset = Quotation.objects.select_related(
        'customer', 'appointment', 'work_type', 'prepared_by'
    ).all()
    
    def get_serializer_class(self):
        if self.action == 'list':
            return QuotationListSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return QuotationCreateUpdateSerializer
        else:
            return QuotationDetailSerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filter by status
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        # Filter by customer
        customer = self.request.query_params.get('customer')
        if customer:
            queryset = queryset.filter(customer_id=customer)
        
        # Filter by work type
        work_type = self.request.query_params.get('work_type')
        if work_type:
            queryset = queryset.filter(work_type_id=work_type)
        
        # Filter by date range
        date_from = self.request.query_params.get('date_from')
        if date_from:
            queryset = queryset.filter(issued_date__gte=date_from)
        date_to = self.request.query_params.get('date_to')
        if date_to:
            queryset = queryset.filter(issued_date__lte=date_to)
        
        # Filter by quote type
        quote_type = self.request.query_params.get('quote_type')
        if quote_type:
            queryset = queryset.filter(quote_type=quote_type)
        
        # Search
        search = self.request.query_params.get('search', '')
        if search:
            queryset = queryset.filter(
                Q(id__icontains=search) |
                Q(customer__first_name__icontains=search) |
                Q(customer__last_name__icontains=search) |
                Q(customer__phone__icontains=search) |
                Q(customer__email__icontains=search)
            )
        
        return queryset.order_by('-issued_date')
    
    def perform_create(self, serializer):
        """Create quotation with prepared_by set to current user"""
        serializer.save(prepared_by=self.request.user)
    
    @action(detail=True, methods=['patch'], url_path='status')
    def update_status(self, request, pk=None):
        """
        Update quotation status.
        PATCH /api/quotations/{id}/status/
        {
            "status": "sent" | "accepted" | "cancelled"
        }
        """
        quotation = self.get_object()
        serializer = QuotationStatusUpdateSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        new_status = serializer.validated_data['status']
        old_status = quotation.status
        
        # Validation
        if old_status == 'accepted' and new_status != 'cancelled':
            return Response({
                'error': 'Accepted quotations can only be cancelled.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if old_status == 'cancelled':
            return Response({
                'error': 'Cancelled quotations cannot be changed.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Handle special status transitions
        if new_status == 'sent':
            quotation.sent_date = timezone.now()
            quotation.sent_via = request.data.get('sent_via', 'email')
        elif new_status == 'accepted':
            quotation.accepted_date = timezone.now()
        elif new_status == 'cancelled':
            # You might want to add cancellation reason
            pass
        
        quotation.status = new_status
        quotation.save()
        
        detail_serializer = QuotationDetailSerializer(quotation)
        return Response(detail_serializer.data)
    
    @action(detail=True, methods=['post'], url_path='duplicate')
    def duplicate(self, request, pk=None):
        """
        Duplicate an existing quotation.
        POST /api/quotations/{id}/duplicate/
        """
        original = self.get_object()
        
        # Get customer ID from request or use original
        customer_id = request.data.get('customer')
        if customer_id:
            try:
                from customers.models import Customer
                customer = Customer.objects.get(id=customer_id)
            except Customer.DoesNotExist:
                return Response({
                    'error': 'Customer not found.'
                }, status=status.HTTP_404_NOT_FOUND)
        else:
            customer = original.customer
        
        # Create new quotation
        new_quotation = Quotation.objects.create(
            customer=customer,
            appointment=original.appointment,
            status=request.data.get('status', 'draft'),
            quote_type=original.quote_type,
            work_type=original.work_type,
            discount_percentage=original.discount_percentage,
            valid_until=timezone.now().date() + timedelta(days=30),
            prepared_by=request.user
        )
        
        # Duplicate areas and surfaces
        for area in original.areas.all():
            new_area = QuotationArea.objects.create(
                quotation=new_quotation,
                area_type=area.area_type,
                display_name=area.display_name,
                sort_order=area.sort_order
            )
            
            for surface in area.surfaces.all():
                new_surface = QuotationSurface.objects.create(
                    area=new_area,
                    surface_name=surface.surface_name,
                    surface_type=surface.surface_type,
                    width_cm=surface.width_cm,
                    height_cm=surface.height_cm,
                    opening_direction=surface.opening_direction,
                    special_requirements=surface.special_requirements,
                    sort_order=surface.sort_order
                )
                
                # Duplicate spec if exists
                if hasattr(surface, 'spec'):
                    spec = surface.spec
                    SurfaceSpec.objects.create(
                        surface=new_surface,
                        fabric_type=spec.fabric_type,
                        model=spec.model,
                        catalog_item=spec.catalog_item,
                        fabric_code=spec.fabric_code,
                        unit_price_per_m2=spec.unit_price_per_m2,
                        motor_control_type=spec.motor_control_type,
                        motor_type=spec.motor_type,
                        motor_price_per_unit=spec.motor_price_per_unit,
                        smart_integration=spec.smart_integration,
                        alexa_quantity=spec.alexa_quantity,
                        alexa_unit_price=spec.alexa_unit_price,
                        pelmet_enabled=spec.pelmet_enabled,
                        pelmet_width_cm=spec.pelmet_width_cm,
                        pelmet_price_per_metre=spec.pelmet_price_per_metre,
                        addon_label=spec.addon_label,
                        addon_amount=spec.addon_amount
                    )
        
        # Recalculate totals
        new_quotation.recalc_totals()
        
        detail_serializer = QuotationDetailSerializer(new_quotation)
        return Response(detail_serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['patch'], url_path='send')
    def send_quotation(self, request, pk=None):
        """
        Mark quotation as sent.
        PATCH /api/quotations/{id}/send/
        {
            "sent_via": "email" | "whatsapp" | "sms"
        }
        """
        quotation = self.get_object()
        
        if quotation.status == 'cancelled':
            return Response({
                'error': 'Cannot send a cancelled quotation.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        sent_via = request.data.get('sent_via', 'email')
        quotation.status = 'sent'
        quotation.sent_date = timezone.now()
        quotation.sent_via = sent_via
        quotation.save()
        
        detail_serializer = QuotationDetailSerializer(quotation)
        return Response(detail_serializer.data)
    
    @action(detail=True, methods=['patch'], url_path='accept')
    def accept_quotation(self, request, pk=None):
        """
        Mark quotation as accepted.
        PATCH /api/quotations/{id}/accept/
        """
        quotation = self.get_object()
        
        if quotation.status == 'cancelled':
            return Response({
                'error': 'Cannot accept a cancelled quotation.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        quotation.status = 'accepted'
        quotation.accepted_date = timezone.now()
        quotation.save()
        
        detail_serializer = QuotationDetailSerializer(quotation)
        return Response(detail_serializer.data)
    
    @action(detail=True, methods=['patch'], url_path='cancel')
    def cancel_quotation(self, request, pk=None):
        """
        Cancel quotation.
        PATCH /api/quotations/{id}/cancel/
        {
            "cancellation_reason": "Client changed mind"
        }
        """
        quotation = self.get_object()
        
        if quotation.status == 'cancelled':
            return Response({
                'error': 'Quotation is already cancelled.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        cancellation_reason = request.data.get('cancellation_reason', 'No reason provided')
        quotation.status = 'cancelled'
        # You might want to add a cancellation_reason field to the model
        quotation.save()
        
        detail_serializer = QuotationDetailSerializer(quotation)
        return Response(detail_serializer.data)
    
    @action(detail=False, methods=['get'], url_path='stats')
    def stats(self, request):
        """
        Get quotation statistics.
        GET /api/quotations/stats/
        """
        queryset = self.get_queryset()
        
        # Total count
        total = queryset.count()
        
        # Status breakdown
        status_counts = {}
        for status_choice in Quotation.STATUS_CHOICES:
            status_code = status_choice[0]
            count = queryset.filter(status=status_code).count()
            if count > 0:
                status_counts[status_code] = count
        
        # Total value
        total_value = queryset.aggregate(Sum('total'))['total__sum'] or 0
        
        # Accepted value
        accepted_value = queryset.filter(status='accepted').aggregate(Sum('total'))['total__sum'] or 0
        
        # Pending value
        pending_value = queryset.filter(status='pending').aggregate(Sum('total'))['total__sum'] or 0
        
        # This month
        today = timezone.now().date()
        first_day = today.replace(day=1)
        this_month = queryset.filter(issued_date__gte=first_day).count()
        
        return Response({
            'total': total,
            'by_status': status_counts,
            'total_value': total_value,
            'accepted_value': accepted_value,
            'pending_value': pending_value,
            'this_month': this_month
        })
    
    def destroy(self, request, *args, **kwargs):
        """
        Soft delete - cancel quotation instead of hard delete.
        """
        quotation = self.get_object()
        
        if quotation.status == 'accepted':
            return Response({
                'error': 'Cannot delete an accepted quotation. Cancel it first.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        quotation.status = 'cancelled'
        quotation.save()
        
        return Response({
            'message': f'Quotation {quotation.id} has been cancelled.',
            'quotation': QuotationDetailSerializer(quotation).data
        }, status=status.HTTP_200_OK)