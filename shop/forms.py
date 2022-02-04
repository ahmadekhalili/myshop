from django import forms
from .models import Product, Category

class IndexCartAddProductForm(forms.Form):
    quantity = forms.IntegerField(initial=1, widget=forms.HiddenInput) #has been tested integer for CartAddProductForm.
    update = forms.BooleanField(required=False, initial=False,
                                widget=forms.HiddenInput)
