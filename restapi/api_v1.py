from django.conf.urls import url, include
from rest_framework.routers import DefaultRouter

from donkiesoauth2.views import DjangoUserViewSet

router = DefaultRouter(schema_title='DonkiesAPI')
router.register(r'users', DjangoUserViewSet)
# router.register(r'employees', business_views.EmployeeViewSet)
# router.register(r'company', business_views.CompanyViewSet)
# router.register(r'estimateitems', business_views.EstimateItemViewSet)
# router.register(r'estimates', business_views.EstimateViewSet)
# router.register(r'jobs', business_views.JobItemViewSet)
# router.register(r'payments', business_views.PaymentViewSet)
# router.register(r'changeorders', business_views.ChangeOrderViewSet)
# router.register(r'changeorderitems', business_views.ChangeOrderItemViewSet)

urlpatterns = [
        url(r'^', include(router.urls)),
        ]
