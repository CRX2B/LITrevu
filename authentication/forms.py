from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from django import forms

class SignupForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = get_user_model()
        fields = ["username", "email", "password1", "password2"]
        
class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = get_user_model()
        fields = ["username", "email", "first_name", "last_name"]
        

