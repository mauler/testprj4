from django.db import IntegrityError
from django.test import TestCase

from cards.accounting.models import Account, Transaction


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
        self.acc.transfers.create(amount=100, description='Bank Deposit')
        self.acc.transactions.create(settlement_amount=99,
                                     transaction_type=Transaction.PRESENTMENT,
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

    def test_account_transfers_balance(self):
        """Check if the summarize for Account transfers are being calculated
        properly."""
        self.acc.transfers.create(amount=100, description='Bank Deposit')

        self.assertEqual(
            Account.objects
            .filter(pk=self.acc.id)
            .transfers_balance()
            .get()
            .transfers_balance,
            100)

        self.acc.transfers.create(amount=-50, description='Money withdraw')

        self.assertEqual(
            Account.objects
            .filter(pk=self.acc.id)
            .transfers_balance()
            .get()
            .transfers_balance,
            50)

    def test_account_presentments_sum(self):
        self.acc.transactions.create(settlement_amount=99,
                                     transaction_type=Transaction.PRESENTMENT,
                                     merchant_mcc=0,
                                     billing_amount=99,
                                     transaction_amount=100)

        self.assertEqual(
            Account.objects
            .filter(pk=self.acc.id)
            .presentments_sum()
            .get()
            .presentments_sum,
            99)
