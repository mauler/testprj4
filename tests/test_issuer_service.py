from unittest.mock import MagicMock
from unittest import TestCase

from issuer.service import IssuerService


class IssuerServiceTests(TestCase):
    CARD_ID = 'CARD123'
    CURRENCY = 'BRL'

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
