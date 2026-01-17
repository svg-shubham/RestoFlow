import json
from django.shortcuts import render,redirect,get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Table,TableSection,Category,Order,MenuItem,OrderItem
import json
from django.contrib import messages
from django.db import transaction
from django.http import JsonResponse
from decimal import Decimal

# Create your views here.
@login_required
def floor_plan(request):
    sections = TableSection.objects.filter(is_active=True).prefetch_related('tables')
    
    return render(request, 'core/floor_plan.html', {
        'sections': sections,
        'available_count': Table.objects.filter(status='AVAILABLE').count(),
        'occupied_count': Table.objects.filter(status='OCCUPIED').count(),
    })

@login_required
def order_detail(request, table_id):
    table = get_object_or_404(Table, id=table_id)
    
    # 1. Active Order dhundo (Jo abhi tak Bill nahi hua)
    order = Order.objects.filter(
        table=table, 
        status__in=['PENDING', 'IN_PROGRESS', 'SERVED']
    ).first()

    # 2. Agar table AVAILABLE hai aur koi order nahi hai -> Naya Order banao
    if not order:
        order = Order.objects.create(
            table=table, 
            status='PENDING', 
            asst_manager=request.user
        )
        table.status = 'OCCUPIED'
        table.save()

    # 3. Menu Data tayyar karo
    categories = Category.objects.filter(is_active=True).prefetch_related('items')
    menu_data = []
    for cat in categories:
        items = [{'id': i.id, 'name': i.name, 'price': float(i.price), 'veg': i.food_type == 'VEG'} for i in cat.items.all()]
        menu_data.append({'name': cat.name, 'items': items})

    # 4. PEHLE SE ORDERED ITEMS (Jo DB mein hain)
    existing_items_list = []
    for oi in order.order_items.all():
        existing_items_list.append({
            'id': oi.menu_item.id,
            'name': oi.menu_item.name,
            'price': float(oi.price_at_order),
            'quantity': oi.quantity,
            'is_existing': True  # Mark as already in kitchen
        })

    context = {
        'table': table,
        'order_id': order.id,
        'categories': categories,
        'menu_json': json.dumps(menu_data),
        'existing_json': json.dumps(existing_items_list),
    }
    return render(request, 'core/order_screen.html', context)

@login_required
def place_order(request):
    if request.method == 'POST':
        order_id = request.POST.get('order_id')
        cart_data = json.loads(request.POST.get('cart_data'))
        order = get_object_or_404(Order, id=order_id)

        with transaction.atomic():
            for item in cart_data['items']:
                # SIRF NAYE ITEMS ADD KARO (is_existing check)
                if not item.get('is_existing', False):
                    menu_item = MenuItem.objects.get(id=item['id'])
                    OrderItem.objects.create(
                        order=order,
                        menu_item=menu_item,
                        quantity=item['quantity'],
                        price_at_order=menu_item.price,
                        status='PREPARING'
                    )
            
            order.status = 'IN_PROGRESS' # Ab ye kitchen mein dikhega
            order.save()
            
        messages.success(request, "Order Kitchen ko bhej diya gaya!")
        return redirect('floor_plan')

@login_required
def kitchen_view(request):
    # Sirf wo orders uthao jo IN_PROGRESS hain
    # Aur unke wahi items uthao jo PREPARING status mein hain
    from django.db.models import Prefetch
    
    preparing_items = OrderItem.objects.filter(status='PREPARING')
    
    active_orders = Order.objects.filter(status='IN_PROGRESS').prefetch_related(
        Prefetch('order_items', queryset=preparing_items, to_attr='items_to_cook')
    ).order_by('-created_at')

    # Ek filter aur: Agar order IN_PROGRESS hai par uske saare items ready ho chuke hain, 
    # toh wo card kitchen se hat jana chahiye.
    filtered_orders = [o for o in active_orders if o.items_to_cook]

    return render(request, 'core/kitchen_view.html', {'orders': filtered_orders})


@login_required
def mark_as_served(request, order_id):
    if request.method == 'POST':
        order = get_object_or_404(Order, id=order_id)
        # Is order ke saare PREPARING items ko SERVED kar do
        order.order_items.filter(status='PREPARING').update(status='SERVED')
        
        # Check karo agar ab kuch bhi pakane ko nahi bacha toh order status change kar do
        if not order.order_items.filter(status='PREPARING').exists():
            # Yahan hum status SERVED kar rahe hain, par table tab tak OCCUPIED rahegi 
            # jab tak Manager billing nahi kar deta.
            order.status = 'SERVED' 
            order.save()
            
        messages.success(request, f"Table {order.table.table_number} ka order ready hai!")
    return redirect('kitchen_view')

def request_bill(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    order.status = 'BILLING'
    order.save()
    return redirect('floor_plan')

# --- CASHIER: AJAX Popup Check ---
def check_bill_requests(request):
    # Sirf wo orders fetch karo jinka status BILLING hai
    requests = Order.objects.filter(status='BILLING')
    if requests.exists():
        r = requests.first()
        return JsonResponse({
            'new_requests': True, 
            'order_id': r.id, 
            'table_no': r.table.table_number
        })
    return JsonResponse({'new_requests': False})

# --- CASHIER: Dashboard ---
def cashier_dashboard(request):
    query = request.GET.get('search', '')
    orders = Order.objects.filter(status__in=['IN_PROGRESS', 'SERVED', 'BILLING'])
    if query:
        orders = orders.filter(Q(table__table_number__icontains=query))
    return render(request, 'core/cashier_dashboard.html', {'orders': orders, 'search': query})

# --- CASHIER: Final Invoice ---
def generate_invoice(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    items = order.order_items.all()
    
    subtotal = Decimal('0.00')
    for item in items:
        # Har item ka total backend mein calculate kar rahe hain (Fixes Multiply Error)
        item.item_total = Decimal(str(item.quantity)) * Decimal(str(item.price_at_order))
        subtotal += item.item_total

    tax = subtotal * Decimal('0.05') # Fixes Decimal vs Float Error
    total = subtotal + tax

    if request.method == 'POST':
        order.subtotal = subtotal
        order.tax_amount = tax
        order.total_amount = total
        order.payment_mode = request.POST.get('payment_mode')
        order.is_paid = True
        order.status = 'COMPLETED'
        order.save()
        
        # Table ko available karo
        table = order.table
        table.status = 'AVAILABLE'
        table.save()
        return redirect('cashier_dashboard')

    return render(request, 'core/invoice.html', {
        'order': order, 'items': items, 'subtotal': subtotal, 'tax': tax, 'total': total
    })