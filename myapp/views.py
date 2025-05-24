# views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.db.models import Q, Sum
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
from django.core.paginator import Paginator
import json
from .models import Customer, Order, DesignImage, Payment
from .forms import OrderForm, CustomerForm
from django.utils import timezone

def dashboard(request):
    """Main dashboard view"""
    # Statistics
    total_orders = Order.objects.count()
    active_orders = Order.objects.exclude(status='delivered').count()
    overdue_orders = Order.objects.filter(
        due_date__lt=timezone.now().date(),
        status__in=['pending', 'progress']
    ).count()
    total_revenue = Order.objects.aggregate(Sum('amount_paid'))['amount_paid__sum'] or 0
    
    # Recent orders
    recent_orders = Order.objects.select_related('customer').order_by('-created_at')[:5]
    
    context = {
        'total_orders': total_orders,
        'active_orders': active_orders,
        'overdue_orders': overdue_orders,
        'total_revenue': total_revenue,
        'recent_orders': recent_orders,
    }
    return render(request, 'tailortrack/dashboard.html', context)

def orders_list(request):
    """List all orders with filtering and searching"""
    orders = Order.objects.select_related('customer').all()
    
    # Search
    search_query = request.GET.get('search', '')
    if search_query:
        orders = orders.filter(
            Q(customer__name__icontains=search_query) |
            Q(customer__phone_number__icontains=search_query)
        )
    
    # Filter by status
    status_filter = request.GET.get('status', '')
    if status_filter:
        orders = orders.filter(status=status_filter)
    
    # Sort
    sort_by = request.GET.get('sort', 'date_desc')
    if sort_by == 'date_asc':
        orders = orders.order_by('created_at')
    elif sort_by == 'due_date':
        orders = orders.order_by('due_date')
    elif sort_by == 'customer':
        orders = orders.order_by('customer__name')
    else:  # date_desc
        orders = orders.order_by('-created_at')
    
    # Pagination
    paginator = Paginator(orders, 12)  # Show 12 orders per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'status_filter': status_filter,
        'sort_by': sort_by,
        'status_choices': Order.STATUS_CHOICES,
    }
    return render(request, 'tailortrack/orders_list.html', context)

def create_order(request):
    """Create new order"""
    if request.method == 'POST':
        # Handle form submission
        customer_name = request.POST.get('customer_name')
        phone_number = request.POST.get('phone_number')
        whatsapp_number = request.POST.get('whatsapp_number', phone_number)
        
        # Get or create customer
        customer, created = Customer.objects.get_or_create(
            phone_number=phone_number,
            defaults={
                'name': customer_name,
                'whatsapp_number': whatsapp_number
            }
        )
        
        # Create order
        order = Order.objects.create(
            customer=customer,
            due_date=request.POST.get('due_date'),
            status=request.POST.get('status', 'pending'),
            bust=request.POST.get('bust') or None,
            waist=request.POST.get('waist') or None,
            hips=request.POST.get('hips') or None,
            length=request.POST.get('length') or None,
            measurement_notes=request.POST.get('measurement_notes', ''),
            design_notes=request.POST.get('design_notes', ''),
            total_cost=request.POST.get('total_cost'),
            amount_paid=request.POST.get('amount_paid', 0),
        )
        
        # Handle file uploads
        for file in request.FILES.getlist('design_images'):
            DesignImage.objects.create(order=order, image=file)
        
        messages.success(request, 'Order created successfully!')
        return redirect('dashboard')
    
    return render(request, 'tailortrack/create_order.html')

def customers_list(request):
    """List all customers"""
    customers = Customer.objects.all().order_by('name')
    
    # Search
    search_query = request.GET.get('search', '')
    if search_query:
        customers = customers.filter(
            Q(name__icontains=search_query) |
            Q(phone_number__icontains=search_query)
        )
    
    context = {
        'customers': customers,
        'search_query': search_query,
    }
    return render(request, 'tailortrack/customers_list.html', context)

def payments_list(request):
    """List pending payments"""
    orders_with_balance = Order.objects.select_related('customer').filter(
        total_cost__gt=models.F('amount_paid')
    ).order_by('due_date')
    
    context = {
        'orders_with_balance': orders_with_balance,
    }
    return render(request, 'tailortrack/payments_list.html', context)

@csrf_exempt
def record_payment(request, order_id):
    """Record a payment for an order"""
    if request.method == 'POST':
        order = get_object_or_404(Order, id=order_id)
        data = json.loads(request.body)
        payment_amount = float(data.get('amount', 0))
        
        if payment_amount <= 0:
            return JsonResponse({'success': False, 'error': 'Invalid payment amount'})
        
        if payment_amount > float(order.balance):
            return JsonResponse({'success': False, 'error': 'Payment exceeds balance'})
        
        # Create payment record
        Payment.objects.create(
            order=order,
            amount=payment_amount,
            notes=data.get('notes', '')
        )
        
        # Update order
        order.amount_paid += payment_amount
        order.save()
        
        return JsonResponse({
            'success': True,
            'new_balance': float(order.balance),
            'total_paid': float(order.amount_paid)
        })
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})

def order_detail(request, order_id):
    """View order details"""
    order = get_object_or_404(Order.objects.select_related('customer'), id=order_id)
    payments = order.payments.all().order_by('-payment_date')
    
    context = {
        'order': order,
        'payments': payments,
    }
    return render(request, 'tailortrack/order_detail.html', context)

# Ajax views for dynamic updates
def get_orders_data(request):
    """Return orders data as JSON for frontend"""
    orders = Order.objects.select_related('customer').all()
    
    orders_data = []
    for order in orders:
        orders_data.append({
            'id': order.id,
            'customer_name': order.customer.name,
            'phone_number': order.customer.phone_number,
            'whatsapp_number': order.customer.whatsapp_number,
            'order_date': order.order_date.isoformat(),
            'due_date': order.due_date.isoformat(),
            'status': order.status,
            'total_cost': float(order.total_cost),
            'amount_paid': float(order.amount_paid),
            'balance': float(order.balance),
            'is_overdue': order.is_overdue,
            'measurements': {
                'bust': order.bust,
                'waist': order.waist,
                'hips': order.hips,
                'length': order.length,
                'notes': order.measurement_notes,
            },
            'design_notes': order.design_notes,
        })
    
    return JsonResponse({'orders': orders_data})

def get_customers_data(request):
    """Return customers data as JSON"""
    customers = Customer.objects.all()
    
    customers_data = []
    for customer in customers:
        customers_data.append({
            'name': customer.name,
            'phone': customer.phone_number,
            'whatsapp': customer.whatsapp_number,
            'total_orders': customer.total_orders,
            'total_spent': float(customer.total_spent),
        })
    
    return JsonResponse({'customers': customers_data})