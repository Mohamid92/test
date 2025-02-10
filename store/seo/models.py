from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

class MetaData(models.Model):
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    
    title = models.CharField(max_length=200)
    meta_description = models.CharField(max_length=255)
    meta_keywords = models.CharField(max_length=255)
    og_title = models.CharField(max_length=200, blank=True)
    og_description = models.CharField(max_length=255, blank=True)
    og_image = models.ImageField(upload_to='og-images/', blank=True)
    
    canonical_url = models.URLField(blank=True)
    is_noindex = models.BooleanField(default=False)
    schema_markup = models.JSONField(default=dict, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=['content_type', 'object_id']),
        ]
