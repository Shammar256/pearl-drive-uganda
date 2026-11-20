from django.core.management.base import BaseCommand
import datetime
from car.models import Hiring

class Command(BaseCommand):
    help = 'Sends SMS alerts for returns due tomorrow'

    def handle(self, *args, **kwargs):
        tomorrow = datetime.date.today() + datetime.timedelta(days=1)
        
        # Find all active hires that are due back tomorrow
        due_hires = Hiring.objects.filter(status="A")
        
        for hire in due_hires:
            if hire.return_date == tomorrow:
                # This is where you would integrate Africa's Talking or Twilio
                # For now, we just print to the console to simulate the SMS
                message = f"Hi {hire.customer.customer_name}, your {hire.car.make} {hire.car.car_Model} ({hire.car.plate_no}) is due back tomorrow ({tomorrow}). Please ensure it is fueled. - Pearl Drive Uganda"
                
                self.stdout.write(self.style.SUCCESS(f"SMS SENT TO {hire.customer.contact}: {message}"))