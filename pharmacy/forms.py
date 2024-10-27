from django import forms
from .models import *
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model

User = get_user_model()

from django import forms
from django.contrib.auth.forms import AuthenticationForm

class CustomLoginForm(AuthenticationForm):
    username = forms.CharField(max_length=150, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'}))

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'category', 'supplier', 'stock_quantity', 'price', 'expiry_date', 'image']

from django import forms
from django_select2.forms import Select2Widget

class SaleForm(forms.ModelForm):
    class Meta:
        model = SaleProduct
        fields = ['product', 'quantity']
        widgets = {
            'product': Select2Widget,  # Use Select2 widget for product field
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Limit product choices to available stock
        self.fields['product'].queryset = Product.objects.filter(stock_quantity__gt=0)

    def clean_quantity(self):
        quantity = self.cleaned_data.get('quantity')
        product = self.cleaned_data.get('product')

        if product and quantity > product.stock_quantity:
            raise forms.ValidationError(f"Cannot order more than {product.stock_quantity} units of {product.name}.")
        
        return quantity


from django.forms import modelformset_factory

SaleFormSet = modelformset_factory(SaleProduct, form=SaleForm, extra=5)  # Adjust 'extra' to the number of forms you want to display by default


class PharmacyForm(forms.ModelForm):
    class Meta:
        model = Pharmacy
        fields = ['name', 'location']

from django import forms

from django.core.exceptions import ValidationError

"""class CustomAdminSignUpForm(forms.ModelForm):
    username = forms.CharField(max_length=150, required=True)
    email = forms.EmailField(required=True)
     # Use TextInput to display password as plain text
    password = forms.CharField(widget=forms.TextInput, required=True)
    password2 = forms.CharField(widget=forms.TextInput, label="Confirm Password", required=True)

    class Meta:
        model = User
        fields = ['username', 'email','password','password2']
"""
class CustomAdminSignUpForm(AuthenticationForm):#forms.Form):
    username = forms.CharField(max_length=150, required=True,widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username'}))
    email = forms.EmailField(required=True,widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'}), required=True)
    password2 = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirm Password'}), label=None, required=True)

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("This username is already taken.")
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("This email is already registered.")
        return email

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password2 = cleaned_data.get('password2')

        if password and password2 and password != password2:
            raise forms.ValidationError("Passwords do not match.")

        return cleaned_data

    def save(self):
        user = User.objects.create_user(
            username=self.cleaned_data['username'],
            email=self.cleaned_data['email'],
            password=self.cleaned_data['password']
        )
        return user



class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'category', 'supplier', 'stock_quantity', 'price', 'cost_price', 'expiry_date', 'image']


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name']


class SupplierForm(forms.ModelForm):
    class Meta:
        model = Supplier
        fields = ['name','contact','email']


class ProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = [
            'username', 'first_name', 'last_name', 'email', 'image'
        ]

    def __init__(self, *args, **kwargs):
        super(ProfileForm, self).__init__(*args, **kwargs)
        # Customize field properties (optional)
        #self.fields['role'].widget.attrs.update({'class': 'form-control'})
        #self.fields['pharmacy'].widget.attrs.update({'class': 'form-control'})
        self.fields['image'].widget.attrs.update({'class': 'form-control-file'})
        #self.fields['suspended'].widget.attrs.update({'class': 'form-check-input'})



"""
class SaleForm(forms.ModelForm):
    class Meta:
        model = Sale
        fields = ['product', 'quantity', 'total_price', 'salesperson', 'order_status']  # Exclude 'date_of_sale' as it's auto-populated

    # Optionally, override the init method to customize the form behavior if needed
    def __init__(self, *args, **kwargs):
        super(SaleForm, self).__init__(*args, **kwargs)
        self.fields['product'].widget.attrs.update({'class': 'form-control'})
        self.fields['quantity'].widget.attrs.update({'class': 'form-control'})
        self.fields['total_price'].widget.attrs.update({'class': 'form-control'})
        self.fields['salesperson'].widget.attrs.update({'class': 'form-control'})
        self.fields['order_status'].widget.attrs.update({'class': 'form-control'})
"""
"""
class SaleForm(forms.ModelForm):
    class Meta:
        model = Sale
        fields = ['product', 'quantity', 'total_price', 'salesperson', 'order_status']  # Exclude 'date_of_sale' as it's auto-populated
        widgets = {
            'order_status': forms.Select(choices=Sale.STATUS_CHOICES),
            'salesperson': forms.Select(),

        }

    # Optionally, override the init method to customize the form behavior if needed
    def __init__(self, *args, **kwargs):
        super(SaleForm, self).__init__(*args, **kwargs)
        self.fields['product'].widget.attrs.update({'class': 'form-control'})
        self.fields['quantity'].widget.attrs.update({'class': 'form-control'})
        self.fields['total_price'].widget.attrs.update({'class': 'form-control'})
        self.fields['salesperson'].widget.attrs.update({'class': 'form-control'})
        self.fields['order_status'].widget.attrs.update({'class': 'form-control'})
"""