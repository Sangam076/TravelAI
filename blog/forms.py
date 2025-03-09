from django import forms
from .models import Profile
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from tinymce.widgets import TinyMCE


# forms.py
class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['photo', 'bio', 'twitter', 'facebook', 'instagram', 'linkedin']
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 3}),
        }





class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['photo', 'bio', 'twitter', 'facebook', 'instagram', 'linkedin']
        widgets = {
            'bio': forms.Textarea(attrs={'class': 'w-full'}),
            'twitter': forms.URLInput(attrs={'class': 'w-full'}),
            'facebook': forms.URLInput(attrs={'class': 'w-full'}),
            'instagram': forms.URLInput(attrs={'class': 'w-full'}),
            'linkedin': forms.URLInput(attrs={'class': 'w-full'}),
        }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        if 'user' in self.fields:
            del self.fields['user']



# forms.py
from django import forms
from .models import TravelPlan

class TravelPlanForm(forms.ModelForm):
    class Meta:
        model = TravelPlan
        fields = ['destination', 'duration', 'budget', 'interests', 'group_type']
        widgets = {
            'interests': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Enter interests separated by commas (e.g., beach, hiking, food)'}),
        }