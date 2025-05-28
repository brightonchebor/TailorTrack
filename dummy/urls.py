from django.urls import path
from .views import *

urlpatterns = [
    path('', dashboard, name='dashboard'),
    path('create_order/', create_order, name='create_order'),
    path('customer_list/', customer_list, name='customer_list'),
    path('order_detail/', order_detail, name='order_detail'),
    path('order_list/', order_list, name='order_list'),
    path('payment_list/', payment_list, name='payment_list'),
    path('login/', login, name='login'),
    path('register/', register, name='register'),
]
