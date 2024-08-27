from django import forms
from django.contrib.auth.forms import AuthenticationForm
from .models import MstPdpaQuestion

class CustomLoginForm(AuthenticationForm):
    username = forms.CharField(label='Username', max_length=254)
    password = forms.CharField(label='Password', widget=forms.PasswordInput)

class CustomMstPdpaQuestionForm(forms.ModelForm):

    file = forms.FileField(required=False, help_text="Upload a file.")

    class Meta:
        model = MstPdpaQuestion
        widgets = {
            'answers': forms.CheckboxSelectMultiple,
        }
        fields = '__all__'