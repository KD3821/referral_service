from django.urls import path
from .views import CodeView, VerificationView


urlpatterns = [
    path('code', CodeView.as_view(), name='code'),
    path('verify', VerificationView.as_view(), name='verification')
]
