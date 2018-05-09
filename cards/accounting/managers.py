from django.db.models.functions import Coalesce
from django.db.models import (
    Manager, QuerySet, Sum, F, OuterRef, Subquery, DecimalField)


DECIMAL_OUTPUT = DecimalField(decimal_places=2)


class AccountManager(Manager):
    """Manager for Account model. """

    def get_queryset(self):
        return AccountManagerQuerySet(self.model, using=self._db)

    def balance(self, *ar, **kw):
        return self.get_queryset().balance(*ar, **kw)


class AccountManagerQuerySet(QuerySet):
    """ManagerQuerySet for Account model. """

    def balance(self):
        """Summarizes the balance for the Account."""
        balance = (F('journals_sum') -
                   F('authorisations_sum'))
        return (self
                .journals_sum()
                .authorisations_sum()
                .annotate(balance=balance))

    def authorisations_sum(self):
        """Summarizes the transactions authorisations for the Account."""
        from cards.accounting.models import Transaction
        authorisations = (Transaction.objects
                          .authorisations()
                          .filter(account=OuterRef('pk')))
        subquery = Subquery(authorisations.values('billing_amount'),
                            output_field=DECIMAL_OUTPUT)
        authorisations_sum = Sum(subquery)
        return self.annotate(authorisations_sum=Coalesce(authorisations_sum,
                                                         0))

    def journals_sum(self):
        """Summarizes the journals for the Account."""
        journals_sum = Sum('journals__amount')
        return self.annotate(journals_sum=Coalesce(journals_sum, 0))


class TransactionManager(Manager):
    """Manager for Transaction model. """

    def get_queryset(self):
        return TransactionManagerQuerySet(self.model, using=self._db)

    def authorisations(self, *ar, **kw):
        return self.get_queryset().authorisations(*ar, **kw)


class TransactionManagerQuerySet(QuerySet):
    """ManagerQuerySet for Transaction model. """

    def authorisations(self):
        """Filters presentment transactions."""
        return self.filter(transaction_type=self.model.AUTHORISATION)
