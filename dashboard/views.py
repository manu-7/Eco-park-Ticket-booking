from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from .forms import TicketBookingForm, UserRegistrationForm, UserLoginForm
from .models import TicketBooking
import razorpay
from django.http import JsonResponse
import qrcode
import os
from django.core.files.base import ContentFile
from io import BytesIO
from reportlab.pdfgen import canvas
from django.http import HttpResponse
from datetime import date


#  Home Page

def home(request):
    return render(request, 'dashboard/home.html')


#  Ticket Booking Form

@login_required(login_url='login')
def book_ticket(request):
    if request.method == "POST":
        form = TicketBookingForm(request.POST)
        if form.is_valid():
            ticket = form.save(commit=False)

            # Ensure the selected date is only today
            if ticket.date != date.today():
                messages.error(request, "You can only book tickets for today.")
                return redirect('book_ticket')

            ticket.user = request.user
            ticket.save()
            messages.success(request, "Your ticket has been booked! Proceed to payment.")
            return redirect('process_payment', ticket.id)
        else:
            messages.error(request, "There was an error with your ticket booking. Please try again.")
    else:
        form = TicketBookingForm()

    return render(request, 'dashboard/book_ticket.html', {'form': form})

#  Initialize Razorpay Client
razorpay_client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

@login_required(login_url='login')
def process_payment(request, ticket_id):
    ticket = get_object_or_404(TicketBooking, id=ticket_id)

    #  Calculate total amount (₹30 per ticket)
    amount = ticket.tickets * 30 * 100  # Convert ₹ to paise

    #  Create Razorpay Order
    try:
        payment_data = {
            "amount": amount,
            "currency": "INR",
            "payment_capture": "1"  # Auto-capture payment
        }
        order = razorpay_client.order.create(data=payment_data)

        context = {
            "order_id": order["id"],
            "amount": amount,
            "razorpay_key": settings.RAZORPAY_KEY_ID,
            "name": request.user.get_full_name() or request.user.username,
            "email": request.user.email,
            "ticket_id": ticket.id 
        }
        return render(request, "dashboard/payment.html", context)

    except Exception as e:
        messages.error(request, f"Payment error: {str(e)}")
        return redirect('book_ticket')


@csrf_exempt
def payment_success(request):
    if request.method == "POST":
        ticket_id = request.POST.get("ticket_id")  

        if not ticket_id:
            messages.error(request, "Payment successful, but ticket ID is missing!")
            return redirect("home")

        # Get ticket details
        ticket = get_object_or_404(TicketBooking, id=ticket_id)

        total_amount = ticket.tickets * 30  
        print(f"Debug: Ticket ID {ticket.id} | Tickets: {ticket.tickets} | Amount: ₹{total_amount}")  # Debugging

        # Generate Invoice Data with Correct Amount
        invoice_data = f"""
        Eco Park Ticket Invoice
        --------------------------
        Name: {ticket.name}
        Email: {ticket.email}
        Date: {ticket.date}
        Tickets: {ticket.tickets}
        Amount Paid: ₹{total_amount}
        Ticket ID: {ticket.id}
        """

        #  Generate QR Code
        qr = qrcode.make(invoice_data)
        buffer = BytesIO()
        qr.save(buffer, format="PNG")

        # Save QR Code to Model
        qr_filename = f"qrcodes/invoice_{ticket.id}.png"
        ticket.qr_code.save(qr_filename, ContentFile(buffer.getvalue()), save=True)

        messages.success(request, "Payment successful! Your ticket is confirmed.")
        return redirect("ticket_confirmation", ticket_id=ticket.id)

    return JsonResponse({"error": "Invalid request"}, status=400)


#  Ticket Confirmation

@login_required(login_url='login')
def ticket_confirmation(request, ticket_id):
    ticket = get_object_or_404(TicketBooking, id=ticket_id)
    
    total_amount = ticket.tickets * 30  
    
    print(f"Ticket ID: {ticket.id}, Tickets: {ticket.tickets}, Total Amount: ₹{total_amount}")  

    return render(request, 'dashboard/ticket_confirmation.html', {
        'ticket': ticket, 
        'total_amount': total_amount
    })
# Contact Page

def contact(request):
    return render(request, 'dashboard/contact.html')


# User Registration

def register(request):
    if request.method == "POST":
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f"Account created for {user.username}!")
            return redirect('home')
    else:
        form = UserRegistrationForm()

    return render(request, "dashboard/register.html", {"form": form})


# User Login

def login_view(request):
    if request.method == "POST":
        form = UserLoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, "You have successfully logged in!")
            return redirect("home")
        else:
            messages.error(request, "Invalid credentials, please try again.")
    else:
        form = UserLoginForm()

    return render(request, "dashboard/login.html", {"form": form})

#  User Logout

@login_required(login_url='login')
def logout_view(request):
    logout(request)
    messages.success(request, "You have successfully logged out!")
    return redirect('home')



@login_required(login_url='login')
def download_ticket(request, ticket_id):
    ticket = get_object_or_404(TicketBooking, id=ticket_id)

    # Create a PDF response
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="ticket_{ticket.id}.pdf"'

    # Generate PDF content
    pdf = canvas.Canvas(response)
    pdf.setTitle("Eco Park Ticket")

    # PDF Header
    pdf.setFont("Helvetica-Bold", 16)
    pdf.drawString(200, 800, "Eco Park Ticket")

    pdf.setFont("Helvetica", 12)
    pdf.drawString(100, 750, f"Name: {ticket.name}")
    pdf.drawString(100, 730, f"Email: {ticket.email}")
    pdf.drawString(100, 710, f"Date: {ticket.date}")
    pdf.drawString(100, 690, f"Tickets: {ticket.tickets}")
    pdf.drawString(100, 670, f"Amount Paid: ₹{ticket.tickets * 30}")

    # Add QR Code if available
    if ticket.qr_code:
        qr_path = os.path.join(settings.MEDIA_ROOT, str(ticket.qr_code))
        if os.path.exists(qr_path):
            pdf.drawInlineImage(qr_path, 250, 580, 100, 100)

    # Save PDF and return response
    pdf.showPage()
    pdf.save()
    return response


def adventure_activities(request):
    return render(request, 'dashboard/adventure.html')