from django.db import models

class TicketBooking(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    date = models.DateField()
    tickets = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    qr_code = models.ImageField(upload_to='qrcodes/', blank=True, null=True)  # ✅ Add QR Code field

    def __str__(self):
        return f"{self.name} - {self.tickets} Tickets"
