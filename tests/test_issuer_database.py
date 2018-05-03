from django.test import TestCase

from cards.accounting.models import Account
from cards.issuer import CardsIssuerDatabase


class CardsIssuerDatabaseTests(TestCase):
    CARD_ID = 'CARD123'
    CURRENCY = 'BRL'

    def setUp(self):
        Account.objects.create(card_id=self.CARD_ID,
                               currency=self.CURRENCY)
        self.issuerdb = CardsIssuerDatabase()

    def test_account_exists(self):
        self.assertTrue(self.issuerdb.account_exists(self.CARD_ID,
                                                     self.CURRENCY))

    def test_load_money(self):
        self.issuerdb.load_money(self.CARD_ID, 100, self.CURRENCY)

        acc = Account.objects.balance().get(card_id=self.CARD_ID,
                                            currency=self.CURRENCY)

        self.assertEqual(acc.balance, 100)
