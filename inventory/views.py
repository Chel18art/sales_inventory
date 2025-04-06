from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login
from .models import Item, Category, Sale, UserProfile
from django.db.models import Sum
from django.contrib.auth.models import User
from .forms import UserForm, ItemForm
from django.http import JsonResponse
import datetime

def user_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        
        # Authenticate the user
        user = authenticate(username=username, password=password)
        
        if user is not None:
            login(request, user)  # Log the user in
            
            # Check if the user has a UserProfile
            if hasattr(user, 'userprofile'):
                # Redirect based on account type (Admin or Cashier)
                if user.userprofile.account_type == 'Admin':
                    return redirect('admin_dashboard')  # Redirect to admin dashboard
                else:
                    return redirect('cashier_pos')  # Redirect to cashier POS dashboard
            else:
                # If the user does not have a userprofile, create one (optional)
                UserProfile.objects.create(user=user, account_type='Cashier')  # Default to 'Cashier'
                return redirect('cashier_pos')  # Redirect to cashier POS dashboard

        else:
            # If authentication fails
            return render(request, 'inventory/login.html', {'error': 'Invalid credentials'})
    
    return render(request, 'inventory/login.html')  # For GET request

def homepage(request):
    return redirect('user_login')

@login_required
def inventory_management(request):
    # Logic to retrieve inventory items
    items = Item.objects.all()
    return render(request, 'inventory/inventory_management.html', {'items': items})

@login_required
def admin_dashboard(request):
    # Query the sales data, ensuring the correct field name is used
    sales_data = Sale.objects.all().order_by('total_price')  # Corrected ordering
    return render(request, 'inventory/admin_dashboard.html', {'sales_data': sales_data})

@login_required
def inventory_view(request):
    items = Item.objects.all()
    return render(request, 'inventory/inventory_view.html', {'items': items})

@login_required
def sales_report(request):
    # Get the period query parameter (e.g., 'today', 'week', etc.)
    period = request.GET.get('period', 'today')
    
    today = datetime.date.today()

    if period == 'today':
        sales_data = Sale.objects.filter(date=today)
    elif period == 'week':
        sales_data = Sale.objects.filter(date__gte=today - datetime.timedelta(days=7))
    elif period == 'month':
        sales_data = Sale.objects.filter(date__month=today.month)
    elif period == 'year':
        sales_data = Sale.objects.filter(date__year=today.year)

    total_sales = sum(sale.total for sale in sales_data)

    return render(request, 'inventory/sales_report.html', {
        'selected_period': period.capitalize(),
        'sales_data': sales_data,
        'total_sales': total_sales,
        'today': today.strftime('%Y-%m-%d'),
    })

@login_required
def add_item(request):
    if request.method == 'POST':
        form = ItemForm(request.POST)
        if form.is_valid():
            form.save()  # Save the item to the database
            return redirect('inventory_management')  # Redirect after successful form submission
    else:
        form = ItemForm()

    return render(request, 'inventory/add_item.html', {'form': form})

def cashier_pos(request):
    return render(request, 'inventory/cashier_pos.html')

def category_management(request):
    if request.method == 'POST' and 'category_name' in request.POST and 'edit_id' not in request.POST:
        category_name = request.POST.get('category_name')
        if category_name:
            Category.objects.create(name=category_name)
        return redirect('category_management')

    if request.method == 'POST' and 'edit_id' in request.POST:
        category_id = request.POST.get('edit_id')
        category_name = request.POST.get('category_name')
        if category_name:
            category = get_object_or_404(Category, id=category_id)
            category.name = category_name
            category.save()
        return redirect('category_management')

    if request.method == 'GET' and 'delete_id' in request.GET:
        category_id = request.GET.get('delete_id')
        category = get_object_or_404(Category, id=category_id)
        category.delete()
        return redirect('category_management')

    categories = Category.objects.all()
    return render(request, 'inventory/category_management.html', {'categories': categories})

@login_required
def user_management(request):
    if request.method == 'POST':
        form = UserForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('user_management')
    else:
        form = UserForm()

    users = User.objects.all()
    return render(request, 'inventory/user_management.html', {'form': form, 'users': users})

def update_item(request, item_id):
    item = get_object_or_404(Item, pk=item_id)
    if request.method == 'POST':
        form = ItemForm(request.POST, instance=item)
        if form.is_valid():
            form.save()
            return redirect('inventory_management')
    else:
        form = ItemForm(instance=item)
    
    return render(request, 'inventory/update_item.html', {'form': form, 'item': item})

def delete_item(request, id):
    item = get_object_or_404(Item, id=id)
    item.delete()
    return redirect('inventory_management')

def item_autocomplete(request):
    query = request.GET.get('term', '')
    items = Item.objects.filter(name__icontains=query).values('name', 'id')
    return JsonResponse(list(items), safe=False)

def add_to_cart(request):
    item_name = request.POST.get('item_name')
    quantity = int(request.POST.get('quantity'))

    try:
        item = Item.objects.get(name=item_name)
    except Item.DoesNotExist:
        return JsonResponse({'error': 'Item not found'})

    subtotal = item.price * quantity

    cart_item = {
        'item': item.name,
        'quantity': quantity,
        'price': item.price,
        'subtotal': subtotal
    }

    if 'cart' not in request.session:
        request.session['cart'] = []

    request.session['cart'].append(cart_item)
    request.session.modified = True

    return JsonResponse({'message': 'Item added to cart', 'cart': request.session['cart']})

def checkout(request):
    if request.method == "POST":
        payment_received = float(request.POST.get('payment_received'))
        cart = request.session.get('cart', [])
        total_amount = sum(item['subtotal'] for item in cart)

        if payment_received < total_amount:
            return JsonResponse({'error': 'Insufficient funds'})

        for cart_item in cart:
            item = Item.objects.get(name=cart_item['item'])
            Sale.objects.create(
                item=item,
                quantity=cart_item['quantity'],
                total_price=cart_item['subtotal']
            )

        request.session['cart'] = []
        request.session.modified = True

        change = payment_received - total_amount
        return JsonResponse({'message': 'Transaction successful', 'change': change, 'total_amount': total_amount})

    return redirect('cashier_pos')
