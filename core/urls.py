from django.urls import path
from . import views

urlpatterns = [
    path('tables/', views.floor_plan, name='floor_plan'),
    path('kitchen/', views.kitchen_view, name='kitchen_view'),
    path('initiate-order/<int:table_id>/', views.order_detail, name='initiate_order'),
    path('place-order/', views.place_order, name='place_order'),
    path('kitchen/serve/<int:order_id>/', views.mark_as_served, name='mark_as_served'),
    path('order/<int:order_id>/request-bill/', views.request_bill, name='request_bill'),
    
    # 2. Cashier ka main dashboard (Search isi mein handle hoga)
    path('cashier/dashboard/', views.cashier_dashboard, name='cashier_dashboard'),
    
    # 3. Popup Notification ke liye AJAX check (Har 5 sec mein call hoga)
    path('check-bill-requests/', views.check_bill_requests, name='check_bill_requests'),
    
    # 4. Final Bill/Invoice generate aur payment collect karne ke liye
    path('generate-invoice/<int:order_id>/', views.generate_invoice, name='generate_invoice'),
]