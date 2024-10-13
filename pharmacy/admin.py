# pharmacy/admin.py
from django.contrib import admin
from .models import Product, Sale, SaleReversal, Supplier, User

admin.site.register(Product)
admin.site.register(Sale)
admin.site.register(SaleReversal)
admin.site.register(Supplier)
admin.site.register(User)
