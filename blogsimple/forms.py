from django.forms import ModelForm, Textarea, TextInput, PasswordInput
from models import Blog
from django.contrib.auth.forms import AuthenticationForm
from django import forms

"""
Add Bootstrap CSS class
"""
class BlogForm(ModelForm):
    class Meta:
        model=Blog
        widgets = {
            'body': Textarea(attrs={'class':'form-control', 'rows':10}),
            'title': TextInput(attrs={'class':'form-control'}),
}

class BlogAuthenticationForm(AuthenticationForm):
    username = forms.CharField(widget=TextInput(attrs={'class':'form-control'}))
    password = forms.CharField(widget=PasswordInput(attrs={'class':'form-control'}))
