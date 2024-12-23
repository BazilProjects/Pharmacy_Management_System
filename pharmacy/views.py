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
from django.http import JsonResponse
from .models import Product
from django.http import JsonResponse
from django.contrib.auth import get_user_model

User = get_user_model()

from django.shortcuts import render, redirect
from django.http import JsonResponse
from .utils import make_paypal_payment, verify_paypal_payment

from django.http import HttpResponse
def drug_suggestions(request):
    query = request.GET.get('query', '')
    if query:
        # Filter drugs that match the query (case-insensitive)
        drugs = Product.objects.filter(name__icontains=query).values_list('name', flat=True)[:10]  # Limit to 10 results
        return JsonResponse({'suggestions': list(drugs)})
    return JsonResponse({'suggestions': []})

def submit_form(request):
    if request.method == 'POST':
        # Retrieve all products and quantities from the request
        products = request.POST.getlist('product[]')
        quantities = request.POST.getlist('quantity[]')

        # Example: Iterate over products and quantities and process each pair
        for product, quantity in zip(products, quantities):
            # Process each product and quantity (e.g., save to the database)
            print(f"Product: {product}, Quantity: {quantity}")

        # Return a success message after processing
        return HttpResponse("Form submitted successfully!")
    else:
        return HttpResponse("Invalid request. Only POST method is allowed.")

def check_drug_exists(request):
    product_name = request.GET.get('product_name')
    if Product.objects.filter(name__iexact=product_name).exists():
        return JsonResponse({'exists': True})
    else:
        return JsonResponse({'exists': False})

def product_search(request):
    if 'q' in request.GET:
        search_term = request.GET.get('q')
        products = Product.objects.filter(name__icontains=search_term, stock_quantity__gt=0)
        results = [{'id': product.id, 'text': product.name} for product in products]
        return JsonResponse(results, safe=False)
    return JsonResponse([], safe=False)

@login_required
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
        username = request.POST['username']
        password = request.POST['password']

        # Create a new user
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists.')
        else:
            user = User.objects.create_user(username=username, password=password,role='admin')
            messages.success(request, 'Account created successfully!')
            login(request, user)  # Log the user in after registration
            return redirect('subscribe')
    else:
        #form = CustomAdminSignUpForm()
        pass
    
    return render(request, 'pharmacy/register_admin.html', {})




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
            return redirect('dashboard')  # Redirect to some admin dashboard after sign-up
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
            return redirect('salesperson_dashboard')  # Redirect to salesperson's dashboard after sign-up
    else:
        form = CustomAdminSignUpForm()

    context={'form': form, 'group': group}
    return render(request, 'pharmacy/register_sales_person.html', context)


def supervising_pharmacist_signup(request, group_id):
    group = Pharmacy.objects.get(id=group_id)

    if request.method == 'POST':
        form = CustomAdminSignUpForm(request.POST)
        if form.is_valid():
            user = form.save()  # No commit argument needed now
            user.role = 'supervising_pharmacist'  # Set role as salesperson
            user.pharmacy=group  # Add the user to the specified group
            bossed_by=group.created_by
            user.save()
            login(request, user)
            group.supervised_by=user
            group.save()
            return redirect('supervising_pharmacist_dashboard')  # Redirect to salesperson's dashboard after sign-up
    else:
        form = CustomAdminSignUpForm()

    context={'form': form, 'group': group}
    return render(request, 'pharmacy/supervising_pharmacist.html', context)






@login_required
def get_today_sales_and_revenue(pharmacy):
    today = timezone.now().date()

    # Total sales (number of products sold)
    total_sales = Sale.objects.filter(date_of_sale__date=today, pharmacy=pharmacy).aggregate(total_sold=Sum('quantity'))['total_sold'] or 0

    # Total money made (sum of total_price)
    total_revenue = Sale.objects.filter(date_of_sale__date=today, pharmacy=pharmacy).aggregate(total_money_made=Sum('total_price'))['total_money_made'] or 0.00

    return total_sales, total_revenue



@login_required
def dashboard(request):
    
    # Current date and time
    today = timezone.now()

    # Calculate the first and last day of the current month
    first_day_of_month = today.replace(day=1)
    last_day_of_month = (first_day_of_month + timedelta(days=32)).replace(day=1) - timedelta(days=1)

    # Calculate the total revenue for the current month
    current_month_revenue = Sale.objects.filter(date_of_sale__range=(first_day_of_month, last_day_of_month)).aggregate(total_revenue=Sum('total_price'))['total_revenue'] or 0

    # Calculate the total gross profit for the current month
    current_month_gross_profit = SaleProduct.objects.filter(
        sale__date_of_sale__range=(first_day_of_month, last_day_of_month)
    ).annotate(
        gross_profit=F('price') * F('quantity') - F('product__cost_price') * F('quantity')
    ).aggregate(total_gross_profit=Sum('gross_profit'))['total_gross_profit'] or 0

    # Print or return the results as needed
    print(f"Current Month Revenue: {current_month_revenue}")
    print(f"Current Month Gross Profit: {current_month_gross_profit}")

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
    try:
        pharmacy = request.user.pharmacy

        total_sales, total_revenue = get_today_sales_and_revenue(pharmacy)
    except:
        total_sales, total_revenue= 0,0
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




@login_required
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


@login_required
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




@login_required
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

@login_required
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
@login_required
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
@login_required
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
                    return redirect('dashboard')
                elif user.role == 'salesperson':
                    return redirect('salesperson_dashboard')
                elif user.role == 'supervising_pharmacist':
                    return redirect('supervising_pharmacist_dashboard')
    else:
        form = CustomLoginForm()
    context={'form':form,}
    return render(request, 'pharmacy/login.html',context)

# Admin Dashboard View
@login_required
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
@login_required
def salesperson_dashboard(request):
    if request.user.role!='salesperson':
        return redirect('login')
    else:
        # Get total sales made by this salesperson
        sales = Sale.objects.filter(salesperson=request.user)
        total_sales = sales.aggregate(total=models.Sum('total_price'))['total'] or 0
        if request.method == 'POST':
            formset = SaleFormSet(request.POST)
            if formset.is_valid():
                for form in formset:
                    if form.cleaned_data:  # Check if the form has any filled data
                        # Ensure we aren't processing deleted or empty forms
                        if not form.cleaned_data.get('DELETE', False):
                            sale = form.save(commit=False)
                            # Decrease stock quantity
                            sale.product.stock_quantity -= form.cleaned_data['quantity']
                            sale.product.save()
                            sale.save()
                return redirect('success_url')  # Replace with your success page URL
        else:
            formset = SaleFormSet(queryset=Sale.objects.none()) 
        context = {
            'formset': formset,
            'sales': sales,
            'total_sales': total_sales,
        }
        return render(request, 'pharmacy/salesperson_dashboard.html', context)
# Salesperson Dashboard View
@login_required
def supervising_pharmacist_dashboard(request):
    context={}
    if request.user.role!='supervising_pharmacist':
        return redirect('login')
    else:
        # Get total sales made by this salesperson
        Pharmacies=Pharmacy.objects.all().filter(supervised_by=request.user).filter(created_by=request.user.bossed_by)
        try:
            Pharmacies1 = Pharmacy.objects.filter(supervised_by =request.user).order_by('-created_at')[0]
            from django.db.models import Q

            # Query SaleProduct where related Product has 'prescription_base' in its tags
            prescription_drugs_sold_1 = SaleProduct.objects.all().filter(products__pharmacy=Pharmacies1).filter(
                product__tags='prescription_based'
            )
            context = {
                'Pharmacies1': Pharmacies1,
                'prescription_drugs_sold_1': prescription_drugs_sold_1,
                }
            context=context | context
        except:
            pass
        try:
            Pharmacies2 = Pharmacy.objects.filter(supervised_by =request.user).order_by('-created_at')[1]
            from django.db.models import Q

            # Query SaleProduct where related Product has 'prescription_base' in its tags
            prescription_drugs_sold_2 = SaleProduct.objects.all().filter(products__pharmacy=Pharmacies2).filter(
                product__tags='prescription_based'
            )
            context = {
                'Pharmacies2': Pharmacies2,
                'prescription_drugs_sold_2': prescription_drugs_sold_2,
                }
            context=context | context
        except:
            pass
        
        
        return render(request, 'pharmacy/supervising_pharmacist_dashboard.html', context)

@login_required
def list_all_supervised_pharmacist(request):
    context={}
    if request.user.role!='supervising_pharmacist':
        return redirect('login')
    else:
        # Get total sales made by this salesperson
        Pharmacies=Pharmacy.objects.all().filter(supervised_by=request.user)

        context = {
            'Pharmacies': Pharmacies,
            }
    
        return render(request, 'pharmacy/all_supervised_pharmacies.html', context)
@login_required
def specific_supervised_pharmacist(request,bossed_by):
    context={}
    if request.user.role!='supervising_pharmacist':
        return redirect('login')
    else:
        # Get total sales made by this salesperson
        Pharmacies=Pharmacy.objects.all().filter(supervised_by=request.user)

        context = {
            'Pharmacies': Pharmacies,
            }
    
        return render(request, 'pharmacy/all_supervised_pharmacies.html', context)

# Sales Reversal Request (Salesperson)
@login_required
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
@login_required
def approve_sale_reversal(request, reversal_id):
    if request.user.role != 'admin':
        return redirect('login')

    reversal = SaleReversal.objects.get(id=reversal_id)
    reversal.is_approved = True
    reversal.approved_by = request.user
    reversal.save()
    messages.success(request, 'Reversal approved.')
    return redirect('admin_dashboard')


 


@login_required
def all_category(request):
    pharmacy=request.user.pharmacy
    print(pharmacy)
    if request.method == 'POST':
        form = CategoryForm(request.POST, request.FILES)  # Handle file upload for image
        if form.is_valid():
            category = form.save(commit=False)
            category.pharmacy=pharmacy
            category.save()
            print('saved')
            
            return redirect('all_categories')  # Redirect to a category list view or any other view
    else:
        form = CategoryForm()

    
    drugs=Category.objects.all().filter(pharmacy=pharmacy)# (Category,pharmacy=pharmacy)  # Fetch the group using the group_id from the URL
    print(drugs)
    context={
            'drugs': drugs,
            'form': form
            }
    if request.user.role=='salesperson':
        
        return render(request, 'pharmacy/all_category_sales.html',context)
    else:
        return render(request, 'pharmacy/all_category.html',context)
@login_required
def add_category(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST, request.FILES)  # Handle file upload for image
        if form.is_valid():
            category = form.save(commit=False)
            category.save()
            return redirect('all_categories')  # Redirect to a category list view or any other view
    else:
        form = CategoryForm()
    
    context = {'form': form}
    return render(request, 'pharmacy/add_category.html', context)
    
# Edit Category (Admin)
##@user_passes_test(is_admin)
@login_required
def edit_category(request, id):
    category = Category.objects.get(id=id)
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
@login_required
def delete_category(request, category_id):
    category = Category.objects.get(id=category_id)
    category.delete()
    return redirect('all_drugs')







@login_required
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

@login_required
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
@login_required
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
@login_required
def delete_sales(request, sales_id):
    sales = Sale.objects.get(id=sales_id)
    sales.delete()
    return redirect('all_drugs')







@login_required
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

@login_required
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
@login_required
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
@login_required
def delete_supplier(request, supplier_id):
    supplier = Supplier.objects.get(id=supplier_id)
    supplier.delete()
    return redirect('all_drugs')




@login_required
def revoke_sale(request, id):
    if request.user.role != 'supervising_pharmacist':
        return redirect('login')
    revoked = Product.objects.get(id=id)
    revoked.allow_sale=False
    revoked.save()
    return redirect('all_drugs')


@login_required
def allow_sale(request, id):
    if request.user.role != 'supervising_pharmacist':
        return redirect('login')
    allowed= Product.objects.get(id=id)
    allowed.allow_sale=True
    allowed.save()
    return redirect('all_drugs')


@login_required
def revoke_license(request, id):
    if request.user.role != 'supervising_pharmacist':
        return redirect('login')
    revoked = Supplier.objects.get(id=id)
    revoked.is_approved=False
    revoked.save()
    return redirect('all_drugs')


@login_required
def allow_license(request, id):
    if request.user.role != 'supervising_pharmacist':
        return redirect('login')
    allowed= Supplier.objects.get(id=id)
    allowed.is_approved=True
    allowed.save()
    return redirect('all_drugs')





@login_required
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
    if request.user.role in ['admin', 'manager', 'supervising_pharmacist']:
        return render(request, 'pharmacy/all_drugs.html',context)
    if request.user.role=='salesperson':
        return render(request, 'pharmacy/all_drugs_sales.html',context)
 
@login_required
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
    if request.user.role=='salesperson':
        return render(request, 'pharmacy/add_product_sales.html', context)
    else:
        return render(request, 'pharmacy/add_product.html', context)


# Edit Product (Admin)
##@user_passes_test(is_admin)
@login_required
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
@login_required
def delete_product(request, product_id):
    product = Product.objects.get(id=product_id)
    product.delete()
    return redirect('all_drugs')



from django.contrib.auth.decorators import user_passes_test

# Check if the user is admin
@login_required
def is_admin(user):
    return user.is_authenticated and user.role == 'admin'

# Check if the user is salesperson
@login_required
def is_salesperson(user):
    return user.is_authenticated and user.role == 'salesperson'

# Admin Dashboard
#@user_passes_test(is_admin)
@login_required
def admin_dashboard(request):
    # Admin functionality here...
    return render(request, 'pharmacy/admin_dashboard.html')

# Salesperson Dashboard
#@user_passes_test(is_salesperson)



# List of Sales (Admin)
#@user_passes_test(is_admin)
@login_required
def list_sales(request):
    sales = Sale.objects.all()
    return render(request, 'pharmacy/list_sales.html', {'sales': sales})

# Request Sale Reversal (Admin)
#@user_passes_test(is_admin)
@login_required
def request_sale_reversal(request, sale_id):
    sale = Sale.objects.get(id=sale_id)
    if request.method == 'POST':
        reason = request.POST['reason']
        SaleReversal.objects.create(sale=sale, reason=reason, reversed_by=request.user)
        return redirect('list_sales')
    return render(request, 'pharmacy/request_sale_reversal.html', {'sale': sale})

# Approve Sale Reversal (Admin)
#@user_passes_test(is_admin)
@login_required
def approve_reversal(request, reversal_id):
    reversal = SaleReversal.objects.get(id=reversal_id)
    reversal.is_approved = True
    reversal.save()
    # Optionally, you could restock the reversed products here.
    return redirect('list_sales')



#@user_passes_test(is_admin)
@login_required
def sales_report(request):
    # Filter sales by date or month
    sales = Sale.objects.all()
    return render(request, 'pharmacy/sales_report.html', {'sales': sales})


def about_us(request):
    return render(request, 'pharmacy/about_us.html')



def home(request):
    return render(request, 'pharmacy/home.html')


def financial_statement(request):
    return render(request, 'pharmacy/financial_statement.html')

def cashier_dashboard(request):
    return render(request, 'pharmacy/cashier_dashboard.html')

def billing(request):
    return render(request, 'pharmacy/billing.html')
@login_required
def subscribe(request):
    return render(request, 'pharmacy/subscribe.html')
from django.contrib.auth.forms import UserCreationForm
@login_required
def profile(request):
    user= User.objects.get(username=request.user.username) 
    print(user)
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=user)
        if form.is_valid():

            form.save()
            print('Profile Saved')
            return redirect('profile')
    else:
        form = ProfileForm(instance=user)
    context={'form':form,'user':user}
    return render(request, 'pharmacy/profile.html',context)

def contact_us(request):
    if request.method=='POST':
        try:
            subject = "Contact LECZ-PharmaSuite(LPS) Support/Sales"
            message = request.POST.get('message')
            name = request.POST.get('name')
            email = request.POST.get('email')
            print(message)
            message=f'{message}............\nreply to {email}\nBy name {name}'
            try:
                send_mail(
                    subject,
                    message,
                    settings.EMAIL_HOST_USER,
                    ['pearljob@gmail.com', 'pearlvibe@gmail.com'],
                    fail_silently=False,
                )
                send_mail(
                    subject,
                    f'Dear {name},\n Your message has been received successfully. We will be contacting you soon! Have a lovely day',
                    settings.EMAIL_HOST_USER,
                    [f'{email}'],
                    fail_silently=False,
                )
            except Exception as e:
                print(f"Error sending mail: {e}")

            messages.success(request, f'We have recived your message, You will recive and email confirming it soon, Have a lovely day')
            return redirect('/')
        except:
            messages.success(request, f'Dear {name},\n Sorry But there may be an error in the System, \n Please Contact me on pearljob@gmail.com')
            return redirect('/')
    context={}
    return render(request,'pharmacy/contact_us.html',context)


from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa

def generate_pdf_view(request):
    template_path = 'pharmacy/receipt.html'  # Create this template with your receipt design
    context = {
        'products': [
            {'name': 'Product 1', 'quantity': 2, 'price': 50},
            {'name': 'Product 2', 'quantity': 1, 'price': 100},
        ],
        'total': 200,
        'date': '2024-10-21',
    }

    # Load the HTML template
    template = get_template(template_path)
    html = template.render(context)

    # Create a PDF object
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'inline; filename="receipt.pdf"'

    # Convert HTML to PDF
    pisa_status = pisa.CreatePDF(html, dest=response)

    if pisa_status.err:
        return HttpResponse('We had some errors with the PDF generation <pre>' + html + '</pre>')
    return response





def create_payment(request,amount):
    if request.method == 'POST':
        amount = amount  # $20 for example
        success, payment_id, approval_url = make_paypal_payment(
            amount=amount,
            currency="USD",
            return_url="http://localhost:8000/paypal/success/",
            cancel_url="http://localhost:8000/paypal/cancel/"
        )

        if success:
            # Redirect to PayPal approval URL
            return redirect(approval_url)
        else:
            return JsonResponse({'success': False, 'message': 'Payment creation failed'})
    
    #return render(request, 'payments/create_payment.html')


def success_payment(request):
    payment_id = request.GET.get('paymentId')
    if verify_paypal_payment(payment_id):
        return JsonResponse({'success': True, 'message': 'Payment successful'})
    else:
        return JsonResponse({'success': False, 'message': 'Payment verification failed'})

def cancel_payment(request):
    return JsonResponse({'success': False, 'message': 'Payment cancelled'})






















from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def private_chat(request, username):
    return render(request, 'pharmacy/chat/private_chat.html', {
        'other_user': username,
    })

@login_required
def group_chat(request, group_name):
    return render(request, 'pharmacy/chat/group_chat.html', {
        'group_name': group_name,
    })
