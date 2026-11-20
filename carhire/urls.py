from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static


from car import views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("django.contrib.auth.urls")),
    path("sign_in/", views.sign_in_view, name="sign_in_page"),

    path("", views.index_view, name="index_page"),
    path("profile/", views.profile_view, name="profiles_page"),
    path("cars/", views.car_List_view, name="car_List_page"),

    path("add_car/", views.add_car_view, name="add_car_page"),
    path("add_customer/", views.add_customer_view, name="add_customer_page"),
    path("add_hiring/", views.add_hiring_view, name="add_hiring_page"),
    path("add_payment/", views.add_payment_view, name="add_payment_page"),

    path("edit_car/<int:car_id>/", views.edit_car_view, name="edit_car_page"),
    path("edit_customer/<int:customer_id>/", views.edit_customer_view, name="edit_customer_page"),
    path("edit_hiring/<int:hiring_id>/", views.edit_hiring_view, name="edit_hiring_page"),
    path("edit_payment/<int:payment_id>/", views.edit_payment_view, name="edit_payment_page"),

    path("delete_car/<int:car_id>/", views.delete_car_view, name="delete_car_page"),
    path("delete_customer/<int:customer_id>/", views.delete_customer_view, name="delete_customer_page"),
    path("delete_hiring/<int:hiring_id>/", views.delete_hiring_view, name="delete_hiring_page"),
    path("delete_payment/<int:payment_id>/", views.delete_payment_view, name="delete_payment_page"),

    path("add_driver/", views.add_driver_view, name="add_driver_page"),
    path("edit_driver/<int:driver_id>/", views.edit_driver_view, name="edit_driver_page"),
    path("delete_driver/<int:driver_id>/", views.delete_driver_view, name="delete_driver_page"),

    path("car_pdf/", views.car_pdf_view, name="car_pdf"),

    path("add_maintenance/", views.add_maintenance_view, name="add_maintenance_page"),
    path("edit_maintenance/<int:maintenance_id>/", views.edit_maintenance_view, name="edit_maintenance_page"),
    path("delete_maintenance/<int:maintenance_id>/", views.delete_maintenance_view, name="delete_maintenance_page"),

    # Public routes
    path("book/", views.public_home_view, name="public_home_page"),
    path("book/success/", views.booking_success_view, name="booking_success_page"),

    path("return_hiring/<int:hiring_id>/", views.return_hiring_view, name="return_hiring_page"),

    path("invoice/<int:hiring_id>/", views.hiring_invoice_view, name="hiring_invoice_page"),
    path("handover/<int:hiring_id>/", views.vehicle_handover_view, name="vehicle_handover_page"),

    path("admin_control/", views.admin_control_view, name="admin_control_page"),

    path("fleet_map/", views.fleet_map_view, name="fleet_map_page"),

    #urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)




