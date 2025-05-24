from django import forms
from .models import Customer, Order, DesignImage, Payment

class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ['name', 'phone_number', 'whatsapp_number']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Customer Name *',
                'id': 'customerName',
            }),
            'phone_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Phone Number *',
                'type': 'tel',
                'id': 'phoneNumber',
            }),
            'whatsapp_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'WhatsApp Number',
                'type': 'tel',
                'id': 'whatsappNumber',
            }),
        }

class OrderForm(forms.ModelForm):
    design_images = forms.FileField(
        widget=forms.ClearableFileInput(attrs={
            'multiple': True,
            'accept': 'image/*,.pdf',
            'class': 'form-control-file',
            'id': 'designUpload',
        }),
        required=False,
        label='Design Upload'
    )

    class Meta:
        model = Order
        fields = [
            'customer',
            'due_date',
            'status',
            'bust',
            'waist',
            'hips',
            'length',
            'measurement_notes',
            'design_notes',
            'total_cost',
            'amount_paid',
        ]
        widgets = {
            'customer': forms.Select(attrs={
                'class': 'form-control',
                'id': 'customerSelect',
            }),
            'due_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
                'id': 'dueDate',
                # you can set min via JS as you already do in index.html
            }),
            'status': forms.Select(attrs={
                'class': 'form-control',
                'id': 'orderStatus',
            }),
            'bust': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.5',
                'placeholder': 'Bust/Chest (inches)',
                'id': 'bust',
            }),
            'waist': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.5',
                'placeholder': 'Waist (inches)',
                'id': 'waist',
            }),
            'hips': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.5',
                'placeholder': 'Hips (inches)',
                'id': 'hips',
            }),
            'length': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.5',
                'placeholder': 'Length (inches)',
                'id': 'length',
            }),
            'measurement_notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Additional Measurements/Notes',
                'id': 'measurementNotes',
            }),
            'design_notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Design Notes',
                'id': 'designNotes',
            }),
            'total_cost': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'placeholder': 'Total Cost (₹) *',
                'id': 'totalCost',
            }),
            'amount_paid': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'placeholder': 'Amount Paid (₹)',
                'id': 'amountPaid',
            }),
        }

    def __init__(self, *args, **kwargs):
        # Allow passing request.FILES in to capture design_images
        self.files = kwargs.pop('files', None)
        super().__init__(*args, **kwargs)

    def save(self, commit=True):
        order = super().save(commit=commit)
        # handle uploaded files
        if self.files:
            for f in self.files.getlist('design_images'):
                DesignImage.objects.create(order=order, image=f)
        return order

class PaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = ['amount', 'notes']
        widgets = {
            'amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0.01',
                'step': '0.01',
                'placeholder': 'Payment Amount',
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Payment Notes (optional)',
            }),
        }

class DesignImageForm(forms.ModelForm):
    class Meta:
        model = DesignImage
        fields = ['image']
        widgets = {
            'image': forms.ClearableFileInput(attrs={
                'class': 'form-control-file',
                'accept': 'image/*,.pdf',
            }),
        }
