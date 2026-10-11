from django.contrib import admin

from .models import InventoryItem, ReorderRequest, StockMovement, Supplier


@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ('name', 'contact_person', 'phone', 'email', 'is_active', 'created_at')
    list_filter = ('is_active',)
    search_fields = ('name', 'contact_person', 'phone', 'email')


@admin.register(InventoryItem)
class InventoryItemAdmin(admin.ModelAdmin):
    list_display = (
        'sku', 'name', 'category', 'quantity_on_hand',
        'reorder_level', 'unit', 'supplier', 'is_active',
    )
    list_filter = ('category', 'unit', 'is_active', 'supplier')
    search_fields = ('sku', 'name', 'location')
    autocomplete_fields = ('supplier',)
    raw_id_fields = ('catalog_item',)


@admin.register(StockMovement)
class StockMovementAdmin(admin.ModelAdmin):
    list_display = ('item', 'movement_type', 'quantity', 'reference', 'created_by', 'created_at')
    list_filter = ('movement_type',)
    search_fields = ('item__sku', 'item__name', 'reference')
    autocomplete_fields = ('item',)


@admin.register(ReorderRequest)
class ReorderRequestAdmin(admin.ModelAdmin):
    list_display = ('item', 'quantity', 'status', 'supplier', 'created_at', 'ordered_at', 'received_at')
    list_filter = ('status',)
    search_fields = ('item__sku', 'item__name')
    autocomplete_fields = ('item', 'supplier')
