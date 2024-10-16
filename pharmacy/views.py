from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from .models import Product, Sale, User, SaleReversal
import datetime
from django.contrib import messages
from .models import *
from .forms import *
from django.shortcuts import render
from .models import Sale, Product
from django.utils import timezone
from datetime import timedelta
from django.db.models import Sum, F
from django.utils import timezone
from django.shortcuts import render, redirect
from .forms import CustomAdminSignUpForm
from django.contrib.auth import login
from .models import User
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from .models import User, Group
# views.py
from django.contrib.auth.decorators import login_required
from .forms import ProductForm
from django.http import JsonResponse

def sales_data(request):
    sales_per_day = Sale.objects.values('date_of_sale').annotate(total_sales=Sum('total_price'))
    
    # Format the data as JSON
    sales_data = {
        "labels": [entry['date_of_sale'].strftime('%b %d') for entry in sales_per_day],  # e.g., 'Oct 12'
        "data": [entry['total_sales'] for entry in sales_per_day]
    }
    
    return JsonResponse(sales_data)

def admin_signup(request):
    if request.method == 'POST':
        form = CustomAdminSignUpForm(request.POST)
        if form.is_valid():
            user = form.save()  # No commit argument needed now
            user.role = 'admin'  # Assign the role from the URL parameter
            user.save()
            login(request, user)  # Log the user in after registration
            return redirect('index')  # Redirect to some admin dashboard after sign-up
    else:
        form = CustomAdminSignUpForm()
    
    return render(request, 'pharmacy/register_admin.html', {'form': form})



def manager_signup(request,group_id):
    
    group =get_object_or_404(Pharmacy, id=group_id)  # Fetch the group using the group_id from the URL

    if request.method == 'POST':
        form = CustomAdminSignUpForm(request.POST)
        if form.is_valid():
            user = form.save()  # No commit argument needed now
            user.role = 'manager'  # Assign the role from the URL parameter
            user.pharmacy=group
            user.save()
            login(request, user)  # Log the user in after registration
            return redirect('index')  # Redirect to some admin dashboard after sign-up
    else:
        form = CustomAdminSignUpForm()
        context={
                'form': form, 
                'group': group,
                }

        return render(request, 'pharmacy/register_manager.html',context)
'''
<a href="{% url 'manager_signup' group_id=1 %}">Sign Up as Manager for Group 1</a>
<a href="{% url 'salesperson_signup' group_id=2 %}">Sign Up as Salesperson for Group 2</a>
'''

def salesperson_signup(request, group_id):
    group = get_object_or_404(Pharmacy, id=group_id)  # Fetch the group using the group_id from the URL

    if request.method == 'POST':
        form = CustomAdminSignUpForm(request.POST)
        if form.is_valid():
            user = form.save()  # No commit argument needed now
            user.role = 'salesperson'  # Set role as salesperson
            user.pharmacy=group  # Add the user to the specified group
            user.save() 
            login(request, user)
            return redirect('index')  # Redirect to salesperson's dashboard after sign-up
    else:
        form = CustomAdminSignUpForm()

    context={'form': form, 'group': group}
    return render(request, 'pharmacy/register_sales_person.html', context)






def get_today_sales_and_revenue(pharmacy):
    today = timezone.now().date()

    # Total sales (number of products sold)
    total_sales = Sale.objects.filter(date_of_sale__date=today, pharmacy=pharmacy).aggregate(total_sold=Sum('quantity'))['total_sold'] or 0

    # Total money made (sum of total_price)
    total_revenue = Sale.objects.filter(date_of_sale__date=today, pharmacy=pharmacy).aggregate(total_money_made=Sum('total_price'))['total_money_made'] or 0.00

    return total_sales, total_revenue


@login_required
def index(request):
    today = timezone.now()
    first_day_of_month = today.replace(day=1)
    last_day_of_month = (first_day_of_month + timedelta(days=32)).replace(day=1) - timedelta(days=1)

    current_month_revenue = Sale.objects.filter(date_of_sale__range=(first_day_of_month, last_day_of_month)).aggregate(total_revenue=Sum('total_price'))['total_revenue'] or int(0)
    current_month_gross_profit = Sale.objects.filter(date_of_sale__range=(first_day_of_month, last_day_of_month)).annotate(
        gross_profit=F('total_price') - F('product__cost_price')
    ).aggregate(total_gross_profit=Sum('gross_profit'))['total_gross_profit'] or int(0)
    fixed_expenses = 0  # Example fixed expenses for the month
    current_month_net_profit = current_month_gross_profit - fixed_expenses

    pending_orders_count = Sale.objects.filter(order_status='pending').count()
    expired_drugs_count = Product.objects.filter(expiry_date__lt=today.date()).count()
    total_antivirals = Product.objects.filter(category__name='Antivirals').count()
    total_antibacterials = Product.objects.filter(category__name='Antibacterials').count()
    total_antifungals = Product.objects.filter(category__name='Antifungals').count()
    # Retrieve all Sale objects


    sales = Sale.objects.all().filter(date_of_sale =today)  # Get all sales
    sales_count = sales.count()  # Get the total count of sales

    total_sales_price = sales.aggregate(Sum('total_price'))['total_price__sum'] or 0
    pharmacy = request.user.pharmacy

    total_sales, total_revenue = get_today_sales_and_revenue(pharmacy)
    context={
        'total_sales': total_sales,
        'total_sales_price':total_sales_price,
        'total_revenue': total_revenue,
        'sales': sales,          # Pass the sales queryset to the template
        'sales_count': sales_count,  ## Sale.objects.filter(product__pharmacy=request.user.pharmacy)

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




def create_pharmacy(request):
    if request.user.role == 'admin':
        if request.method == 'POST':
            form = PharmacyForm(request.POST)
            if form.is_valid():
                form.save()
                return redirect('pharmacy_list')
        else:
            form = PharmacyForm()
        return render(request, 'pharmacy/create_pharmacy.html', {'form': form})
    else:
        return redirect('no_permission')  # Salesperson shouldn't be able to create a pharmacy


def all_sales_person(request):
    pharmacies = Pharmacy.objects.filter(created_by=request.user)

    # Step 2: Initialize a list to hold the results
    results = []

    # Step 3: Loop through each pharmacy and filter users
    for pharmacy in pharmacies:
        # Get users with role 'sole' associated with the pharmacy
        users = User.objects.filter(role='sole', pharmacy=pharmacy)

        # Combine the pharmacy with its users
        results.append({
            'pharmacy': pharmacy,
            'users': users
        })# (Pharmacys,pharmacy=pharmacy)  # Fetch the group using the group_id from the URL
    context={
            'results': results
            }

    return render(request, 'pharmacy/all_sales_person.html',context)

def all_pharmacy(request):
    #pharmacy=request.user.pharmacy
    if request.method == 'POST':
        form = PharmacyForm(request.POST, request.FILES)  # Handle file upload for image
        if form.is_valid():
            pharmacy = form.save(commit=False)
            pharmacy.created_by=request.user
            pharmacy.save()
            return redirect('all_pharmacy')  # Redirect to a pharmacy list view or any other view
    else:
        form = PharmacyForm()

    
    pharmacys=Pharmacy.objects.all().filter(created_by=request.user)# (Pharmacys,pharmacy=pharmacy)  # Fetch the group using the group_id from the URL
    context={
            'pharmacys': pharmacys,
            'form': form
            }

    return render(request, 'pharmacy/all_pharmacy.html',context)

def add_pharmacy(request):
    if request.method == 'POST':
        form = PharmacyForm(request.POST, request.FILES)  # Handle file upload for image
        if form.is_valid():
            pharmacy = form.save(commit=False)
            pharmacy.created_by=request.user
            pharmacy.save()
            return redirect('all_pharmacy')  # Redirect to a pharmacy list view or any other view
    else:
        form = PharmacyForm()
    
    context = {'form': form}
    return render(request, 'pharmacy/add_pharmacy.html', context)


# Edit Pharmacys (Admin)
##@user_passes_test(is_admin)
def edit_pharmacy(request, pharmacy_id):
    pharmacy = Pharmacy.objects.get(id=pharmacy_id)
    if request.method == 'POST':
        form = PharmacyForm(request.POST, request.FILES, instance=pharmacy)
        if form.is_valid():
            form.save()
            return redirect('all_drugs')
    else:
        form = PharmacyForm(instance=pharmacy)
    return render(request, 'pharmacy/add_product.html', {'form': form, 'product':'Pharmacy Store'})

# Delete Pharmacys (Admin)
##@user_passes_test(is_admin)
def delete_pharmacy(request, pharmacy_id):
    pharmacy = Pharmacy.objects.get(id=pharmacy_id)
    pharmacy.delete()
    return redirect('all_pharmacy')



# Login View
def login_view(request):
    if request.method == 'POST':
        form = CustomLoginForm(data=request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user and not user.suspended:
                login(request, user)
                if user.role == 'admin':
                    return redirect('/')
                elif user.role == 'salesperson':
                    return redirect('/')
                else:
                    return redirect('/')
    else:
        form = CustomLoginForm()
    context={'form':form,}
    return render(request, 'pharmacy/login.html',context)

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





def all_category(request):
    pharmacy=request.user.pharmacy
    if request.method == 'POST':
        form = CategoryForm(request.POST, request.FILES)  # Handle file upload for image
        if form.is_valid():
            category = form.save(commit=False)
            category.pharmacy=pharmacy
            category.save()
            return redirect('category_list')  # Redirect to a category list view or any other view
    else:
        form = CategoryForm()

    
    drugs=Category.objects.all().filter(pharmacy=pharmacy)# (Category,pharmacy=pharmacy)  # Fetch the group using the group_id from the URL
    context={
            'drugs': drugs,
            'form': form
            }

    return render(request, 'pharmacy/all_category.html',context)

def add_category(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST, request.FILES)  # Handle file upload for image
        if form.is_valid():
            category = form.save(commit=False)
            category.save()
            return redirect('category_list')  # Redirect to a category list view or any other view
    else:
        form = CategoryForm()
    
    context = {'form': form}
    return render(request, 'pharmacy/add_category.html', context)


# Edit Category (Admin)
##@user_passes_test(is_admin)
def edit_category(request, category_id):
    category = Category.objects.get(id=category_id)
    if request.method == 'POST':
        form = CategoryForm(request.POST, request.FILES, instance=category)
        if form.is_valid():
            form.save()
            return redirect('all_drugs')
    else:
        form = CategoryForm(instance=category)
    return render(request, 'pharmacy/add_category.html', {'form': form})

# Delete Category (Admin)
##@user_passes_test(is_admin)
def delete_category(request, category_id):
    category = Category.objects.get(id=category_id)
    category.delete()
    return redirect('all_drugs')







def all_sales(request):
    pharmacy=request.user.pharmacy
    if request.method == 'POST':
        form = SaleForm(request.POST, request.FILES)  # Handle file upload for image
        if form.is_valid():
            sales = form.save(commit=False)
            sales.pharmacy=pharmacy
            sales.save()
            return redirect('sales_list')  # Redirect to a sales list view or any other view
    else:
        form = SaleForm()

    
    drugs=Sale.objects.all().filter(pharmacy=pharmacy)# (Sales,pharmacy=pharmacy)  # Fetch the group using the group_id from the URL
    context={
            'drugs': drugs,
            'form': form
            }

    return render(request, 'pharmacy/all_sales.html',context)

def add_sales(request):
    if request.method == 'POST':
        form = SaleForm(request.POST, request.FILES)  # Handle file upload for image
        if form.is_valid():
            sales = form.save(commit=False)
            sales.save()
            return redirect('sales_list')  # Redirect to a sales list view or any other view
    else:
        form = SaleForm()
    
    context = {'form': form}
    return render(request, 'pharmacy/add_sales.html', context)


# Edit Sales (Admin)
##@user_passes_test(is_admin)
def edit_sales(request, sales_id):
    sales = Sale.objects.get(id=sales_id)
    if request.method == 'POST':
        form = SaleForm(request.POST, request.FILES, instance=sales)
        if form.is_valid():
            form.save()
            return redirect('all_drugs')
    else:
        form = SalesForm(instance=sales)
    return render(request, 'pharmacy/add_sales.html', {'form': form})

# Delete Sales (Admin)
##@user_passes_test(is_admin)
def delete_sales(request, sales_id):
    sales = Sale.objects.get(id=sales_id)
    sales.delete()
    return redirect('all_drugs')







def all_supplier(request):
    pharmacy=request.user.pharmacy
    if request.method == 'POST':
        form = SupplierForm(request.POST, request.FILES)  # Handle file upload for image
        if form.is_valid():
            supplier = form.save(commit=False)
            supplier.pharmacy=pharmacy
            supplier.save()
            return redirect('supplier_list')  # Redirect to a supplier list view or any other view
    else:
        form = SupplierForm()

    
    drugs=Supplier.objects.all().filter(pharmacy=pharmacy)# (Supplier,pharmacy=pharmacy)  # Fetch the group using the group_id from the URL
    context={
            'drugs': drugs,
            'form': form
            }

    return render(request, 'pharmacy/all_supplier.html',context)

def add_supplier(request):
    if request.method == 'POST':
        form = SupplierForm(request.POST, request.FILES)  # Handle file upload for image
        if form.is_valid():
            supplier = form.save(commit=False)
            supplier.save()
            return redirect('supplier_list')  # Redirect to a supplier list view or any other view
    else:
        form = SupplierForm()
    
    context = {'form': form}
    return render(request, 'pharmacy/add_supplier.html', context)


# Edit Supplier (Admin)
##@user_passes_test(is_admin)
def edit_supplier(request, supplier_id):
    supplier = Supplier.objects.get(id=supplier_id)
    if request.method == 'POST':
        form = SupplierForm(request.POST, request.FILES, instance=supplier)
        if form.is_valid():
            form.save()
            return redirect('all_drugs')
    else:
        form = SupplierForm(instance=supplier)
    return render(request, 'pharmacy/add_supplier.html', {'form': form})

# Delete Supplier (Admin)
##@user_passes_test(is_admin)
def delete_supplier(request, supplier_id):
    supplier = Supplier.objects.get(id=supplier_id)
    supplier.delete()
    return redirect('all_drugs')









def all_products(request):
    pharmacy=request.user.pharmacy
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)  # Handle file upload for image
        if form.is_valid():
            product = form.save(commit=False)
            product.save()
            return redirect('product_list')  # Redirect to a product list view or any other view
    else:
        form = ProductForm()

    
    drugs=Product.objects.all().filter(pharmacy=pharmacy)# (Product,pharmacy=pharmacy)  # Fetch the group using the group_id from the URL
    context={
            'drugs': drugs,
            'form': form
            }

    return render(request, 'pharmacy/all_drugs.html',context)

def add_product(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)  # Handle file upload for image
        if form.is_valid():
            product = form.save(commit=False)
            product.save()
            return redirect('product_list')  # Redirect to a product list view or any other view
    else:
        form = ProductForm()
    
    context = {'form': form}
    return render(request, 'pharmacy/add_product.html', context)


# Edit Product (Admin)
##@user_passes_test(is_admin)
def edit_product(request, product_id):
    product = Product.objects.get(id=product_id)
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            return redirect('all_drugs')
    else:
        form = ProductForm(instance=product)
    return render(request, 'pharmacy/add_product.html', {'form': form})

# Delete Product (Admin)
##@user_passes_test(is_admin)
def delete_product(request, product_id):
    product = Product.objects.get(id=product_id)
    product.delete()
    return redirect('all_drugs')



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
def sales_report(request):
    # Filter sales by date or month
    sales = Sale.objects.all()
    return render(request, 'pharmacy/sales_report.html', {'sales': sales})

def about_us(request):
    return render(request, 'pharmacy/about_us.html')

def financial_statement(request):
    return render(request, 'pharmacy/financial_statement.html')

