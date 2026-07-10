from django.contrib import admin
from .models import HomepageBanner

class HomepageBannerAdmin(admin.ModelAdmin):
    list_display = ('title', 'is_active', 'created_date')
    list_editable = ('is_active',)
# Register your models here.
admin.site.register(HomepageBanner, HomepageBannerAdmin)