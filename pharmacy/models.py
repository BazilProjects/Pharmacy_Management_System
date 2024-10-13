from django.db import models
from django.contrib.auth.models import AbstractUser
import datetime
from django.db import models
from django.contrib.auth.models import User  # Ensure you have the User model imported

# Extended User model with roles
class User(AbstractUser):
    ROLES = (('admin', 'Admin'), ('salesperson', 'Salesperson'))
    role = models.CharField(max_length=15, choices=ROLES)
    suspended = models.BooleanField(default=False)

    # Fixing the related_name clash by adding related_name to groups and user_permissions fields
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='pharmacy_user_groups',  # Add unique related_name
        blank=True,
        help_text='The groups this user belongs to.',
        verbose_name='groups',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='pharmacy_user_permissions',  # Add unique related_name
        blank=True,
        help_text='Specific permissions for this user.',
        verbose_name='user permissions',
    )


class Category(models.Model):
    name = models.CharField(max_length=100, null=True, blank=True)  # Set null=True, blank=True

    def __str__(self):
        return self.name if self.name else "Unnamed Category"  # Handle None case


class Supplier(models.Model):
    name = models.CharField(max_length=100, null=True, blank=True)  # Set null=True, blank=True
    contact = models.CharField(max_length=100, null=True, blank=True)  # Set null=True, blank=True
    email = models.EmailField(null=True, blank=True)  # Set null=True, blank=True
    date_joined = models.DateField(auto_now_add=True)  # Typically, this would remain as is

    def __str__(self):
        return self.name if self.name else "Unnamed Supplier"  # Handle None case


class Product(models.Model):
    name = models.CharField(max_length=100, null=True, blank=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, null=True, blank=True)
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE, null=True, blank=True)
    stock_quantity = models.IntegerField(null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    cost_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)  # New field
    expiry_date = models.DateField(null=True, blank=True)
    image = models.ImageField(upload_to='products/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def is_expired(self):
        return self.expiry_date < datetime.date.today()

    def __str__(self):
        return self.name



class Sale(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
    ]
    
    product = models.ForeignKey(Product, on_delete=models.CASCADE, null=True, blank=True)
    quantity = models.IntegerField(null=True, blank=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    date_of_sale = models.DateTimeField(auto_now_add=True)
    salesperson = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    order_status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='completed', null=True, blank=True)  # This should be here

    def __str__(self):
        return f"Sale of {self.product} by {self.salesperson} on {self.date_of_sale}"


class SaleReversal(models.Model):
    sale = models.ForeignKey(Sale, on_delete=models.CASCADE, null=True, blank=True)  # Set null=True, blank=True
    reason = models.TextField(null=True, blank=True)  # Set null=True, blank=True
    is_approved = models.BooleanField(default=False)
    request_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reversal_requests', null=True, blank=True)  # Set null=True, blank=True
    approved_by = models.ForeignKey(User, null=True, on_delete=models.SET_NULL, related_name='reversal_approvals', blank=True)  # Keep SET_NULL and set blank=True
    created_at = models.DateTimeField(auto_now_add=True)  # Typically, this would remain as is
