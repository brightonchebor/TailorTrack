from django.shortcuts import render, redirect, get_object_or_404
from .models import *
from django.db.models import Q, Sum, F
from django.core.paginator import Paginator
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
import json
from django.utils import timezone
from decimal import Decimal

# Create your views here.
@login_required
def dashboard(request):
    # Statistics - filter by current user
    total_orders = Order.objects.filter(customer__user=request.user).count()
    active_orders = Order.objects.filter(customer__user=request.user).exclude(status='delivered').count()
    overdue_orders = Order.objects.filter(
        customer__user=request.user,
        due_date__lt=timezone.now().date(),
        status__in=['pending', 'progress']
    ).count()
    total_revenue = Order.objects.filter(customer__user=request.user).aggregate(Sum('amount_paid'))['amount_paid__sum'] or 0
    
    # Recent orders - filter by current user
    recent_orders = Order.objects.filter(customer__user=request.user).select_related('customer').order_by('-created_at')[:3]
    
    context = {
        'total_orders': total_orders,
        'active_orders': active_orders,
        'overdue_orders': overdue_orders,
        'total_revenue': total_revenue,
        'recent_orders': recent_orders,
    }

    return render(request, 'tailor/dashboard.html', context)

@login_required
def create_order(request):
    """Create new order"""
    if request.method == 'POST':
        # Handle form submission
        customer_name = request.POST.get('customer_name')
        phone_number = request.POST.get('phone_number')
        whatsapp_number = request.POST.get('whatsapp_number', phone_number)
        
        # Get or create customer - link to current user
        customer, created = Customer.objects.get_or_create(
            phone_number=phone_number,
            user=request.user,  # Filter by current user
            defaults={
                'name': customer_name,
                'whatsapp_number': whatsapp_number,
                'user': request.user  # Set user when creating
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

    return render(request, 'tailor/create_order.html')

@login_required
def customer_list(request):
    """List all customers with search functionality - filter by current user"""
    customers = Customer.objects.filter(user=request.user).order_by('name')
    
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
    
    return render(request, 'tailor/customer_list.html', context)

@login_required
def customer_details(request, customer_id):
    """Get detailed customer information as JSON - ensure customer belongs to current user"""
    customer = get_object_or_404(Customer, id=customer_id, user=request.user)
    
    # Get customer's orders with design images
    orders = customer.orders.prefetch_related('design_images').all().order_by('-created_at')[:10]  # Last 10 orders
    
    # Calculate totals using the correct field names
    total_spent = sum(float(order.amount_paid) for order in customer.orders.all())
    total_balance = sum(float(order.total_cost - order.amount_paid) for order in customer.orders.all())
    
    orders_data = []
    for order in orders:
        # Get design images for this order
        design_images = []
        for image in order.design_images.all():
            design_images.append({
                'id': image.id,
                'url': image.image.url,
                'uploaded_at': image.uploaded_at.strftime('%d-%b-%Y')
            })
        
        orders_data.append({
            'id': order.id,
            'status': order.get_status_display(),
            'created_at': order.created_at.strftime('%d-%b-%Y'),
            'due_date': order.due_date.strftime('%d-%b-%Y') if order.due_date else '',
            'total_amount': float(order.total_cost),  # Using total_cost from model
            'paid_amount': float(order.amount_paid),  # Using amount_paid from model
            'balance_amount': float(order.total_cost - order.amount_paid),  # Calculated balance
            'description': getattr(order, 'design_notes', ''),  # Using design_notes as description
            'design_images': design_images,  # Add design images
        })
    
    customer_data = {
        'id': customer.id,
        'name': customer.name,
        'phone_number': customer.phone_number,
        'whatsapp_number': customer.whatsapp_number or '',
        'created_at': customer.created_at.strftime('%d-%b-%Y'),
        'total_orders': customer.total_orders,
        'total_spent': float(total_spent),
        'total_balance': float(total_balance),
        'orders': orders_data,
    }
    
    return JsonResponse(customer_data)

@login_required
@require_POST
def customer_delete(request, customer_id):
    """Delete a customer and all associated orders - ensure customer belongs to current user"""
    try:
        customer = get_object_or_404(Customer, id=customer_id, user=request.user)
        customer_name = customer.name
        
        # Delete the customer (this will cascade delete orders if properly configured)
        customer.delete()
        
        return JsonResponse({
            'success': True,
            'message': f'Customer "{customer_name}" has been deleted successfully.'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)

@login_required
def customer_edit(request, customer_id):
    """Edit customer information - ensure customer belongs to current user"""
    customer = get_object_or_404(Customer, id=customer_id, user=request.user)
    
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            
            customer.name = data.get('name', customer.name)
            customer.phone_number = data.get('phone_number', customer.phone_number)
            customer.whatsapp_number = data.get('whatsapp_number', customer.whatsapp_number)
            
            customer.save()
            
            return JsonResponse({
                'success': True,
                'message': 'Customer updated successfully'
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=400)
    
    return JsonResponse({
        'success': False,
        'error': 'Invalid request method'
    }, status=405)

@login_required
def order_detail(request, order_id):
    """View order details - ensure order belongs to current user"""
    order = get_object_or_404(
        Order.objects.select_related('customer'), 
        id=order_id, 
        customer__user=request.user
    )
    payments = order.payments.all().order_by('-payment_date')
    
    context = {
        'order': order,
        'payments': payments,
    }

    return render(request, 'tailor/order_detail.html', context)

@login_required
def order_list(request):
    """List all orders with filtering and searching - filter by current user"""
    orders = Order.objects.filter(customer__user=request.user).select_related('customer')
    
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

    return render(request, 'tailor/order_list.html', context)

@login_required
def payment_list(request):
    """List pending payments - filter by current user"""
    orders_with_balance = Order.objects.filter(
        customer__user=request.user,
        total_cost__gt=F('amount_paid')
    ).select_related('customer').order_by('due_date')
    
    context = {
        'orders_with_balance': orders_with_balance,
    }

    return render(request, 'tailor/payment_list.html', context)

@login_required
@require_POST
def record_payment(request):
    """Record a payment for an order - ensure order belongs to current user"""
    try:
        order_id = request.POST.get('order_id')
        amount = request.POST.get('amount')
        notes = request.POST.get('notes', '')
        
        # Validate input
        if not order_id or not amount:
            return JsonResponse({
                'success': False,
                'error': 'Order ID and amount are required.'
            }, status=400)
        
        try:
            # Convert to Decimal to match database field type
            amount = Decimal(str(amount))
        except (ValueError, TypeError):
            return JsonResponse({
                'success': False,
                'error': 'Invalid amount format.'
            }, status=400)
        
        if amount <= 0:
            return JsonResponse({
                'success': False,
                'error': 'Payment amount must be greater than zero.'
            }, status=400)
        
        # Get the order - ensure it belongs to current user
        order = get_object_or_404(Order, id=order_id, customer__user=request.user)
        
        # Check if payment amount doesn't exceed balance
        current_balance = order.total_cost - order.amount_paid
        if amount > current_balance:
            return JsonResponse({
                'success': False,
                'error': f'Payment amount cannot exceed outstanding balance of KES {current_balance:,.2f}'
            }, status=400)
        
        # Create payment record
        payment = Payment.objects.create(
            order=order,
            amount=amount,
            notes=notes
        )
        
        # Update order's amount_paid - now both are Decimal
        order.amount_paid += amount
        order.save()
        
        # Update order status if fully paid
        if order.amount_paid >= order.total_cost:
            order.status = 'completed'
            order.save()
        
        return JsonResponse({
            'success': True,
            'message': f'Payment of KES {amount:,.2f} recorded successfully!',
            'new_balance': float(order.total_cost - order.amount_paid),
            'new_amount_paid': float(order.amount_paid)
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'An error occurred: {str(e)}'
        }, status=500)