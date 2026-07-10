from django.db import models

# Create your models here.
class HomepageBanner(models.Model):
    title = models.CharField(max_length=100, help_text="Internal name for the banner")
    image = models.ImageField(upload_to='photos/banners')
    is_active = models.BooleanField(default=False, help_text="Check this to display on the homepage")
    created_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title