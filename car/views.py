import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages

from car.forms import CarForm, CustomerForm, HiringForm, PaymentForm, DriverForm, MaintenanceForm, PublicBookingForm, HandoverForm
from car.models import Car, Customer, Hiring, Payment, Driver, Maintenance
from car.utils import render_to_pdf
from django.utils import timezone

import datetime
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.db.models import Sum, Q





# ---------- Dashboard ----------
@login_required
def index_view(request):
    today = datetime.date.today()
    soon = today + datetime.timedelta(days=14)

    overdue = Maintenance.objects.filter(
        Q(status="S") | Q(status="I"),
        service_date__lt=today,
    ).count()

    upcoming = Maintenance.objects.filter(
        Q(status="S") | Q(status="I"),
        service_date__gte=today,
        service_date__lte=soon,
    ).count()

    in_garage = Car.objects.filter(status="M").count()

    # --- NEW: Calculate Overdue Hires ---
    # A hire is overdue if it's active, and (hire_date + number_of_days) is before today
    active_hires = Hiring.objects.filter(status="A")
    overdue_hires_count = 0
    for h in active_hires:
        expected_return = h.hire_date + datetime.timedelta(days=h.number_of_days)
        if expected_return < today:
            overdue_hires_count += 1

    return render(request, "index.html", {
        "total_cars": Car.objects.count(),
        "available": Car.objects.filter(status="A").count(),
        "taken": Car.objects.filter(status="T").count(),
        "in_garage": in_garage,
        "total_customers": Customer.objects.count(),
        "total_drivers": Driver.objects.count(),
        "drivers_available": Driver.objects.filter(status="A").count(),
        "total_hirings": Hiring.objects.count(),
        "overdue_maintenance": overdue,
        "upcoming_maintenance": upcoming,
        "overdue_hires": overdue_hires_count, # <-- Passed to template
    })

@login_required
def profile_view(request):
    return render(request, "profiles.html")


@login_required
def car_List_view(request):
    return render(request, "car_List.html", {"cars": Car.objects.all()})


# ---------- Sign-up ----------
def sign_in_view(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Account created. Please log in.")
            return redirect("login")
        messages.error(request, "Invalid form input.")
    else:
        form = UserCreationForm()
    return render(request, "registration/sign_in.html", {"form": form})


# ---------- Car CRUD ----------
@login_required
def add_car_view(request):
    if request.method == "POST":
        form = CarForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Car added successfully!")
            return redirect("add_car_page")
        messages.error(request, "Please fix the errors below.")
    else:
        form = CarForm()
    return render(request, "add_car.html", {"form": form, "cars": Car.objects.all()})


@login_required
def edit_car_view(request, car_id):
    car = get_object_or_404(Car, id=car_id)
    form = CarForm(request.POST or None, request.FILES or None, instance=car)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Car updated.")
        return redirect("add_car_page")
    return render(request, "edit_car.html", {"form": form, "car": car})


@login_required
def delete_car_view(request, car_id):
    get_object_or_404(Car, id=car_id).delete()
    messages.success(request, "Car deleted.")
    return redirect("add_car_page")


# ---------- Customer CRUD ----------
@login_required
def add_customer_view(request):
    if request.method == "POST":
        form = CustomerForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Customer added.")
            return redirect("add_customer_page")
    else:
        form = CustomerForm()
    return render(request, "add_customer.html", {"form": form, "customers": Customer.objects.all()})


@login_required
def edit_customer_view(request, customer_id):
    customer = get_object_or_404(Customer, id=customer_id)
    form = CustomerForm(request.POST or None, instance=customer)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Customer updated.")
        return redirect("add_customer_page")
    return render(request, "edit_customer.html", {"form": form, "customer": customer})


@login_required
def delete_customer_view(request, customer_id):
    get_object_or_404(Customer, id=customer_id).delete()
    messages.success(request, "Customer deleted.")
    return redirect("add_customer_page")


# ---------- Hiring CRUD ----------
@login_required
def add_hiring_view(request):
    if request.method == "POST":
        form = HiringForm(request.POST)
        if form.is_valid():
            hiring = form.save()
            hiring.car.status = "T"
            hiring.car.save()
            if hiring.service_type == "C" and hiring.driver:
                hiring.driver.status = "T"
                hiring.driver.save()
            messages.success(request, "Hire added.")
            return redirect("add_hiring_page")
    else:
        form = HiringForm()
    return render(request, "add_hiring.html", {"form": form, "hirings": Hiring.objects.all()})

@login_required
def edit_hiring_view(request, hiring_id):
    hiring = get_object_or_404(Hiring, id=hiring_id)
    form = HiringForm(request.POST or None, instance=hiring)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Hire updated.")
        return redirect("add_hiring_page")
    return render(request, "edit_hiring.html", {"form": form, "hiring": hiring})


@login_required
def delete_hiring_view(request, hiring_id):
    get_object_or_404(Hiring, id=hiring_id).delete()
    messages.success(request, "Hire deleted.")
    return redirect("add_hiring_page")


# ---------- Payment CRUD ----------
@login_required
def add_payment_view(request):
    if request.method == "POST":
        form = PaymentForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Payment recorded.")
            return redirect("add_payment_page")
    else:
        form = PaymentForm()
    return render(request, "add_payment.html", {"form": form, "payments": Payment.objects.all()})


@login_required
def edit_payment_view(request, payment_id):
    payment = get_object_or_404(Payment, id=payment_id)
    form = PaymentForm(request.POST or None, instance=payment)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Payment updated.")
        return redirect("add_payment_page")
    return render(request, "edit_payment.html", {"form": form, "payment": payment})


@login_required
def delete_payment_view(request, payment_id):
    get_object_or_404(Payment, id=payment_id).delete()
    messages.success(request, "Payment deleted.")
    return redirect("add_payment_page")


# ---------- PDF ----------
@login_required
def car_pdf_view(request):
    return render_to_pdf("car_pdf.html", {"cars": Car.objects.all()})

@login_required
def hiring_invoice_view(request, hiring_id):
    hiring = get_object_or_404(Hiring, id=hiring_id)
    
    # Calculate expected return date
    expected_return = hiring.hire_date + datetime.timedelta(days=hiring.number_of_days)
    
    context = {
        "hiring": hiring,
        "expected_return": expected_return,
        "today": datetime.date.today(),
        "company": {
            "name": "Pearl Drive Uganda",
            "address": "Plot 12, Kampala Road, Kampala",
            "phone": "+256 700 000 000",
            "email": "info@pearldrive.ug",
            "tin": "1001234567"
        }
    }
    
    return render_to_pdf("invoice_pdf.html", context)


def sign_in_view(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Account created. Please log in.")
            return redirect("login")
        messages.error(request, "Please fix the errors below.")
    else:
        form = UserCreationForm()
    return render(request, "registration/sign_up.html", {"form": form})

# ---------- Driver CRUD ----------
@login_required
def add_driver_view(request):
    if request.method == "POST":
        form = DriverForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Driver added.")
            return redirect("add_driver_page")
    else:
        form = DriverForm()
    return render(request, "add_driver.html", {"form": form, "drivers": Driver.objects.all()})


@login_required
def edit_driver_view(request, driver_id):
    driver = get_object_or_404(Driver, id=driver_id)
    form = DriverForm(request.POST or None, request.FILES or None, instance=driver)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Driver updated.")
        return redirect("add_driver_page")
    return render(request, "edit_driver.html", {"form": form, "driver": driver})


@login_required
def delete_driver_view(request, driver_id):
    get_object_or_404(Driver, id=driver_id).delete()
    messages.success(request, "Driver deleted.")
    return redirect("add_driver_page")


# ---------- Maintenance CRUD ----------
@login_required
def add_maintenance_view(request):
    if request.method == "POST":
        form = MaintenanceForm(request.POST)
        if form.is_valid():
            record = form.save()
            # If service is scheduled/in progress, flip car to Maintenance
            if record.status in ("S", "I") and record.car.status == "A":
                record.car.status = "M"
                record.car.save()
            messages.success(request, "Maintenance record added.")
            return redirect("add_maintenance_page")
        messages.error(request, "Please fix the errors below.")
    else:
        form = MaintenanceForm()

    records = Maintenance.objects.select_related("car").all()
    return render(request, "add_maintenance.html", {
        "form": form,
        "records": records,
        "today": datetime.date.today(),
    })


@login_required
def edit_maintenance_view(request, maintenance_id):
    record = get_object_or_404(Maintenance, id=maintenance_id)
    form = MaintenanceForm(request.POST or None, instance=record)
    if request.method == "POST" and form.is_valid():
        updated = form.save()
        # If marked Done, return the car to Available
        if updated.status == "D" and updated.car.status == "M":
            updated.car.status = "A"
            updated.car.save()
        messages.success(request, "Maintenance record updated.")
        return redirect("add_maintenance_page")
    return render(request, "edit_maintenance.html", {
        "form": form,
        "record": record,
    })


@login_required
def delete_maintenance_view(request, maintenance_id):
    record = get_object_or_404(Maintenance, id=maintenance_id)
    car = record.car
    record.delete()
    # If the car has no other active maintenance, free it up
    if car.status == "M" and not car.maintenances.filter(status__in=["S", "I"]).exists():
        car.status = "A"
        car.save()
    messages.success(request, "Maintenance record deleted.")
    return redirect("add_maintenance_page")


# ---------- PUBLIC VIEWS (No login required) ----------
def public_home_view(request):
    cars = Car.objects.filter(status="A")
    
    if request.method == "POST":
        form = PublicBookingForm(request.POST)
        if form.is_valid():
            hiring = form.save()
            messages.success(request, "Booking request received! We will contact you shortly.")
            return redirect("booking_success_page")
    else:
        form = PublicBookingForm()

    return render(request, "public/home.html", {"cars": cars, "form": form})

def booking_success_view(request):
    return render(request, "public/success.html")



# ---------- Returns & Overdue ----------
@login_required
def return_hiring_view(request, hiring_id):
    hiring = get_object_or_404(Hiring, id=hiring_id)
    
    if hiring.status != "C":
        # 1. Mark hire as completed
        hiring.status = "C"
        hiring.save()

        # 2. Free up the car
        hiring.car.status = "A"
        hiring.car.save()

        # 3. Free up the driver (if chauffeur)
        if hiring.driver:
            hiring.driver.status = "A"
            hiring.driver.save()

        messages.success(request, f"Hire #{hiring.id} completed. {hiring.car.plate_no} is now available.")
    else:
        messages.info(request, "This hire is already completed.")

    return redirect("add_hiring_page")


@login_required
def index_view(request):
    today = datetime.date.today()
    soon = today + datetime.timedelta(days=14)
    six_months_ago = today - datetime.timedelta(days=180)

    # 1. Alerts (Maintenance & Overdue Hires)
    overdue_maint = Maintenance.objects.filter(Q(status="S") | Q(status="I"), service_date__lt=today).count()
    upcoming_maint = Maintenance.objects.filter(Q(status="S") | Q(status="I"), service_date__gte=today, service_date__lte=soon).count()
    
    active_hires = Hiring.objects.filter(status="A")
    overdue_hires = sum(1 for h in active_hires if (h.hire_date + datetime.timedelta(days=h.number_of_days)) < today)

    # 2. Revenue Calculations
    # Total revenue is the sum of all payments recorded
    total_revenue = Payment.objects.aggregate(Sum('amount_paid'))['amount_paid__sum'] or 0
    
    # Revenue this month
    current_month_payments = Payment.objects.filter(
        payment_date__year=today.year, 
        payment_date__month=today.month
    )
    revenue_this_month = current_month_payments.aggregate(Sum('amount_paid'))['amount_paid__sum'] or 0

    # 3. Chart Data (Last 6 Months)
    chart_labels = []
    chart_data = []
    for i in range(5, -1, -1): # 5, 4, 3, 2, 1, 0 months ago
        # Calculate the first and last day of that month
        target_date = today - datetime.timedelta(days=i*30)
        month_start = target_date.replace(day=1)
        
        # Simple way to get end of month: first day of next month - 1 day
        if month_start.month == 12:
            next_month = month_start.replace(year=month_start.year+1, month=1)
        else:
            next_month = month_start.replace(month=month_start.month+1)
        month_end = next_month - datetime.timedelta(days=1)

        monthly_rev = Payment.objects.filter(
            payment_date__gte=month_start, 
            payment_date__lte=month_end
        ).aggregate(Sum('amount_paid'))['amount_paid__sum'] or 0

        chart_labels.append(month_start.strftime("%b %Y"))
        chart_data.append(float(monthly_rev))

    # 4. Top 5 Cars by Revenue (based on hires)
    top_cars = Car.objects.annotate(
        total_earned=Sum('hiring__payment__amount_paid')
    ).filter(total_earned__isnull=False).order_by('-total_earned')[:5]

    return render(request, "index.html", {
        "total_cars": Car.objects.count(),
        "available": Car.objects.filter(status="A").count(),
        "taken": Car.objects.filter(status="T").count(),
        "in_garage": Car.objects.filter(status="M").count(),
        "total_customers": Customer.objects.count(),
        "total_drivers": Driver.objects.count(),
        "drivers_available": Driver.objects.filter(status="A").count(),
        "total_hirings": Hiring.objects.count(),
        
        # New analytics data
        "overdue_maintenance": overdue_maint,
        "upcoming_maintenance": upcoming_maint,
        "overdue_hires": overdue_hires,
        "total_revenue": total_revenue,
        "revenue_this_month": revenue_this_month,
        "chart_labels": chart_labels,
        "chart_data": chart_data,
        "top_cars": top_cars,
    })



@login_required
def vehicle_handover_view(request, hiring_id):
    hiring = get_object_or_404(Hiring, id=hiring_id)
    
    if request.method == "POST":
        form = HandoverForm(request.POST, request.FILES, instance=hiring)
        if form.is_valid():
            hiring = form.save(commit=False)
            
            # If they added end_mileage, it's a Check-in (Return)
            if hiring.end_mileage is not None:
                hiring.status = "C" # Mark Completed
                hiring.car.status = "A" # Free the car
                hiring.car.save()
                if hiring.driver:
                    hiring.driver.status = "A"
                    hiring.driver.save()
                messages.success(request, f"Check-in complete. {hiring.car.plate_no} is now available.")
            
            # If they added start_mileage (and no end_mileage), it's a Checkout
            elif hiring.start_mileage is not None and hiring.status == "P":
                hiring.status = "A" # Mark Active
                hiring.car.status = "T" # Mark car as Taken
                hiring.car.save()
                messages.success(request, f"Checkout complete. {hiring.car.plate_no} is now on hire.")
            
            hiring.save()
            return redirect("add_hiring_page")
    else:
        form = HandoverForm(instance=hiring)

    return render(request, "handover.html", {"form": form, "hiring": hiring})




@login_required
def admin_control_view(request):
    # Gather all the stats the admin needs at a glance
    context = {
        "total_cars": Car.objects.count(),
        "available_cars": Car.objects.filter(status="A").count(),
        "cars_in_garage": Car.objects.filter(status="M").count(),
        "total_drivers": Driver.objects.count(),
        "total_customers": Customer.objects.count(),
        "pending_hires": Hiring.objects.filter(status="P").count(),
        "active_hires": Hiring.objects.filter(status="A").count(),
        "recent_hires": Hiring.objects.order_by('-id')[:5], # Last 5 bookings
    }
    return render(request, "admin_control.html", context)


@login_required
def fleet_map_view(request):
    active_hires = Hiring.objects.filter(status="A").select_related('car', 'customer')
    
    cars_data = []
    for hire in active_hires:
        car = hire.car
        
        # THE FIX: If the car doesn't have GPS, give it fake GPS automatically!
        if not car.current_latitude or not car.current_longitude:
            car.current_latitude = 0.3136 + random.uniform(-0.04, 0.04)
            car.current_longitude = 32.5811 + random.uniform(-0.04, 0.04)
            car.last_gps_update = timezone.now()
            car.save()

        cars_data.append({
            "plate": car.plate_no,
            "model": f"{car.make} {car.car_Model}",
            "lat": car.current_latitude,
            "lng": car.current_longitude,
            "driver": hire.driver.name if hire.driver else "Self-drive",
            "customer": hire.customer.customer_name,
            "last_update": car.last_gps_update.strftime("%H:%M:%S") if car.last_gps_update else "Never",
        })

    context = {
        "cars_json": json.dumps(cars_data)
    }
    return render(request, "fleet_map.html", context)
