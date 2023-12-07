from django import forms
from .models import Band
from .models import Reviews


class SubmitReview(forms.ModelForm):
    class Meta:
        model = Reviews
        fields = ['review', 'rating']

        widgets = {
            'review': forms.TextInput(attrs={'class': 'form-control'}),
            'band': forms.TextInput(attrs={'class': 'hidden'}),
            'rating': forms.Select(attrs={'class': 'form-control'})
        }
