from django.db import models
from django.core.validators import RegexValidator
from django.utils import timezone

class Customer(models.Model):
    name = models.CharField(max_length=100)
    phone_number = models.CharField(
        max_length=15,
        validators=[RegexValidator(regex=r'^\+?1?\d{9,15}$', message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.")]
    )
    whatsapp_number = models.CharField(max_length=15, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['phone_number']
    
    def __str__(self):
        return self.name
    
    @property
    def total_orders(self):
        return self.orders.count()
    
    @property
    def total_spent(self):
        return sum(order.amount_paid for order in self.orders.all())

class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('progress', 'In Progress'),
        ('completed', 'Completed'),
        ('delivered', 'Delivered'),
    ]
    
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='orders')
    order_date = models.DateField(default=timezone.now)
    due_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Measurements
    bust = models.FloatField(null=True, blank=True)
    waist = models.FloatField(null=True, blank=True)
    hips = models.FloatField(null=True, blank=True)
    length = models.FloatField(null=True, blank=True)
    measurement_notes = models.TextField(blank=True)
    
    # Design and notes
    design_notes = models.TextField(blank=True)
    
    # Payment
    total_cost = models.DecimalField(max_digits=10, decimal_places=2)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Order #{self.id} - {self.customer.name}"
    
    @property
    def balance(self):
        return self.total_cost - self.amount_paid
    
    @property
    def is_overdue(self):
        return self.due_date < timezone.now().date() and self.status not in ['completed', 'delivered']

class DesignImage(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='design_images')
    image = models.ImageField(upload_to='design_images/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Design for Order #{self.order.id}"

class Payment(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True)
    
    def __str__(self):
        return f"Payment of ₹{self.amount} for Order #{self.order.id}"