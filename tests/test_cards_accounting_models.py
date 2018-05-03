from django.db import IntegrityError
from django.test import TestCase

from cards.accounting.models import Account


class ModelsTests(TestCase):

    def test_account_integrity(self):
        """An Account is considered uniques for card_id and currency
        together"""
        Account.objects.create(card_id='card-brl',
                               currency='BRL')

        with self.assertRaises(IntegrityError):
            Account.objects.create(card_id='card-brl',
                                   currency='BRL')

    def test_account_balance(self):
        """Check if the summarize for Account transfers are being calculated
        properly."""
        acc = Account.objects.create(card_id='card-brl',
                                     currency='BRL')

        acc.transfers.create(amount=100, description='Bank Deposit')

        self.assertEqual(
            Account.objects.filter(pk=acc.id).balance().get().balance, 100)

        acc.transfers.create(amount=-50, description='Money withdraw')

        self.assertEqual(
            Account.objects.filter(pk=acc.id).balance().get().balance, 50)
