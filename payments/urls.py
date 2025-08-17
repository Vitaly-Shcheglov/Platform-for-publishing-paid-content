from django.urls import path

from .views import PaymentCreateView, PaymentListView, stripe_webhook

app_name = "payments"

urlpatterns = [
    path("payments/", PaymentListView.as_view(), name="payment-list"),
    path("payments/create/", PaymentCreateView.as_view(), name="payment-create"),
    path("stripe-webhook/", stripe_webhook, name="stripe_webhook"),
]
