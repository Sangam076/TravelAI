from django.db import models
from django.utils.timezone import now
from PIL import Image
from tinymce.models import HTMLField
from django.contrib.auth.models import User
from django.db.models.signals import post_save


class Message(models.Model):
    sender = models.ForeignKey(User, related_name="sent_messages", on_delete=models.CASCADE)
    receiver = models.ForeignKey(User, related_name="received_messages", on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.sender} -> {self.receiver}: {self.content[:20]}" 


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    photo = models.ImageField(upload_to='profile_photos/', default='default.jpg')
    bio = models.TextField(blank=True, null=True)
    twitter = models.URLField(blank=True, null=True)
    facebook = models.URLField(blank=True, null=True)
    instagram = models.URLField(blank=True, null=True)
    linkedin = models.URLField(blank=True, null=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"
    
def create_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

post_save.connect(create_profile, sender=User)

from django.db import models
from django.contrib.auth.models import User

class TravelPlan(models.Model):
    BUDGET_CHOICES = [
        ('low', 'Low'),
        ('moderate', 'Moderate'),
        ('high', 'High'),
    ]
    
    GROUP_TYPE_CHOICES = [
        ('solo', 'Solo'),
        ('couple', 'Couple'),
        ('family', 'Family'),
        ('friends', 'Friends'),
    ]
    
    budget = models.CharField(max_length=10, choices=BUDGET_CHOICES, default='moderate')
    interests = models.TextField()
    group_type = models.CharField(max_length=10, choices=GROUP_TYPE_CHOICES, default='solo')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    
    destination = models.CharField(max_length=200)
    duration = models.IntegerField()
    
    # AI-generated content fields
    places_to_visit = models.TextField(blank=True, default="Default visit")
    activities = models.TextField(blank=True, default="Default activity")
    restaurants = models.TextField(blank=True, default="Default visit")
    best_time_to_visit = models.TextField(blank=True, default="Default visit")
    itinerary = models.TextField(blank=True, default="Default plan")
    packing_checklist = models.TextField(blank=True, default="Default list")
    budget_breakdown = models.TextField(blank=True, default="Default budget")
    
    # New fields
    is_saved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    
    def __str__(self):
        return f"{self.destination} - {self.user.username}"
    
import uuid
from django.db import models
from django.contrib.auth.models import User

class PlanInvite(models.Model):
    plan = models.ForeignKey('TravelPlan', on_delete=models.CASCADE)
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_invites')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_invites')
    token = models.UUIDField(default=uuid.uuid4, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    accepted = models.BooleanField(default=False)

    def get_invite_url(self):
        from django.urls import reverse
        return reverse('accept_invite', kwargs={'token': str(self.token)})
