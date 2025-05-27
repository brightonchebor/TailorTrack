from django.shortcuts import render

# Create your views here.
def dashboard(request):

    context = {}

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