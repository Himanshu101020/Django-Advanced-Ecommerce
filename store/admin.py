from django.contrib import admin
from .models import Product, ProductGallery, Variation, ReviewRating
import admin_thumbnails

# 1. Create an Inline class for the child model
# class VariationInline(admin.TabularInline):
#     model = Variation
#     extra = 1  # How many blank rows to show by default

@admin_thumbnails.thumbnail('image')
class ProductGalleryInline(admin.TabularInline):
    model = ProductGallery
    extra = 1


class ProductAdmin(admin.ModelAdmin):
    list_display = ('product_name', 'price', 'stock', 'category', 'modified_date', 'is_available')
    prepopulated_fields = {'slug': ('product_name',)}
    inlines = [ProductGalleryInline]
    # inlines = [VariationInline] # This injects the variation table directly into the Product page!

class VariationAdmin(admin.ModelAdmin):
    list_display = ('product', 'variation_category', 'variation_value', 'is_active')
    list_editable = ('is_active',)
    list_filter = ('product', 'variation_category', 'variation_value')




admin.site.register(Product, ProductAdmin)
admin.site.register(Variation, VariationAdmin)
admin.site.register(ReviewRating)
admin.site.register(ProductGallery)