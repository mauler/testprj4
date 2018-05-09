from django.db import IntegrityError
from django.test import TestCase

from cards.accounting.models import Account, Transaction, Batch


class ModelsTests(TestCase):
    def setUp(self):
        self.acc = Account.objects.create(card_id='card-brl',
                                          currency='BRL')

    def test_account_integrity(self):
        """An Account is considered uniques for card_id and currency
        together"""

        with self.assertRaises(IntegrityError):
            Account.objects.create(card_id='card-brl',
                                   currency='BRL')

    def test_account_balance(self):
        """Calculates the final balance based on tranasfers balance minus
        setlements sum."""
        batch = Batch.objects.create(description='Bank Deposit')

        self.acc.journals.create(amount=100, batch=batch)

        self.acc.transactions.create(settlement_amount=99,
                                     transaction_type=Transaction.AUTHORISATION,
                                     merchant_mcc=0,
                                     billing_amount=99,
                                     transaction_amount=100)

        self.assertEqual(
            Account.objects
            .filter(pk=self.acc.id)
            .balance()
            .get()
            .balance,
            1)

    def test_account_journals_sum(self):
        """Check if the summarize for Account journals are being calculated
        properly."""
        batch = Batch.objects.create(description='Bank Deposit')

        self.acc.journals.create(amount=100, batch=batch)

        self.assertEqual(
            Account.objects
            .filter(pk=self.acc.id)
            .journals_sum()
            .get()
            .journals_sum,
            100)

        self.acc.journals.create(amount=-50, batch=batch)

        self.assertEqual(
            Account.objects
            .filter(pk=self.acc.id)
            .journals_sum()
            .get()
            .journals_sum,
            50)
