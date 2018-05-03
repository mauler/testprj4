from django.test import TestCase

from cards.accounting.models import Account
from cards.issuer import CardsIssuerDatabase, account_not_found
from issuer.db import InsufficientFunds, AccountNotFound


class DecoratorTests(TestCase):

    @account_not_found
    def _raise_exception(self):
        raise Account.DoesNotExist

    def test_account_not_found(self):
        with self.assertRaises(AccountNotFound):
            self._raise_exception()


class CardsIssuerDatabaseTests(TestCase):
    CARD_ID = 'CARD123'
    CURRENCY = 'BRL'

    TRANSACTION_ID = 'IDDQD666'

    MERCHANT_NAME = 'Game Store'
    MERCHANT_COUNTRY = 'BR'
    MERCHAN_MCC = 1234

    BILLING_AMOUNT = 100
    BILLING_CURRENCY = 'BRL'

    TRANSACTION_AMOUNT = 100
    TRANSACTION_CURRENCY = 'BRL'

    SETTLEMENT_AMOUNT = 100
    SETTLEMENT_CURRENCY = 'BRL'

    def setUp(self):
        self.acc = Account.objects.create(card_id=self.CARD_ID,
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

    def test_make_authorisation_insuficient_funds(self):
        with self.assertRaises(InsufficientFunds):
            self.issuerdb.make_authorisation(
                self.CARD_ID,
                self.TRANSACTION_ID,
                self.MERCHANT_NAME,
                self.MERCHANT_COUNTRY,
                self.MERCHAN_MCC,
                self.BILLING_AMOUNT,
                self.BILLING_CURRENCY,
                self.TRANSACTION_AMOUNT,
                self.TRANSACTION_CURRENCY)

    def test_make_authorisation(self):
        # Load money into account
        self.issuerdb.load_money(self.CARD_ID,
                                 self.BILLING_AMOUNT,
                                 self.BILLING_CURRENCY)

        # Create authorisation
        self.issuerdb.make_authorisation(
            self.CARD_ID,
            self.TRANSACTION_ID,
            self.MERCHANT_NAME,
            self.MERCHANT_COUNTRY,
            self.MERCHAN_MCC,
            self.BILLING_AMOUNT,
            self.BILLING_CURRENCY,
            self.TRANSACTION_AMOUNT,
            self.TRANSACTION_CURRENCY)

        # Check the Transaction created
        self.assertQuerysetEqual(
            self.acc.transactions.authorisations(),
            ['<Transaction: {} => authorisation>'.format(self.TRANSACTION_ID)])

        # Check the authorisation sum
        self.assertEqual(
            Account.objects
            .filter(id=self.acc.id)
            .balance()
            .get()
            .authorisations_sum,
            self.BILLING_AMOUNT)

        # Check the new balance
        self.assertEqual(
            Account.objects.filter(id=self.acc.id).balance().get().balance,
            0)
