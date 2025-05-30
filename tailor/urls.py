from django.urls import path
from .views import *

urlpatterns = [
    path('', dashboard, name='dashboard'),
    path('create_order/', create_order, name='create_order'),
    path('customer_list/', customer_list, name='customer_list'),
    path('customers/<int:customer_id>/details/', customer_details, name='customer_details'),
    path('customers/<int:customer_id>/delete/', customer_delete, name='customer_delete'),
    path('customers/<int:customer_id>/edit/', customer_edit, name='customer_edit'),
    path('order_detail/', order_detail, name='order_detail'),
    path('order_list/', order_list, name='order_list'),
    path('payment_list/', payment_list, name='payment_list'),
    path('record-payment/', record_payment, name='record_payment'),
    path('login/', login, name='login'),
    path('register/', register, name='register'),
]
