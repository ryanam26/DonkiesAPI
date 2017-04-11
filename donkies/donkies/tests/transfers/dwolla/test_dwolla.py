import pytest
from ...import base
from bank.models import Customer


class TestDwolla(base.Mixin):
    """
    Run tests from US server.
    """

    @pytest.mark.django_db
    def test_update_customers(self):
        Customer.objects.update_customers()
