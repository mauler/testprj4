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
