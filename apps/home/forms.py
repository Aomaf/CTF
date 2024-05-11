from django import forms
from .models import Challenge


class ImageFileUploadForm(forms.Form):
    class Meta:
        model = Challenge
        fields = ["filepath",] 