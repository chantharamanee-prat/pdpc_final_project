
from home.models import TnxPdpaResult
from django.utils.translation import gettext_lazy as _


class PDPAAuditReport(TnxPdpaResult):

    class Meta:
        proxy = True
        verbose_name        = _("PDPA Audit Report")
        verbose_name_plural = _("PDPA Audit Reports")