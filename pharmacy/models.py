from django.db import models
from django.contrib.auth.models import AbstractUser
import datetime
from django.db import models
from django.contrib.auth.models import User  # Ensure you have the User model imported

from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission

from django.db import models
from django.conf import settings  # Import settings to reference the custom user model

class Pharmacy(models.Model):
    name = models.CharField(max_length=255,blank=True,null=True)
    location = models.CharField(max_length=255,blank=True,null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,  # Use AUTH_USER_MODEL for the custom user model
        on_delete=models.CASCADE,   # Define the behavior on user deletion
        blank=True,
        null=True,
        related_name='pharmacies'   # This allows reverse lookup
    )
    supervised_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,  # Use AUTH_USER_MODEL for the custom user model
        on_delete=models.CASCADE,   # Define the behavior on user deletion
        blank=True,
        null=True,
        related_name='super_vising_pharmacist'   # This allows reverse lookup
    )

    def __str__(self):
        return self.name


class User(AbstractUser):
    ROLES = (
        ('admin', 'Admin'),
        ('salesperson', 'Salesperson'),
        ('manager', 'Manager'),  # Added manager role
        ('cashier','Cashier'),
        ('supervising_pharmacist','Supervising_Pharmacist'),
    )
    
    role = models.CharField(max_length=25, choices=ROLES)
    suspended = models.BooleanField(default=False)
    pharmacy = models.ForeignKey(Pharmacy, on_delete=models.CASCADE, null=True, blank=True, related_name='creators_users')
    image=models.ImageField(upload_to='media/user_profile/', null=True, blank=True)
    bossed_by=models.ForeignKey(Pharmacy, on_delete=models.CASCADE, null=True, blank=True, related_name='pharmacy_boss')

    def __str__(self):
        return self.username




class Category(models.Model):
    name = models.CharField(max_length=100, null=True, blank=True)
    pharmacy = models.ForeignKey(Pharmacy, on_delete=models.CASCADE, null=True, blank=True, related_name='categories')  # Associate with a pharmacy

    def __str__(self):
        return self.name if self.name else "Unnamed Category"


class Supplier(models.Model):
    name = models.CharField(max_length=100, null=True, blank=True)
    contact = models.CharField(max_length=100, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    date_joined = models.DateField(auto_now_add=True)
    pharmacy = models.ForeignKey(Pharmacy, on_delete=models.CASCADE, null=True, blank=True, related_name='suppliers')  # Associate with a pharmacy
    is_approved = models.BooleanField(default=False)
    def __str__(self):
        return self.name if self.name else "Unnamed Supplier"


class Product(models.Model):
    known_tags = (
        ('opiods', 'Opiods'),
        ('overthecounter', 'OverTheCounter'),
        ('prescription_based', 'Prescription_Based'),
    )
    name = models.CharField(max_length=100, null=True, blank=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, null=True, blank=True)
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE, null=True, blank=True)
    stock_quantity = models.IntegerField(null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    cost_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)  # New field
    expiry_date = models.DateField(null=True, blank=True)
    image = models.ImageField(upload_to='products/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    pharmacy = models.ForeignKey(Pharmacy, on_delete=models.CASCADE, null=True, blank=True, related_name='products')  # Associate with a pharmacy
    allow_sale = models.BooleanField(default=True)
    
    tags = models.CharField(max_length=25, choices=known_tags, default='overthecounter')
    def is_expired(self):
        return self.expiry_date < datetime.date.today()

    def __str__(self):
        return self.name if self.name else "Unnamed Product"


class Sale(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
    ]
    transaction_hash=models.CharField(max_length=3,null=True,blank=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    date_of_sale = models.DateTimeField(auto_now_add=True)
    salesperson = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    order_status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='completed', null=True, blank=True)
    pharmacy = models.ForeignKey(Pharmacy, on_delete=models.CASCADE, null=True, blank=True, related_name='sales')  # Associate with a pharmacy

    def __str__(self):
        return f"Sale of {self.transaction_hash} by {self.salesperson} on {self.date_of_sale}"


class SaleProduct(models.Model):
    sale = models.ForeignKey(Sale, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, null=True, blank=True)
    quantity = models.IntegerField(null=True, blank=True)
    price =  models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    def __str__(self):
        return f'{self.quantity} units of {self.product.name} in Sale {self.sale.id}'


class SaleReversal(models.Model):
    sale = models.ForeignKey(Sale, on_delete=models.CASCADE, null=True, blank=True)
    reason = models.TextField(null=True, blank=True)
    is_approved = models.BooleanField(default=False)
    request_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reversal_requests', null=True, blank=True)
    approved_by = models.ForeignKey(User, null=True, on_delete=models.SET_NULL, related_name='reversal_approvals', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    pharmacy = models.ForeignKey(Pharmacy, on_delete=models.CASCADE, null=True, blank=True, related_name='sale_reversals')  # Associate with a pharmacy

    def __str__(self):
        return f"Reversal for sale: {self.sale} by {self.request_by}"



class PrivateMessage(models.Model):
    sender = models.ForeignKey(User, related_name='sent_private_messages', on_delete=models.CASCADE)
    receiver = models.ForeignKey(User, related_name='received_private_messages', on_delete=models.CASCADE)
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)  # New field to track read status

    def __str__(self):
        return f"From {self.sender} to {self.receiver} at {self.timestamp}"

class GroupMessage(models.Model):
    sender = models.ForeignKey(User, related_name='sent_group_messages', on_delete=models.CASCADE)
    group_name = models.CharField(max_length=100)
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)  # New field for read status

    def __str__(self):
        return f"From {self.sender} in {self.group_name} at {self.timestamp}"
