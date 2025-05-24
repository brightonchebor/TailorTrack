# urls.py (in your app)
from django.urls import path
from . import views

app_name = 'tailortrack'

urlpatterns = [
    # Main views
    path('', views.dashboard, name='dashboard'),
    path('orders/', views.orders_list, name='orders_list'),
    path('orders/create/', views.create_order, name='create_order'),
    path('orders/<int:order_id>/', views.order_detail, name='order_detail'),
    path('customers/', views.customers_list, name='customers_list'),
    path('payments/', views.payments_list, name='payments_list'),
    
    # Ajax endpoints
    path('api/orders/', views.get_orders_data, name='get_orders_data'),
    path('api/customers/', views.get_customers_data, name='get_customers_data'),
    path('api/payments/record/<int:order_id>/', views.record_payment, name='record_payment'),
]

