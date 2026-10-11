from decimal import Decimal

from django.db.models import DecimalField, ExpressionWrapper, F, Q, Sum
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import InventoryItem, ReorderRequest, StockMovement, Supplier
from .serializers import (
    InventoryItemSerializer,
    InventoryStatsSerializer,
    ReorderRequestSerializer,
    ReorderStatusUpdateSerializer,
    StockMovementCreateSerializer,
    StockMovementSerializer,
    SupplierSerializer,
)


class SupplierViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = SupplierSerializer
    queryset = Supplier.objects.all()

    def get_queryset(self):
        qs = super().get_queryset()
        search = self.request.query_params.get('search', '')
        if search:
            qs = qs.filter(
                Q(name__icontains=search) |
                Q(contact_person__icontains=search) |
                Q(phone__icontains=search) |
                Q(email__icontains=search)
            )
        active = self.request.query_params.get('is_active')
        if active is not None:
            qs = qs.filter(is_active=active.lower() in ('1', 'true', 'yes'))
        return qs


class InventoryItemViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = InventoryItemSerializer
    queryset = InventoryItem.objects.select_related('supplier', 'catalog_item').all()

    def get_queryset(self):
        qs = super().get_queryset()
        search = self.request.query_params.get('search', '')
        if search:
            qs = qs.filter(
                Q(sku__icontains=search) |
                Q(name__icontains=search) |
                Q(location__icontains=search)
            )
        category = self.request.query_params.get('category')
        if category:
            qs = qs.filter(category=category)
        supplier = self.request.query_params.get('supplier')
        if supplier:
            qs = qs.filter(supplier_id=supplier)
        low_stock = self.request.query_params.get('low_stock')
        if low_stock and low_stock.lower() in ('1', 'true', 'yes'):
            qs = qs.filter(quantity_on_hand__lte=F('reorder_level'))
        active = self.request.query_params.get('is_active')
        if active is not None:
            qs = qs.filter(is_active=active.lower() in ('1', 'true', 'yes'))
        return qs

    @action(detail=False, methods=['get'], url_path='low-stock')
    def low_stock(self, request):
        items = self.get_queryset().filter(quantity_on_hand__lte=F('reorder_level'), is_active=True)
        serializer = self.get_serializer(items, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='stats')
    def stats(self, request):
        items = InventoryItem.objects.filter(is_active=True)
        low_stock_count = items.filter(quantity_on_hand__lte=F('reorder_level')).count()
        total_value = items.aggregate(
            total=Sum(
                ExpressionWrapper(
                    F('quantity_on_hand') * F('unit_cost'),
                    output_field=DecimalField(max_digits=14, decimal_places=2),
                )
            )
        )['total'] or Decimal('0')

        by_category = {}
        for category, _label in InventoryItem.CATEGORY_CHOICES:
            by_category[category] = items.filter(category=category).count()

        data = {
            'total_items': items.count(),
            'low_stock_count': low_stock_count,
            'total_stock_value': total_value,
            'by_category': by_category,
            'pending_reorders': ReorderRequest.objects.filter(status__in=['pending', 'ordered']).count(),
            'active_suppliers': Supplier.objects.filter(is_active=True).count(),
        }
        return Response(InventoryStatsSerializer(data).data)

    @action(detail=True, methods=['post'], url_path='adjust-stock')
    def adjust_stock(self, request, pk=None):
        item = self.get_object()
        payload = {
            'item': item.id,
            'movement_type': request.data.get('movement_type', 'adjust'),
            'quantity': request.data.get('quantity'),
            'reference': request.data.get('reference', ''),
            'notes': request.data.get('notes', ''),
        }
        serializer = StockMovementCreateSerializer(data=payload, context={'request': request})
        serializer.is_valid(raise_exception=True)
        movement = serializer.save()
        return Response({
            'movement': StockMovementSerializer(movement).data,
            'item': InventoryItemSerializer(item).data,
        }, status=status.HTTP_200_OK)


class StockMovementViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    permission_classes = [IsAuthenticated]
    queryset = StockMovement.objects.select_related('item', 'created_by').all()

    def get_serializer_class(self):
        if self.action == 'create':
            return StockMovementCreateSerializer
        return StockMovementSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        item = self.request.query_params.get('item')
        if item:
            qs = qs.filter(item_id=item)
        movement_type = self.request.query_params.get('movement_type')
        if movement_type:
            qs = qs.filter(movement_type=movement_type)
        return qs

    def create(self, request, *args, **kwargs):
        serializer = StockMovementCreateSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        movement = serializer.save()
        return Response(StockMovementSerializer(movement).data, status=status.HTTP_201_CREATED)


class ReorderRequestViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = ReorderRequestSerializer
    queryset = ReorderRequest.objects.select_related('item', 'supplier', 'created_by').all()
    http_method_names = ['get', 'post', 'patch', 'delete', 'head', 'options']

    def get_queryset(self):
        qs = super().get_queryset()
        status_param = self.request.query_params.get('status')
        if status_param:
            qs = qs.filter(status=status_param)
        item = self.request.query_params.get('item')
        if item:
            qs = qs.filter(item_id=item)
        return qs

    @action(detail=True, methods=['patch'], url_path='status')
    def update_status(self, request, pk=None):
        reorder = self.get_object()
        serializer = ReorderStatusUpdateSerializer(
            reorder, data=request.data, context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        updated = serializer.save()
        return Response(ReorderRequestSerializer(updated).data)

    @action(detail=False, methods=['post'], url_path='from-low-stock')
    def from_low_stock(self, request):
        """Create pending reorders for all low-stock items that don't already have one."""
        low_items = InventoryItem.objects.filter(
            is_active=True,
            quantity_on_hand__lte=F('reorder_level'),
        )
        created = []
        for item in low_items:
            exists = ReorderRequest.objects.filter(
                item=item, status__in=['pending', 'ordered']
            ).exists()
            if exists:
                continue
            qty = item.reorder_quantity if item.reorder_quantity > 0 else Decimal('1')
            reorder = ReorderRequest.objects.create(
                item=item,
                supplier=item.supplier,
                quantity=qty,
                status='pending',
                created_by=request.user if request.user.is_authenticated else None,
                notes='Auto-created from low-stock alert',
            )
            created.append(reorder)
        return Response(
            ReorderRequestSerializer(created, many=True).data,
            status=status.HTTP_201_CREATED,
        )
