 
from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.auth import get_user_model

class CustomUserCreationForm(UserCreationForm):
    

    email = forms.EmailField(required=True, label="Email Address")

    class Meta(UserCreationForm.Meta):
        
        model = get_user_model()
        fields = UserCreationForm.Meta.fields + ('email',)