from django.contrib import admin
from .models import Table,TableSection,Category,MenuItem,Order
from django.utils.html import format_html
# Register your models here.
@admin.register(TableSection)
class tableSectionAdmin(admin.ModelAdmin):
  list_display = ('name', 'display_order', 'service_charge_percent', 'is_active')
  list_editable = ('display_order', 'is_active', 'service_charge_percent')
  search_fields = ('name',)

@admin.register(Table)
class TableAdmin(admin.ModelAdmin):
    list_display = ('table_number', 'section', 'capacity', 'status', 'is_active')
    list_filter = ('section', 'status', 'is_active')
    list_editable = ('status', 'is_active')
    search_fields = ('table_number',)
    list_select_related = ('section',)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('display_order', 'name', 'is_active')
    list_editable = ('is_active',) # Manager sirf active status toggle kar paye shayad?
    
    # Permission Logic: Agar admin nahi hai toh edit/delete nahi kar sakta
    def has_add_permission(self, request):
        return request.user.is_superuser

    def has_change_permission(self, request, obj=None):
        return request.user.is_superuser

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser

@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
    list_display = ('display_menu_image', 'name', 'category', 'price', 'food_type', 'is_available', 'is_out_of_stock')
    list_filter = ('category', 'food_type', 'is_available', 'is_out_of_stock')
    list_editable = ('is_available', 'is_out_of_stock')
    search_fields = ('name',)
    def display_menu_image(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="50" height="50" style="border-radius:5px;" />', obj.image.url)
        return "No Image"
    display_menu_image.short_description = 'Photo'
    def has_add_permission(self, request):
        return request.user.is_superuser

    def has_change_permission(self, request, obj=None):
        return True 

    def get_readonly_fields(self, request, obj=None):
        if not request.user.is_superuser:
            return [f.name for f in self.model._meta.fields] + ['price_with_tax', 'final_price']
        return super().get_readonly_fields(request, obj)

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser


admin.site.site_header = "RestoFlow Control Center"
admin.site.site_title = "RestoFlow Admin"
admin.site.index_title = "Welcome to Restaurant Management"

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    class Media:
        css = {
            'all': ('css/custom_admin.css',) # Ye file static/css mein banayein
        }