import datetime
from django.db import models
from decimal import Decimal


class Car(models.Model):
    TRANSMISSION = [("M", "Manual"), ("A", "Automatic")]
    STATUS = [("A", "Available"), ("T", "Taken"), ("M", "Maintenance")]

    plate_no = models.CharField(max_length=50, unique=True)
    make = models.CharField(max_length=30)
    car_Model = models.CharField(max_length=50)
    capacity = models.IntegerField(null=True, blank=True)
    transmission = models.CharField(max_length=2, choices=TRANSMISSION)
    price_per_day = models.IntegerField(null=True, blank=True)
    status = models.CharField(max_length=2, choices=STATUS, default="A")
    image = models.ImageField(upload_to="cars/", null=True, blank=True)
    features = models.CharField(max_length=255, blank=True, help_text="e.g., Pop-up roof, Rooftop tent, 4x4")

    class Meta:
        verbose_name_plural = "Cars"
        ordering = ["make", "car_Model"]

    def __str__(self):
        return f"{self.make} {self.car_Model} ({self.plate_no})"


class Customer(models.Model):
    customer_name = models.CharField(max_length=80)
    contact = models.CharField(max_length=50, default="N/A")
    address = models.CharField(max_length=120, default="N/A")
    email = models.EmailField(blank=True, default="")
    is_returning = models.BooleanField(default=False, help_text="Checked automatically if customer has hired before.") 

    def __str__(self):
        return self.customer_name



class Driver(models.Model):
    STATUS = [("A", "Available"), ("T", "On Hire"), ("O", "Off Duty")]

    name = models.CharField(max_length=80)
    phone = models.CharField(max_length=30)
    license_no = models.CharField(max_length=40, unique=True)
    license_expiry = models.DateField()
    daily_rate = models.IntegerField(default=0, help_text="Driver fee per day (UGX)")
    photo = models.ImageField(upload_to="drivers/", null=True, blank=True)
    status = models.CharField(max_length=1, choices=STATUS, default="A")

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} ({self.license_no})"


class Maintenance(models.Model):
    SERVICE_TYPES = [
        ("O", "Oil change"),
        ("T", "Tyres"),
        ("B", "Brakes"),
        ("E", "Engine"),
        ("G", "General service"),
        ("R", "Repair"),
    ]
    STATUS = [
        ("S", "Scheduled"),
        ("I", "In progress"),
        ("D", "Done"),
    ]

    car = models.ForeignKey(Car, on_delete=models.CASCADE, related_name="maintenances")
    service_type = models.CharField(max_length=1, choices=SERVICE_TYPES)
    description = models.TextField(blank=True)
    cost = models.IntegerField(default=0, help_text="Cost in UGX")
    service_date = models.DateField()
    next_service_date = models.DateField(
        null=True, blank=True,
        help_text="When the next service is due",
    )
    garage = models.CharField(max_length=80, blank=True, default="")
    status = models.CharField(max_length=1, choices=STATUS, default="S")

    class Meta:
        ordering = ["-service_date"]

    def __str__(self):
        return f"{self.car.plate_no} — {self.get_service_type_display()} ({self.service_date})"




class Hiring(models.Model):
    SERVICE = [("S", "Self-drive"), ("C", "Chauffeur")]
    STATUS = [
        ("P", "Pending"),
        ("A", "Active"),
        ("C", "Completed"),
    ]
    PICKUP_CHOICES = [
        ("KLA", "Kampala Office"),
        ("EBB", "Entebbe Airport"),
        ("HTL", "Hotel Delivery"),
    ]

    hire_date = models.DateField()
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    car = models.ForeignKey(Car, on_delete=models.CASCADE)
    driver = models.ForeignKey(
        Driver, on_delete=models.SET_NULL,
        null=True, blank=True,
        help_text="Required for chauffeur hires",
    )
    number_of_days = models.IntegerField(default=1)
    service_type = models.CharField(max_length=1, choices=SERVICE, default="S")
    status = models.CharField(max_length=1, choices=STATUS, default="A")
    
    # New Business Logic Fields
    pickup_location = models.CharField(max_length=3, choices=PICKUP_CHOICES, default="KLA")
    discount_applied = models.BooleanField(default=False)
    amount_to_be_paid = models.IntegerField(editable=False, default=0)
    
    # Checkout Data
    start_mileage = models.IntegerField(null=True, blank=True, help_text="Odometer reading at pickup")
    start_fuel = models.IntegerField(null=True, blank=True, help_text="Fuel level at pickup (%)")
    start_photo = models.ImageField(upload_to="handovers/start/", null=True, blank=True)

    # Check-in Data
    end_mileage = models.IntegerField(null=True, blank=True, help_text="Odometer reading at return")
    end_fuel = models.IntegerField(null=True, blank=True, help_text="Fuel level at return (%)")
    end_photo = models.ImageField(upload_to="handovers/end/", null=True, blank=True)

    def save(self, *args, **kwargs):
        # 1. Calculate Base Rate
        rate = self.car.price_per_day or 0
        driver_fee = 0
        if self.service_type == "C" and self.driver:
            driver_fee = (self.driver.daily_rate or 0) * (self.number_of_days or 1)
        
        base_total = rate * (self.number_of_days or 1) + driver_fee
        
        # 2. Apply Returning Client Discount (10% off)
        if self.customer and self.customer.is_returning:
            self.amount_to_be_paid = int(base_total * 0.9) 
            self.discount_applied = True
        else:
            self.amount_to_be_paid = base_total
            self.discount_applied = False
            
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.customer} → {self.car} ({self.hire_date})"

    @property
    def return_date(self):
        return self.hire_date + datetime.timedelta(days=self.number_of_days)

    def overlaps_with(self, start_date, end_date):
        """Checks if this hire overlaps with a given date range."""
        return (self.hire_date < end_date) and (self.return_date > start_date)




class Payment(models.Model):
    payment_date = models.DateField()
    hire = models.ForeignKey(Hiring, on_delete=models.CASCADE)
    amount_paid = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.hire} — {self.amount_paid}"