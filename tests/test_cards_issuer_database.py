from django.test import TestCase

from cards.accounting.models import Account, Transaction
from cards.issuer import CardsIssuerDatabase, account_not_found
from issuer.db import InsufficientFunds, AccountNotFound, AuthorisationNotFound


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
    MERCHANT_MCC = 1234

    TRANSACTION_AMOUNT = 100
    TRANSACTION_CURRENCY = 'BRL'

    BILLING_AMOUNT = 100
    BILLING_CURRENCY = 'BRL'

    SETTLEMENT_AMOUNT = 95
    SETTLEMENT_CURRENCY = 'BRL'

    PROFITS = BILLING_AMOUNT - SETTLEMENT_AMOUNT

    def setUp(self):
        self.acc = Account.objects.create(card_id=self.CARD_ID,
                                          currency=self.CURRENCY)

        self.issuerdb = CardsIssuerDatabase()

    def test_set_presentment_authorisation_not_found(self):
        """ Tests AuthorisationNotFound raising. """
        with self.assertRaises(AuthorisationNotFound):
            self.issuerdb.set_presentment(self.TRANSACTION_ID,
                                          self.SETTLEMENT_AMOUNT,
                                          self.SETTLEMENT_CURRENCY)

    def test_set_presentment(self):
        """ Tests a set presentment operation, check if all Accouting movements
        are properly created. """

        # Load moneys into account
        self.issuerdb.load_money(self.CARD_ID,
                                 self.BILLING_AMOUNT,
                                 self.BILLING_CURRENCY)
        # Makes the authorisation
        self.issuerdb.make_authorisation(
            self.CARD_ID,
            self.TRANSACTION_ID,
            self.MERCHANT_NAME,
            self.MERCHANT_COUNTRY,
            self.MERCHANT_MCC,
            self.BILLING_AMOUNT,
            self.BILLING_CURRENCY,
            self.TRANSACTION_AMOUNT,
            self.TRANSACTION_CURRENCY)

        # Sets the presentment
        self.issuerdb.set_presentment(self.TRANSACTION_ID,
                                      self.SETTLEMENT_AMOUNT,
                                      self.SETTLEMENT_CURRENCY)

        tr = Transaction.objects.get(transaction_id=self.TRANSACTION_ID)
        # Check if transaction fields were updated
        self.assertEqual(tr.transaction_type, Transaction.PRESENTMENT)
        self.assertEqual(tr.settlement_amount, self.SETTLEMENT_AMOUNT)
        self.assertEqual(tr.settlement_currency, self.SETTLEMENT_CURRENCY)

        # Check if the accouting funds movement was created
        self.assertIsNotNone(tr.presentment_batch)

        # Check accounts balances
        accounts = Account.objects.balance()

        # The cardholder account should be empty
        self.assertEqual(accounts.get(pk=self.acc.id).balance, 0)

        # The scheme account should have the settlement amount
        self.assertEqual(accounts.get(pk=self
                                      .issuerdb
                                      ._get_scheme_account(self
                                                           .SETTLEMENT_CURRENCY)
                                      .id)
                         .balance,
                         self.SETTLEMENT_AMOUNT)

        # The issuer account should have the profits amount, sums the initial
        # loaded money for the card holder
        self.assertEqual(accounts.get(pk=self
                                      .issuerdb
                                      ._get_issuer_account(self
                                                           .SETTLEMENT_CURRENCY)
                                      .id)
                         .balance + self.BILLING_AMOUNT,
                         self.PROFITS)

    def test_get_scheme_account(self):
        acc = self.issuerdb._get_scheme_account(self.BILLING_CURRENCY)
        self.assertEqual(acc.currency, self.BILLING_CURRENCY)
        self.assertEqual(acc.card_id, CardsIssuerDatabase.SCHEME_CARD_ID)

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
                self.MERCHANT_MCC,
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
            self.MERCHANT_MCC,
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
