from django.db.models.functions import Coalesce
from django.db.models import Manager, QuerySet, Sum


class AccountManager(Manager):
    """Manager for Account model. """

    def get_queryset(self):
        return AccountManagerQuerySet(self.model, using=self._db)

    def balance(self, *ar, **kw):
        return self.get_queryset().balance(*ar, **kw)


class AccountManagerQuerySet(QuerySet):
    """ManagerQuerySet for Account model. """

    def balance(self):
        """Summarizes the transfers for the Account."""
        return self.annotate(balance=Coalesce(Sum('transfers__amount'), 0))
