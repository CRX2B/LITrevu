from django.db import models
from authentication.models import User
from django.conf import settings
from PIL import Image

class Ticket(models.Model):
    title = models.CharField(max_length=128)
    description = models.TextField(max_length=2048, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    image = models.ImageField(upload_to="tickets/", null=True, blank=True)
    
    IMAGE_MAX_SIZE = (500, 500)
    
    def resize_image(self):
        if self.image:
            image = Image.open(self.image)
            image.thumbnail(self.IMAGE_MAX_SIZE)
            image.save(self.image.path)
            
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.resize_image()
        
        
class Review(models.Model):
    RATING_CHOICES = [(1, "1"), (2, "2"), (3, "3"), (4, "4"), (5, "5")]

    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, null=True, blank=True)
    rating = models.PositiveSmallIntegerField(choices=RATING_CHOICES)
    headline = models.CharField(max_length=128)
    body = models.TextField(max_length=8192, blank=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    


class UserFollows(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="following")
    followed_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="followers")
    
    class Meta:
        unique_together = ("user", "followed_user")
    



