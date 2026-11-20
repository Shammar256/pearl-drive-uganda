from django.db.models import Q
import datetime
from django import forms
from django.forms import ModelForm, DateInput
from car.models import Car, Customer, Hiring, Payment, Driver, Maintenance


class CarForm(ModelForm):
    class Meta:
        model = Car
        fields = ["plate_no", "make", "car_Model", "capacity",
                  "transmission", "price_per_day", "status", "image", "features"] # Added features


class CustomerForm(ModelForm):
    class Meta:
        model = Customer
        fields = ["customer_name", "contact", "address", "email"]


class HiringForm(ModelForm):
    class Meta:
        model = Hiring
        fields = ["hire_date", "customer", "car", "service_type",
                  "driver", "number_of_days", "pickup_location"] # Added pickup_location
        widgets = {"hire_date": DateInput(attrs={"type": "date"})}

    def clean(self):
        cleaned = super().clean()
        car = cleaned.get("car")
        service = cleaned.get("service_type")
        driver = cleaned.get("driver")

        if car and car.status == "T":
            raise forms.ValidationError(f"{car.plate_no} is already taken.")

        if service == "C" and not driver:
            raise forms.ValidationError("Chauffeur hires require a driver.")

        if service == "S" and driver:
            raise forms.ValidationError("Self-drive hires should not have a driver.")

        if driver and driver.status == "T":
            raise forms.ValidationError(f"Driver {driver.name} is already on hire.")

        return cleaned


class PaymentForm(ModelForm):
    class Meta:
        model = Payment
        fields = ["payment_date", "hire", "amount_paid"]
        widgets = {"payment_date": DateInput(attrs={"type": "date"})}


class DriverForm(ModelForm):
    class Meta:
        model = Driver
        fields = ["name", "phone", "license_no", "license_expiry",
                  "daily_rate", "photo", "status"]
        widgets = {"license_expiry": DateInput(attrs={"type": "date"})}

    def clean_license_no(self):
        license_no = self.cleaned_data.get("license_no")
        qs = Driver.objects.filter(license_no=license_no)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError(
                f"A driver with license number '{license_no}' already exists."
            )
        return license_no


class MaintenanceForm(ModelForm):
    class Meta:
        model = Maintenance
        fields = ["car", "service_type", "description", "cost",
                  "service_date", "next_service_date", "garage", "status"]
        widgets = {
            "service_date": DateInput(attrs={"type": "date"}),
            "next_service_date": DateInput(attrs={"type": "date"}),
            "description": forms.Textarea(attrs={"rows": 2}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.instance.pk:
            self.fields["car"].queryset = Car.objects.exclude(status="M")


class PublicBookingForm(ModelForm):
    customer_name = forms.CharField(max_length=80)
    contact = forms.CharField(max_length=50)
    email = forms.EmailField(required=False)
    address = forms.CharField(max_length=120, required=False)

    class Meta:
        model = Hiring
        fields = ["car", "hire_date", "number_of_days", "service_type", "pickup_location"] # Added pickup_location
        widgets = {
            "hire_date": DateInput(attrs={"type": "date", "min": "2024-01-01"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["car"].queryset = Car.objects.filter(status="A")
        self.fields["car"].empty_label = "Select an available car..."

    def clean(self):
        cleaned_data = super().clean()
        car = cleaned_data.get("car")
        hire_date = cleaned_data.get("hire_date")
        days = cleaned_data.get("number_of_days")

        if car and hire_date and days:
            end_date = hire_date + datetime.timedelta(days=days)
            
            overlapping_hires = Hiring.objects.filter(
                car=car, 
                status__in=["P", "A"] 
            )
            
            for existing_hire in overlapping_hires:
                if existing_hire.overlaps_with(hire_date, end_date):
                    raise forms.ValidationError(
                        f"Sorry, the {car.make} {car.car_Model} is already booked from "
                        f"{existing_hire.hire_date} to {existing_hire.return_date}."
                    )
        return cleaned_data

    def save(self, commit=True):
        email = self.cleaned_data.get("email")
        phone = self.cleaned_data.get("contact")
        
        # Check if customer exists by email or phone
        qs = Customer.objects.filter(contact=phone)
        if email:
            qs = Customer.objects.filter(Q(email=email) | Q(contact=phone))
            
        existing_customer = qs.first()
        
        if existing_customer:
            customer = existing_customer
            customer.is_returning = True # Mark as returning client
            customer.save()
        else:
            customer = Customer.objects.create(
                customer_name=self.cleaned_data["customer_name"],
                contact=phone,
                email=email or "",
                address=self.cleaned_data.get("address", "N/A"),
                is_returning=False
            )

        hiring = super().save(commit=False)
        hiring.customer = customer
        hiring.status = "P" 
        if commit:
            hiring.save()
        return hiring


class HandoverForm(ModelForm):
    class Meta:
        model = Hiring
        fields = ["start_mileage", "start_fuel", "start_photo", 
                  "end_mileage", "end_fuel", "end_photo"]