from celery import shared_task
from django.core.mail import send_mail
from django.apps import apps  # Import apps to get the model dynamically

@shared_task
def send_welcome_email(passenger_id):
    """Task to send a welcome email to the passenger."""
    try:
        Passenger = apps.get_model('passenger', 'Passenger')
        passenger = Passenger.objects.get(passenger_id=passenger_id)
        send_mail(
            subject="Welcome to  Uberv",
            message=f"Hello {passenger.first_name},\n\nWelcome to Uberv!",
            from_email="noreply@example.com",
            recipient_list=[passenger.email],
        )
        print(f"Welcome email sent to {passenger.email}")
    except Passenger.DoesNotExist:
        print(f"Passenger with ID {passenger_id} does not exist.")