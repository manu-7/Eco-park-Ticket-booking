from django.urls import path
from . import views
from .views import adventure_activities

urlpatterns = [
    path('', views.home, name='home'),  # Home page
    path('book_ticket/', views.book_ticket, name='book_ticket'),  # Ticket booking
    path('contact/', views.contact, name='contact'),  # Contact page
    path('register/', views.register, name='register'),  # User registration
    path('login/', views.login_view, name='login'),  # User login
    path('logout/', views.logout_view, name='logout'),  # User logout
    path('ticket_confirmation/<int:ticket_id>/', views.ticket_confirmation, name='ticket_confirmation'),  # Confirmation page
    path('download_ticket/<int:ticket_id>/', views.download_ticket, name='download_ticket'), 

    # ✅ Payment URLs
    path('process_payment/<int:ticket_id>/', views.process_payment, name='process_payment'), 
    path('payment_success/', views.payment_success, name='payment_success'), 
    path('adventure/', adventure_activities, name='adventure'),
    
]
