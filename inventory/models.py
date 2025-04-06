from django.db import models
from django.contrib.auth.models import User
from django import forms
from django.http import JsonResponse
def some_function():
    from .models import Item

# Model for UserProfile
class UserProfile(models.Model):
    ACCOUNT_TYPES = (
        ('Admin', 'Admin'),
        ('Cashier', 'Cashier'),
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    account_type = models.CharField(max_length=10, choices=ACCOUNT_TYPES)

    def __str__(self):
        return f"{self.user.username} ({self.account_type})"

# Model for Category
class Category(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

class Item(models.Model):
    name = models.CharField(max_length=100)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)  # Assuming Category is another model
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Add quantity if it's missing
    quantity = models.IntegerField(default=0)

    def __str__(self):
        return self.name
    
    
# Model for Sale
class Sale(models.Model):
    date = models.DateField()
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    total_price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"Sale of {self.item.name} on {self.date}"
# Model for SaleItem
class SaleItem(models.Model):
    sale = models.ForeignKey(Sale, on_delete=models.CASCADE, related_name='items')
    item = models.ForeignKey('Item', on_delete=models.SET_NULL, null=True)  # Use string reference for ForeignKey
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.item.name} x {self.quantity}"

# ItemForm for adding items
class ItemForm(forms.ModelForm):
    class Meta:
        model = Item
        fields = ['name', 'category', 'description', 'quantity', 'price']

def cashier_pos(request):
    items = Item.objects.all()
    return render(request, 'cashier_pos.html', {'items': items})

def add_to_cart(request):
    item_id = request.POST.get('item_id')
    quantity = int(request.POST.get('quantity'))

    item = Item.objects.get(id=item_id)
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

        # Record sale in the database
        for cart_item in cart:
            item = Item.objects.get(name=cart_item['item'])
            Sale.objects.create(
                item=item,
                quantity=cart_item['quantity'],
                total_price=cart_item['subtotal']
            )

        # Clear cart
        request.session['cart'] = []
        request.session.modified = True

        change = payment_received - total_amount
        return JsonResponse({'message': 'Transaction successful', 'change': change, 'total_amount': total_amount})
    return redirect('cashier_pos')

def sales_report(request):
    period = request.GET.get('period', 'today')

    if period == 'today':
        start_date = datetime.today().date()
        end_date = start_date
    elif period == 'week':
        start_date = datetime.today() - timedelta(days=7)
        end_date = datetime.today()
    elif period == 'month':
        start_date = datetime.today() - timedelta(days=30)
        end_date = datetime.today()
    elif period == 'year':
        start_date = datetime.today() - timedelta(days=365)
        end_date = datetime.today()

    sales_data = Sale.objects.filter(date__range=[start_date, end_date])
    total_sales = sales_data.aggregate(Sum('total_price'))['total_price__sum'] or 0.00

    return render(request, 'sales_report.html', {
        'sales_data': sales_data,
        'total_sales': total_sales,
        'selected_period': period
    })