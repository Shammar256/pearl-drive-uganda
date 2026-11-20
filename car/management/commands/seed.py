import random
import datetime
from django.core.management.base import BaseCommand
from django.utils import timezone
from car.models import Car, Customer, Driver, Hiring, Payment, Maintenance

class Command(BaseCommand):
    help = 'Seeds the database with dummy data for testing'

    def handle(self, *args, **kwargs):
        self.stdout.write("Clearing old data...")
        # WARNING: This deletes all current data!
        Payment.objects.all().delete()
        Hiring.objects.all().delete()
        Maintenance.objects.all().delete()
        Driver.objects.all().delete()
        Customer.objects.all().delete()
        Car.objects.all().delete()

        self.stdout.write("Creating Cars...")
        cars_data = [
            ("UBG 111A", "Toyota", "Premio", 5, "A", 150000),
            ("UBG 222B", "Toyota", "RAV4", 5, "A", 250000),
            ("UBG 333C", "Toyota", "Land Cruiser", 7, "A", 450000),
            ("UBG 444D", "Toyota", "Hiace", 14, "M", 350000),
            ("UBG 555E", "Nissan", "X-Trail", 5, "A", 220000),
            ("UBG 666F", "Mercedes", "C-Class", 4, "A", 300000),
            ("UBG 777G", "BMW", "X5", 5, "A", 350000),
            ("UBG 888H", "Hyundai", "Tucson", 5, "A", 180000),
            ("UBG 999I", "Kia", "Sportage", 5, "A", 180000),
            ("UBG 000J", "Subaru", "Forester", 5, "A", 200000),
        ]
        cars = []
        for plate, make, model, cap, trans, price in cars_data:
            car = Car.objects.create(
                plate_no=plate, make=make, car_Model=model,
                capacity=cap, transmission=trans, price_per_day=price,
                status="A"
            )
            cars.append(car)

        self.stdout.write("Creating Drivers...")
        drivers_data = [
            ("John Doe", "+256 770 000 001", "DL-001"),
            ("Mary Jane", "+256 770 000 002", "DL-002"),
            ("Peter Pan", "+256 770 000 003", "DL-003"),
            ("Sarah Connor", "+256 770 000 004", "DL-004"),
        ]
        drivers = []
        for name, phone, lic in drivers_data:
            driver = Driver.objects.create(
                name=name, phone=phone, license_no=lic,
                license_expiry=datetime.date.today() + datetime.timedelta(days=365),
                daily_rate=50000, status="A"
            )
            drivers.append(driver)

        self.stdout.write("Creating Customers...")
        customers_data = [
            ("Alice Smith", "+256 750 111 222", "alice@example.com"),
            ("Bob Johnson", "+256 750 333 444", "bob@example.com"),
            ("Charlie Brown", "+256 750 555 666", "charlie@example.com"),
            ("Diana Prince", "+256 750 777 888", "diana@example.com"),
            ("Ethan Hunt", "+256 750 999 000", "ethan@example.com"),
        ]
        customers = []
        for name, phone, email in customers_data:
            cust = Customer.objects.create(
                customer_name=name, contact=phone, email=email, address="Kampala"
            )
            customers.append(cust)

        self.stdout.write("Creating Hires and Payments...")
        today = datetime.date.today()
        
        # Create 15 Hires (5 completed, 5 active, 5 pending)
        for i in range(15):
            car = random.choice(cars)
            customer = random.choice(customers)
            days = random.randint(1, 7)
            
            # Distribute statuses
            if i < 5:
                status = "C" # Completed
                hire_date = today - datetime.timedelta(days=days + 10)
                car.status = "A"
            elif i < 10:
                status = "A" # Active
                hire_date = today - datetime.timedelta(days=1)
                car.status = "T"
            else:
                status = "P" # Pending
                hire_date = today + datetime.timedelta(days=5)
                car.status = "A"
            
            car.save()

            service = random.choice(["S", "C"])
            driver = random.choice(drivers) if service == "C" else None
            if driver and status == "A":
                driver.status = "T"
                driver.save()

            hire = Hiring.objects.create(
                hire_date=hire_date, customer=customer, car=car, driver=driver,
                number_of_days=days, service_type=service, status=status
            )

            # Create a payment for active and completed hires
            if status in ["A", "C"]:
                Payment.objects.create(
                    payment_date=hire_date, hire=hire, amount_paid=hire.amount_to_be_paid
                )

        self.stdout.write("Creating Maintenance...")
        for i in range(3):
            car = random.choice(cars)
            Maintenance.objects.create(
                car=car, service_type="O", description="Routine oil change",
                cost=150000, service_date=today - datetime.timedelta(days=10),
                next_service_date=today + datetime.timedelta(days=80),
                garage="Kampala Auto", status="D"
            )

        self.stdout.write(self.style.SUCCESS("Successfully seeded the database!"))