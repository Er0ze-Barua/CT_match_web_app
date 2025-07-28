# ctmatch_web/matcher/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.auth import get_user_model

class CustomUserCreationForm(UserCreationForm):
    # This form extends Django's built-in UserCreationForm
    # and adds an email field.

    email = forms.EmailField(required=True, label="Email Address")

    class Meta(UserCreationForm.Meta):
        # We're telling it to use the default User model
        # and to include 'email' along with default fields.
        model = get_user_model()
        fields = UserCreationForm.Meta.fields + ('email',)