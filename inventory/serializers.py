from decimal import Decimal

from django.db import transaction
from django.utils import timezone
from rest_framework import serializers

from .models import InventoryItem, ReorderRequest, StockMovement, Supplier


class SupplierSerializer(serializers.ModelSerializer):
    items_count = serializers.SerializerMethodField()

    class Meta:
        model = Supplier
        fields = [
            'id', 'name', 'contact_person', 'phone', 'email',
            'address', 'notes', 'is_active', 'items_count',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'items_count']

    def get_items_count(self, obj):
        return obj.items.filter(is_active=True).count()


class InventoryItemSerializer(serializers.ModelSerializer):
    supplier_name = serializers.CharField(source='supplier.name', read_only=True)
    catalog_item_name = serializers.CharField(source='catalog_item.name', read_only=True)
    is_low_stock = serializers.BooleanField(read_only=True)
    stock_value = serializers.SerializerMethodField()

    class Meta:
        model = InventoryItem
        fields = [
            'id', 'sku', 'name', 'category', 'unit',
            'quantity_on_hand', 'reorder_level', 'reorder_quantity',
            'unit_cost', 'location', 'supplier', 'supplier_name',
            'catalog_item', 'catalog_item_name', 'notes',
            'is_active', 'is_low_stock', 'stock_value',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'is_low_stock', 'stock_value']

    def get_stock_value(self, obj):
        return obj.quantity_on_hand * obj.unit_cost


class StockMovementSerializer(serializers.ModelSerializer):
    item_sku = serializers.CharField(source='item.sku', read_only=True)
    item_name = serializers.CharField(source='item.name', read_only=True)
    created_by_name = serializers.SerializerMethodField()

    class Meta:
        model = StockMovement
        fields = [
            'id', 'item', 'item_sku', 'item_name',
            'movement_type', 'quantity', 'reference', 'notes',
            'created_by', 'created_by_name', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_by', 'created_at', 'updated_at']

    def get_created_by_name(self, obj):
        if not obj.created_by:
            return None
        return obj.created_by.full_name or obj.created_by.email


class StockMovementCreateSerializer(serializers.Serializer):
    item = serializers.PrimaryKeyRelatedField(queryset=InventoryItem.objects.all())
    movement_type = serializers.ChoiceField(choices=StockMovement.MOVEMENT_CHOICES)
    quantity = serializers.DecimalField(max_digits=12, decimal_places=2, min_value=Decimal('0.01'))
    reference = serializers.CharField(required=False, allow_blank=True, default='')
    notes = serializers.CharField(required=False, allow_blank=True, default='')

    def validate(self, data):
        item = data['item']
        movement_type = data['movement_type']
        quantity = data['quantity']

        if movement_type == 'out' and quantity > item.quantity_on_hand:
            raise serializers.ValidationError({
                'quantity': f'Insufficient stock. Available: {item.quantity_on_hand}.'
            })
        return data

    @transaction.atomic
    def create(self, validated_data):
        item = validated_data['item']
        movement_type = validated_data['movement_type']
        quantity = validated_data['quantity']
        user = self.context['request'].user

        if movement_type == 'in':
            item.quantity_on_hand += quantity
        elif movement_type == 'out':
            item.quantity_on_hand -= quantity
        else:  # adjust — set absolute? or relative?
            # Adjustment adds (can be used with out for decrease via separate type)
            # For adjust we treat quantity as the new absolute level via notes convention,
            # but simpler: adjust means set quantity_on_hand = quantity
            item.quantity_on_hand = quantity

        item.save(update_fields=['quantity_on_hand', 'updated_at'])

        return StockMovement.objects.create(
            item=item,
            movement_type=movement_type,
            quantity=quantity,
            reference=validated_data.get('reference', ''),
            notes=validated_data.get('notes', ''),
            created_by=user if user and user.is_authenticated else None,
        )


class ReorderRequestSerializer(serializers.ModelSerializer):
    item_sku = serializers.CharField(source='item.sku', read_only=True)
    item_name = serializers.CharField(source='item.name', read_only=True)
    supplier_name = serializers.CharField(source='supplier.name', read_only=True)
    created_by_name = serializers.SerializerMethodField()

    class Meta:
        model = ReorderRequest
        fields = [
            'id', 'item', 'item_sku', 'item_name',
            'supplier', 'supplier_name', 'quantity', 'status', 'notes',
            'ordered_at', 'received_at',
            'created_by', 'created_by_name',
            'created_at', 'updated_at',
        ]
        read_only_fields = [
            'id', 'ordered_at', 'received_at', 'created_by',
            'created_at', 'updated_at',
        ]

    def get_created_by_name(self, obj):
        if not obj.created_by:
            return None
        return obj.created_by.full_name or obj.created_by.email

    def create(self, validated_data):
        user = self.context['request'].user
        validated_data['created_by'] = user if user and user.is_authenticated else None
        if not validated_data.get('supplier') and validated_data['item'].supplier_id:
            validated_data['supplier'] = validated_data['item'].supplier
        if not validated_data.get('quantity'):
            validated_data['quantity'] = validated_data['item'].reorder_quantity or Decimal('1')
        return super().create(validated_data)


class ReorderStatusUpdateSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=ReorderRequest.STATUS_CHOICES)

    @transaction.atomic
    def update(self, instance, validated_data):
        new_status = validated_data['status']
        old_status = instance.status

        if new_status == old_status:
            return instance

        instance.status = new_status

        if new_status == 'ordered' and not instance.ordered_at:
            instance.ordered_at = timezone.now()

        if new_status == 'received' and old_status != 'received':
            instance.received_at = timezone.now()
            item = instance.item
            item.quantity_on_hand += instance.quantity
            item.save(update_fields=['quantity_on_hand', 'updated_at'])
            StockMovement.objects.create(
                item=item,
                movement_type='in',
                quantity=instance.quantity,
                reference=f'REORDER-{instance.id}',
                notes=f'Stock received from reorder #{instance.id}',
                created_by=self.context['request'].user if self.context.get('request') else None,
            )

        instance.save()
        return instance


class InventoryStatsSerializer(serializers.Serializer):
    total_items = serializers.IntegerField()
    low_stock_count = serializers.IntegerField()
    total_stock_value = serializers.DecimalField(max_digits=14, decimal_places=2)
    by_category = serializers.DictField()
    pending_reorders = serializers.IntegerField()
    active_suppliers = serializers.IntegerField()
