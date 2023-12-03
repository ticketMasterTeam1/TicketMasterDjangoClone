from django import forms
from .models import Band
from .models import Reviews


class SubmitReview(forms.ModelForm):
    class Meta:
        model = Reviews
        fields = '__all__'

        widgets = {
            'review': forms.TextInput(attrs={'class': 'form-control'})
        }