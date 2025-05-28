from django.shortcuts import render, redirect, get_object_or_404
from .models import *
from django.db.models import Q, Sum
from django.core.paginator import Paginator
from django.contrib import messages

# Create your views here.
def dashboard(request):

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

    return render(request, 'myapp/dashboard.html', context)

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

    return render(request, 'myapp/create_order.html')

def customer_list(request):

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

    return render(request, 'myapp/customer_list.html', context)

def order_detail(request, order_id):

    """View order details"""
    order = get_object_or_404(Order.objects.select_related('customer'), id=order_id)
    payments = order.payments.all().order_by('-payment_date')
    
    context = {
        'order': order,
        'payments': payments,
    }

    return render(request, 'myapp/order_detail.html', context)

def order_list(request):

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

    return render(request, 'myapp/order_list.html', context)

def payment_list(request):

    """List pending payments"""
    orders_with_balance = Order.objects.select_related('customer').filter(
        total_cost__gt=models.F('amount_paid')
    ).order_by('due_date')
    
    context = {
        'orders_with_balance': orders_with_balance,
    }

    return render(request, 'myapp/payment_list.html', context)


def login(request):

    return render(request, 'myapp/login.html')

def register(request):

    return render(request, 'myapp/register.html')