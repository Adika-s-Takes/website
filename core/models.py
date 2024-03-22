from django.db import models
from autoslug import AutoSlugField


class DripGuide(models.Model):
    title = models.CharField(max_length=300)
    slug = AutoSlugField(populate_from="title")
    featured_image = models.FileField(upload_to="images/drips", null=True)
    active = models.BooleanField(default=False)
    body = models.TextField()
    date_uploaded = models.DateField(auto_now=True)

    def __str__(self):
        return self.title

# Create your models here.
