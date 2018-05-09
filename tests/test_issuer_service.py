from unittest.mock import MagicMock
from unittest import TestCase

from issuer.db import InsufficientFunds, AuthorisationNotFound
from issuer.service import IssuerService


class IssuerServiceTests(TestCase):
    CARD_ID = 'CARD123'
    CURRENCY = 'BRL'

    TRANSACTION_ID = 'IDDQD666'

    MERCHANT_NAME = 'Game Store'
    MERCHANT_COUNTRY = 'BR'
    MERCHANT_MCC = 1234

    BILLING_AMOUNT = 100
    BILLING_CURRENCY = 'BRL'

    TRANSACTION_AMOUNT = 100
    TRANSACTION_CURRENCY = 'BRL'

    SETTLEMENT_AMOUNT = 100
    SETTLEMENT_CURRENCY = 'BRL'

    def setUp(self):
        self.db_mock = MagicMock()
        self.service = IssuerService(self.db_mock, [self.CURRENCY])

    def test_account_exists(self):
        # Ensure the account exists calls return False
        self.db_mock.account_exists.return_value = False

        # Call the load_money from the Service
        self.service.load_money(self.CARD_ID, 100, self.CURRENCY)

        # Create account should be called since the account doesn't exists
        self.db_mock.create_account.assert_called()

    def test_load_money_invalid_currency(self):
        """Tries to load money for a invalid currency. """

        with self.assertRaises(ValueError) as cm:
            self.service.load_money(self.CARD_ID, 100, 'INVALID_CURRENCY')

        self.assertEqual(cm.exception.args,
                         ('Currency "INVALID_CURRENCY" not available.', ))

    def test_make_authorisation(self):
        """Tests make authorisation. """

        # Authorisation for 200 BRL, should return False
        self.assertTrue(self.service.make_authorisation(
            self.CARD_ID,
            self.TRANSACTION_ID,
            self.MERCHANT_NAME,
            self.MERCHANT_COUNTRY,
            self.MERCHANT_MCC,
            self.BILLING_AMOUNT,
            self.BILLING_CURRENCY,
            self.TRANSACTION_AMOUNT,
            self.TRANSACTION_CURRENCY))

        self.db_mock.make_authorisation.assert_called_with(
            self.CARD_ID,
            self.TRANSACTION_ID,
            self.MERCHANT_NAME,
            self.MERCHANT_COUNTRY,
            self.MERCHANT_MCC,
            self.BILLING_AMOUNT,
            self.BILLING_CURRENCY,
            self.TRANSACTION_AMOUNT,
            self.TRANSACTION_CURRENCY)

    def test_make_authorisation_false(self):
        """Tests make authorisation. """

        # Authorisation should return InsufficientFunds
        self.db_mock.make_authorisation.side_effect = InsufficientFunds

        # Authorisation for 200 BRL, should return False
        self.assertFalse(self.service.make_authorisation(
            self.CARD_ID,
            self.TRANSACTION_ID,
            self.MERCHANT_NAME,
            self.MERCHANT_COUNTRY,
            self.MERCHANT_MCC,
            self.BILLING_AMOUNT,
            self.BILLING_CURRENCY,
            self.TRANSACTION_AMOUNT,
            self.TRANSACTION_CURRENCY))

    def test_set_presentment_authorisation_not_found(self):
        """Tests if error is raised when Authorisation doesn't exists. """

        # DB set presentment should return AuthorisationNotFound
        self.service._db.set_presentment.side_effect = AuthorisationNotFound

        with self.assertRaises(AuthorisationNotFound):
            self.service.set_presentment('INVALID-TRANSACTION',
                                         self.BILLING_AMOUNT,
                                         self.BILLING_CURRENCY)

    def test_set_presentment(self):
        """Tests normal authorisation to presentment call. """

        self.service.set_presentment(self.CARD_ID,
                                     self.BILLING_AMOUNT,
                                     self.BILLING_CURRENCY)

        self.db_mock.set_presentment.assert_called_with(self.CARD_ID,
                                                        self.BILLING_AMOUNT,
                                                        self.BILLING_CURRENCY)
