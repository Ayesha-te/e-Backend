from django.urls import path
from .views import SignupView, me, VendorListView

urlpatterns = [
    path('signup/', SignupView.as_view()),
    path('me/', me),
    path('vendors/', VendorListView.as_view()),
]