import logging

from django.utils.translation import ugettext as _
from django.db import models

log = logging.getLogger(__name__)

class StatsJob(models.Model):
    search_id = models.CharField(null=False, max_length=48)
    created_on = models.DateTimeField(auto_now=True)
    status = models.CharField(null=False, max_length=48)
    progress = models.IntegerField(_('Ingest progress'), null=True, default=None)
    error = models.CharField(_('Error message'), null=True, default=None, max_length=255)