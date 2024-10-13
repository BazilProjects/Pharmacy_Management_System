from django import forms
from .models import Product, Sale

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'category', 'supplier', 'stock_quantity', 'price', 'expiry_date', 'image']

class SaleForm(forms.ModelForm):
    class Meta:
        model = Sale
        fields = ['product', 'quantity']
