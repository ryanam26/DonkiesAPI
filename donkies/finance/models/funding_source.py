from web.models import ActiveModel, ActiveManager
from django.db import models

from web.models.user import User


class FundingSource(ActiveModel):
    user = models.ForeignKey(User, related_name='funding_sources_user')
    funding_sources_url = models.CharField(max_length=255, blank=True,
                                           null=True)
