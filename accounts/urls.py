from django.urls import path
from .views import SignupView, MeView, VendorListView

urlpatterns = [
    path('signup/', SignupView.as_view(), name='signup'),
    path('me/', MeView.as_view(), name='me'),
    path('vendors/', VendorListView.as_view(), name='vendors'),
]