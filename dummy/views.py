from django.shortcuts import render
from myapp.models import *
from django.db.models import Q, Sum

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

    context = {}

    return render(request, 'myapp/create_order.html', context)

def customer_list(request):

    context = {}

    return render(request, 'myapp/customer_list.html', context)

def order_detail(request):

    context = {}

    return render(request, 'myapp/order_detail.html', context)

def order_list(request):

    context = {}

    return render(request, 'myapp/order_list.html', context)

def payment_list(request):

    context = {}

    return render(request, 'myapp/payment_list.html', context)