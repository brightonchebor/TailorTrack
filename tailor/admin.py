from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import Customer, Order, DesignImage, Payment
from django.contrib.auth.models import User

# Custom admin site configuration
admin.site.site_header = "Tailor Management System"
admin.site.site_title = "Tailor Admin"
admin.site.index_title = "Welcome to Tailor Management System"

class DesignImageInline(admin.TabularInline):
    model = DesignImage
    extra = 1
    readonly_fields = ('image_preview',)
    fields = ('image', 'image_preview', 'uploaded_at')
    
    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" width="100" height="100" style="object-fit: cover; border-radius: 5px;" />',
                obj.image.url
            )
        return "No image"
    image_preview.short_description = "Preview"

class PaymentInline(admin.TabularInline):
    model = Payment
    extra = 0
    readonly_fields = ('payment_date',)
    fields = ('amount', 'payment_date', 'notes')

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = [
        'name', 
        'phone_number', 
        'whatsapp_number', 
        'user',
        'total_orders_display', 
        'total_spent_display',
        'created_at'
    ]
    list_filter = [
        'user',
        'created_at',
    ]
    search_fields = [
        'name', 
        'phone_number', 
        'whatsapp_number',
        'user__username'
    ]
    readonly_fields = [
        'created_at', 
        'total_orders_display', 
        'total_spent_display'
    ]
    fieldsets = (
        ('Customer Information', {
            'fields': ('user', 'name', 'phone_number', 'whatsapp_number')
        }),
        ('Statistics', {
            'fields': ('total_orders_display', 'total_spent_display', 'created_at'),
            'classes': ('collapse',)
        }),
    )
    
    def total_orders_display(self, obj):
        count = obj.total_orders
        if count > 0:
            url = reverse('admin:tailor_order_changelist') + f'?customer__id__exact={obj.id}'
            return format_html('<a href="{}">{} orders</a>', url, count)
        return "0 orders"
    total_orders_display.short_description = "Total Orders"
    
    def total_spent_display(self, obj):
        amount = obj.total_spent
        return f"KES {amount:,.2f}"
    total_spent_display.short_description = "Total Spent"
    
    def get_queryset(self, request):
        # Super users see all customers, regular users only see their own
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(user=request.user)
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        # Auto-set user field for non-superusers
        if db_field.name == "user" and not request.user.is_superuser:
            kwargs["queryset"] = User.objects.filter(id=request.user.id)
            kwargs["initial"] = request.user.id
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'customer_link',
        'user_display',
        'status_badge',
        'order_date',
        'due_date',
        'total_cost',
        'amount_paid',
        'balance_display',
        'is_overdue_display'
    ]
    list_filter = [
        'status',
        'customer__user',
        'order_date',
        'due_date',
        'created_at'
    ]
    search_fields = [
        'customer__name',
        'customer__phone_number',
        'design_notes',
        'measurement_notes'
    ]
    readonly_fields = [
        'created_at',
        'updated_at',
        'balance_display',
        'is_overdue_display'
    ]
    inlines = [DesignImageInline, PaymentInline]
    
    fieldsets = (
        ('Order Information', {
            'fields': ('customer', 'status', 'order_date', 'due_date')
        }),
        ('Measurements', {
            'fields': ('bust', 'waist', 'hips', 'length', 'measurement_notes'),
            'classes': ('collapse',)
        }),
        ('Design & Notes', {
            'fields': ('design_notes',),
            'classes': ('collapse',)
        }),
        ('Payment Information', {
            'fields': ('total_cost', 'amount_paid', 'balance_display')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def customer_link(self, obj):
        url = reverse('admin:tailor_customer_change', args=[obj.customer.id])
        return format_html('<a href="{}">{}</a>', url, obj.customer.name)
    customer_link.short_description = "Customer"
    
    def user_display(self, obj):
        return obj.customer.user.username
    user_display.short_description = "User"
    
    def status_badge(self, obj):
        colors = {
            'pending': '#ffc107',
            'progress': '#17a2b8',
            'completed': '#28a745',
            'delivered': '#6c757d'
        }
        color = colors.get(obj.status, '#6c757d')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 3px; font-size: 12px;">{}</span>',
            color, obj.get_status_display()
        )
    status_badge.short_description = "Status"
    
    def balance_display(self, obj):
        balance = obj.balance
        if balance > 0:
            return format_html('<span style="color: red;">KES {:.2f}</span>', balance)
        elif balance == 0:
            return format_html('<span style="color: green;">Paid</span>')
        else:
            return format_html('<span style="color: blue;">Overpaid by KES {:.2f}</span>', abs(balance))
    balance_display.short_description = "Balance"
    
    def is_overdue_display(self, obj):
        if obj.is_overdue:
            return format_html('<span style="color: red; font-weight: bold;">⚠️ Overdue</span>')
        return format_html('<span style="color: green;">✓ On time</span>')
    is_overdue_display.short_description = "Due Status"
    
    def get_queryset(self, request):
        # Super users see all orders, regular users only see their own
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(customer__user=request.user)
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        # Filter customers to only show user's own customers
        if db_field.name == "customer" and not request.user.is_superuser:
            kwargs["queryset"] = Customer.objects.filter(user=request.user)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

@admin.register(DesignImage)
class DesignImageAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'order_link',
        'customer_name',
        'image_preview',
        'uploaded_at'
    ]
    list_filter = [
        'uploaded_at',
        'order__customer__user'
    ]
    search_fields = [
        'order__customer__name',
        'order__id'
    ]
    readonly_fields = ['uploaded_at', 'image_preview']
    
    def order_link(self, obj):
        url = reverse('admin:tailor_order_change', args=[obj.order.id])
        return format_html('<a href="{}">Order #{}</a>', url, obj.order.id)
    order_link.short_description = "Order"
    
    def customer_name(self, obj):
        return obj.order.customer.name
    customer_name.short_description = "Customer"
    
    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" width="150" height="150" style="object-fit: cover; border-radius: 5px;" />',
                obj.image.url
            )
        return "No image"
    image_preview.short_description = "Preview"
    
    def get_queryset(self, request):
        # Super users see all images, regular users only see their own
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(order__customer__user=request.user)

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'order_link',
        'customer_name',
        'amount_display',
        'payment_date',
        'notes_preview'
    ]
    list_filter = [
        'payment_date',
        'order__customer__user'
    ]
    search_fields = [
        'order__customer__name',
        'order__id',
        'notes'
    ]
    readonly_fields = ['payment_date']
    date_hierarchy = 'payment_date'
    
    def order_link(self, obj):
        url = reverse('admin:tailor_order_change', args=[obj.order.id])
        return format_html('<a href="{}">Order #{}</a>', url, obj.order.id)
    order_link.short_description = "Order"
    
    def customer_name(self, obj):
        return obj.order.customer.name
    customer_name.short_description = "Customer"
    
    def amount_display(self, obj):
        return f"KES {obj.amount:,.2f}"
    amount_display.short_description = "Amount"
    
    def notes_preview(self, obj):
        if obj.notes:
            return obj.notes[:50] + "..." if len(obj.notes) > 50 else obj.notes
        return "-"
    notes_preview.short_description = "Notes"
    
    def get_queryset(self, request):
        # Super users see all payments, regular users only see their own
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(order__customer__user=request.user)