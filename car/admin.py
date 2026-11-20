from django.contrib import admin

from .models import Car,Customer,Hiring,Payment

class Carking(admin.ModelAdmin):
    list_display = ("plate_no", "make", "model", "capacity", "price_per_day", "transmission", "status") 

admin.site.register(Car, Carking)
class Customerking(admin.ModelAdmin):
    list_display = ("customer_name", "contact", "address")

admin.site.register(Customer, Customerking)


class Hiringking(admin.ModelAdmin):
    list_display = ("hire_date", "customer", "car","number_of_days", "amount_to_be_paid")


admin.site.register(Hiring, Hiringking)

class Paymentking(admin.ModelAdmin):
    list_display = ("payment_date", "hire", "amount_paid") 

admin.site.register(Payment, Paymentking)


class Hiringking(admin.ModelAdmin):
    list_display = ("hire_date", "customer", "car", "service_type", "status", "amount_to_be_paid")
    list_filter = ("status", "service_type")