from django import forms
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import Prompt, PromptSet

# Field dropdown choices
ch_status = (
    ('In Progress', 'In Progress'),
    ('Completed', 'Completed')
)

ch_rating = (
    (0, "0/10"),
    (1, "1/10"),
    (2, "2/10"),
    (3, "3/10"),
    (4, "4/10"),
    (5, "5/10"),
    (6, "610"),
    (7, "7/10"),
    (8, "8/10"),
    (9, "9/10"),
    (10, "10/10"),
)

# Authentication Forms
class SignupForm(UserCreationForm):
    usertag = forms.CharField(max_length=100, required=True, help_text="Other users will identify you by your usertag.")
    access_code = forms.CharField(max_length=100, required=True, help_text="Use the access code sent by your professor.")

    class Meta:
        model = User
        fields = ('username', 'usertag', 'password1', 'password2',)

class SigninForm(forms.Form):
    username = forms.CharField(max_length=150, required=True)
    password = forms.CharField(min_length=8, max_length=150, widget=forms.PasswordInput)

# Create/Edit Forms
class PromptForm(forms.ModelForm):
    class Meta:
        model = Prompt
        fields = ('name', 'ref', 'difficulty', 'description', 'hint', 'prompt_set')

class PromptSetForm(forms.ModelForm):
    class Meta:
        model = PromptSet
        fields = "__all__"

class AccessCodeForm(forms.Form):
    quantity = forms.IntegerField(min_value=1, required=True)
    code_length = forms.IntegerField(min_value=8, max_value=32, help_text="# of characters for access code", label="Code Length", required=True)

# Misc Forms
class SubmitPromptForm(forms.Form):
    status = forms.CharField(max_length=64, widget=forms.Select(choices=ch_status))
    satisfaction = forms.CharField(max_length=1, widget=forms.Select(choices=ch_rating))
