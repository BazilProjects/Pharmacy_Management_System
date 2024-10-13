from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from .models import Product, Sale, User, SaleReversal
import datetime
from django.contrib import messages

from django.shortcuts import render
from .models import Sale, Product
from django.utils import timezone
from datetime import timedelta
from django.db.models import Sum, F

def index(request):
    today = timezone.now()
    first_day_of_month = today.replace(day=1)
    last_day_of_month = (first_day_of_month + timedelta(days=32)).replace(day=1) - timedelta(days=1)

    current_month_revenue = Sale.objects.filter(date_of_sale__range=(first_day_of_month, last_day_of_month)).aggregate(total_revenue=Sum('total_price'))['total_revenue'] or int(0)
    current_month_gross_profit = Sale.objects.filter(date_of_sale__range=(first_day_of_month, last_day_of_month)).annotate(
        gross_profit=F('total_price') - F('product__cost_price')
    ).aggregate(total_gross_profit=Sum('gross_profit'))['total_gross_profit'] or int(0)
    fixed_expenses = 200  # Example fixed expenses for the month
    current_month_net_profit = current_month_gross_profit - fixed_expenses

    pending_orders_count = Sale.objects.filter(order_status='pending').count()
    expired_drugs_count = Product.objects.filter(expiry_date__lt=today.date()).count()
    total_antivirals = Product.objects.filter(category__name='Antivirals').count()
    total_antibacterials = Product.objects.filter(category__name='Antibacterials').count()
    total_antifungals = Product.objects.filter(category__name='Antifungals').count()
    
    context = {
        'current_month_revenue': current_month_revenue,
        'current_month_gross_profit': current_month_gross_profit,
        'current_month_net_profit': current_month_net_profit,
        'pending_orders_count': pending_orders_count,
        'expired_drugs_count': expired_drugs_count,
        'total_antivirals': total_antivirals,
        'total_antibacterials': total_antibacterials,
        'total_antifungals': total_antifungals,
    }


    return render(request, 'pharmacy/index.html',context)


# Login View
def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user and not user.suspended:
            login(request, user)
            if user.role == 'admin':
                return redirect('admin_dashboard')
            elif user.role == 'salesperson':
                return redirect('salesperson_dashboard')
    return render(request, 'pharmacy/login.html')

# Admin Dashboard View
def admin_dashboard(request):
    if request.user.role != 'admin':
        return redirect('login')

    # Data to show on admin dashboard
    products = Product.objects.all()
    sales = Sale.objects.all()
    low_stock_products = Product.objects.filter(stock_quantity__lt=10)
    expired_products = Product.objects.filter(expiry_date__lt=datetime.date.today())
    salespersons = User.objects.filter(role='salesperson')

    # Calculate total sales per salesperson
    sales_data = {}
    for sp in salespersons:
        sales_total = Sale.objects.filter(salesperson=sp).aggregate(total=models.Sum('total_price'))['total']
        sales_data[sp.username] = sales_total or 0

    # Expired drugs notification
    expired_notification = expired_products.count() > 0

    context = {
        'products': products,
        'sales': sales,
        'low_stock_products': low_stock_products,
        'expired_products': expired_products,
        'sales_data': sales_data,
        'expired_notification': expired_notification,
    }
    return render(request, 'pharmacy/admin_dashboard.html', context)

# Salesperson Dashboard View
def salesperson_dashboard(request):
    if request.user.role != 'salesperson':
        return redirect('login')

    # Get total sales made by this salesperson
    sales = Sale.objects.filter(salesperson=request.user)
    total_sales = sales.aggregate(total=models.Sum('total_price'))['total'] or 0

    context = {
        'sales': sales,
        'total_sales': total_sales,
    }
    return render(request, 'pharmacy/salesperson_dashboard.html', context)

# Sales Reversal Request (Salesperson)
def request_sale_reversal(request, sale_id):
    if request.user.role != 'salesperson':
        return redirect('login')

    sale = Sale.objects.get(id=sale_id)
    if request.method == 'POST':
        reason = request.POST['reason']
        SaleReversal.objects.create(sale=sale, reason=reason, request_by=request.user)
        messages.success(request, 'Reversal request sent.')
        return redirect('salesperson_dashboard')

    context = {'sale': sale}
    return render(request, 'pharmacy/request_reversal.html', context)

# Approve Sale Reversal (Admin)
def approve_sale_reversal(request, reversal_id):
    if request.user.role != 'admin':
        return redirect('login')

    reversal = SaleReversal.objects.get(id=reversal_id)
    reversal.is_approved = True
    reversal.approved_by = request.user
    reversal.save()
    messages.success(request, 'Reversal approved.')
    return redirect('admin_dashboard')



# Add Product (Admin)
#user_passes_test(is_admin)
def add_product(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('admin_dashboard')
    else:
        form = ProductForm()
    return render(request, 'pharmacy/add_product.html', {'form': form})

# Edit Product (Admin)
##@user_passes_test(is_admin)
def edit_product(request, product_id):
    product = Product.objects.get(id=product_id)
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            return redirect('admin_dashboard')
    else:
        form = ProductForm(instance=product)
    return render(request, 'pharmacy/edit_product.html', {'form': form})

# Delete Product (Admin)
##@user_passes_test(is_admin)
def delete_product(request, product_id):
    product = Product.objects.get(id=product_id)
    product.delete()
    return redirect('admin_dashboard')



from django.contrib.auth.decorators import user_passes_test

# Check if the user is admin
def is_admin(user):
    return user.is_authenticated and user.role == 'admin'

# Check if the user is salesperson
def is_salesperson(user):
    return user.is_authenticated and user.role == 'salesperson'

# Admin Dashboard
#@user_passes_test(is_admin)
def admin_dashboard(request):
    # Admin functionality here...
    return render(request, 'pharmacy/admin_dashboard.html')

# Salesperson Dashboard
#@user_passes_test(is_salesperson)
def salesperson_dashboard(request):
    # Salesperson functionality here...
    return render(request, 'pharmacy/salesperson_dashboard.html')



from .forms import SaleForm

#@user_passes_test(is_salesperson)
def process_sale(request):
    if request.method == 'POST':
        form = SaleForm(request.POST)
        if form.is_valid():
            sale = form.save(commit=False)
            sale.salesperson = request.user
            sale.total_price = sale.quantity * sale.product.price
            sale.save()
            return redirect('salesperson_dashboard')
    else:
        form = SaleForm()
    return render(request, 'pharmacy/process_sale.html', {'form': form})


# List of Sales (Admin)
#@user_passes_test(is_admin)
def list_sales(request):
    sales = Sale.objects.all()
    return render(request, 'pharmacy/list_sales.html', {'sales': sales})

# Request Sale Reversal (Admin)
#@user_passes_test(is_admin)
def request_sale_reversal(request, sale_id):
    sale = Sale.objects.get(id=sale_id)
    if request.method == 'POST':
        reason = request.POST['reason']
        SaleReversal.objects.create(sale=sale, reason=reason, reversed_by=request.user)
        return redirect('list_sales')
    return render(request, 'pharmacy/request_sale_reversal.html', {'sale': sale})

# Approve Sale Reversal (Admin)
#@user_passes_test(is_admin)
def approve_reversal(request, reversal_id):
    reversal = SaleReversal.objects.get(id=reversal_id)
    reversal.is_approved = True
    reversal.save()
    # Optionally, you could restock the reversed products here.
    return redirect('list_sales')


#@user_passes_test(is_admin)
def add_supplier(request):
    if request.method == 'POST':
        name = request.POST['name']
        contact = request.POST['contact']
        email = request.POST['email']
        Supplier.objects.create(name=name, contact=contact, email=email)
        return redirect('admin_dashboard')
    return render(request, 'pharmacy/add_supplier.html')

#@user_passes_test(is_admin)
def list_suppliers(request):
    suppliers = Supplier.objects.all()
    return render(request, 'pharmacy/list_suppliers.html', {'suppliers': suppliers})


#@user_passes_test(is_admin)
def sales_report(request):
    # Filter sales by date or month
    sales = Sale.objects.all()
    return render(request, 'pharmacy/sales_report.html', {'sales': sales})
