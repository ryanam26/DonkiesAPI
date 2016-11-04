from django.conf.urls import url
from donkiesapp.views import login
from django.views.generic import TemplateView

urlpatterns = [
    url(r'^auth/login/', login),
    url(r'^test', TemplateView.as_view(template_name='test.html'))
]
