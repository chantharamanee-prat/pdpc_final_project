from django import forms
from django.contrib.auth.forms import AuthenticationForm
from .models import MstPdpaQuestion, TnxResultDocument

class CustomLoginForm(AuthenticationForm):
    username = forms.CharField(label='Username', max_length=254)
    password = forms.CharField(label='Password', widget=forms.PasswordInput)

class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True

class MultipleFileField(forms.FileField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("widget", MultipleFileInput())
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        single_file_clean = super().clean
        if isinstance(data, (list, tuple)):
            result = [single_file_clean(d, initial) for d in data]
        else:
            result = [single_file_clean(data, initial)]
        return result

class CustomMstPdpaQuestionForm(forms.ModelForm):
    class Meta:
        model = MstPdpaQuestion
        widgets = {
            'answers': forms.CheckboxSelectMultiple,
        }
        fields = '__all__'


class TnxResultDocumentForm(forms.Form):

    file = forms.FileField(label="Select a file")