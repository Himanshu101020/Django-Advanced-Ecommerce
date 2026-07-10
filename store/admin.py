from django.contrib import admin
from .models import Product, Variation

# 1. Create an Inline class for the child model
# class VariationInline(admin.TabularInline):
#     model = Variation
#     extra = 1  # How many blank rows to show by default


class ProductAdmin(admin.ModelAdmin):
    list_display = ('product_name', 'price', 'stock', 'category', 'modified_date', 'is_available')
    prepopulated_fields = {'slug': ('product_name',)}
    # inlines = [VariationInline] # This injects the variation table directly into the Product page!

class VariationAdmin(admin.ModelAdmin):
    list_display = ('product', 'variation_category', 'variation_value', 'is_active')
    list_editable = ('is_active',)
    list_filter = ('product', 'variation_category', 'variation_value')

admin.site.register(Product, ProductAdmin)
admin.site.register(Variation, VariationAdmin)