from django.urls import path
from .views import SignupView, me, VendorListView, DropshipperListView

urlpatterns = [
    path('signup/', SignupView.as_view()),
    path('me/', me),
    path('vendors/', VendorListView.as_view()),
    path('dropshippers/', DropshipperListView.as_view()),
]