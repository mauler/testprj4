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

    def transfers_balance(self, *ar, **kw):
        return self.get_queryset().transfers_balance(*ar, **kw)


class AccountManagerQuerySet(QuerySet):
    """ManagerQuerySet for Account model. """

    def balance(self):
        """Summarizes the balance for the Account."""
        balance = F('transfers_balance') - F('presentments_sum')
        return (self
                .transfers_balance()
                .presentments_sum()
                .annotate(balance=balance))

    def presentments_sum(self):
        """Summarizes the transactions presentments for the Account."""
        from cards.accounting.models import Transaction
        presentments = (Transaction.objects
                        .presentments()
                        .filter(account=OuterRef('pk')))
        subquery = Subquery(presentments.values('settlement_amount'),
                            output_field=DECIMAL_OUTPUT)
        presentments_sum = Sum(subquery)
        return self.annotate(presentments_sum=Coalesce(presentments_sum, 0))

    def transfers_balance(self):
        """Summarizes the transfers for the Account."""
        return self.annotate(
            transfers_balance=Coalesce(Sum('transfers__amount'), 0))


class TransactionManager(Manager):
    """Manager for Transaction model. """

    def get_queryset(self):
        return TransactionManagerQuerySet(self.model, using=self._db)

    def presentments(self, *ar, **kw):
        return self.get_queryset().presentments(*ar, **kw)

    def authorisations(self, *ar, **kw):
        return self.get_queryset().authorisations(*ar, **kw)


class TransactionManagerQuerySet(QuerySet):
    """ManagerQuerySet for Transaction model. """

    def presentments(self):
        """Filters presentment transactions."""
        return self.filter(transaction_type=self.model.PRESENTMENT)

    def authorisations(self):
        """Filters presentment transactions."""
        return self.filter(transaction_type=self.model.AUTHORISATION)
