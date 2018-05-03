from decimal import Decimal
import logging

from issuer.db import InsufficientFunds

LOGGER = logging.getLogger(__name__)


class IssuerService:
    def __init__(self, db, currencies):
        """Instances a new Issuer service.

        :param db: The database bridge.
        :type db: issuer.db.IssuerDatabase

        :param currencies: List of supported currencies.
        :type currencies: list
        """
        self._db = db
        self._currencies = currencies

    def _validate_currency(self, currency):
        """Validates if a currency is valid and can be used in the operation.

        :param currency: Currency code, 3 char long.
        :type currency: str

        :raises: ValueError
        """
        if currency not in self._currencies:
            raise ValueError('Currency "{}" not available.'.format(currency))

    def load_money(self, card_id, amount, currency):
        """Load money into an Account.

        :param card_id: The card unique identification
        :type card_id: str

        :param amount: Amount to be loaded
        :type amount: Decimal

        :param currency: Currency code, 3 char long.
        :type currency: str

        :raises: AccountNotFound, ValueError
        """
        self._validate_currency(currency)

        LOGGER.debug('Checking for account existence {}:{}',
                     card_id,
                     currency)

        if not self._db.account_exists(card_id, currency):
            LOGGER.warning('Account {}:{} not found.', card_id, currency)
            self._db.create_account(card_id, currency)
            LOGGER.info('Account {}:{} created.', card_id, currency)

        self._db.load_money(card_id, Decimal(amount), currency)
        LOGGER.info('{} {} loaded into account {}:{}.',
                    amount,
                    currency,
                    card_id,
                    currency)

    def make_authorisation(self, card_id, transaction_id, merchant_name,
                           merchant_country, merchant_mcc, billing_amount,
                           billing_currency, transaction_amount,
                           transaction_currency):
        """
        Makes an authorisation, it will fail if account doesn't have enough
        funds. If have enough funds are available it's recorded a new
        authorisation at the database.

        :param card_id: The card unique identification
        :type card_id: str

        :param transaction_id:  Unique transaction id
        :type transaction_id: str

        :param merchant_name: Merchant store name.
        :type merchant_name: str

        :param merchant_country: Merchant country abbreviated.
        :type merchant_country: str

        :param merchant_mcc: Merchant category code, 4 digits
        :type merchant_mcc: int

        :param billing_amount: Amount to be billed
        :type billing_amount: Decimal

        :param currency: Billing currency code, 3 char long.
        :type currency: str

        :param transaction_amount: Transaction to be billed
        :type transaction_amount: Decimal

        :param transaction_currency: Transaction currency code, 3 char long.
        :type transaction_currency: str

        :returns: bool -- If the authorisation was created successfully.
        """

        # Validates the Billing currency
        self._validate_currency(billing_currency)

        # Validates the transaction currency
        self._validate_currency(transaction_currency)

        LOGGER.debug('Trying authorisation transaction {} for account {}:{}',
                     transaction_id,
                     card_id,
                     billing_currency)

        try:
            self._db.make_authorisation(
                card_id,
                transaction_id,
                merchant_name,
                merchant_country,
                merchant_mcc,
                billing_amount,
                billing_currency,
                transaction_amount,
                transaction_currency)

            LOGGER.info(
                'Created authorisation transaction {} for account {}:{}',
                transaction_id,
                card_id,
                billing_currency)

        except InsufficientFunds:

            LOGGER.warning('Insufficient funds for authorisation '
                           'transaction {} to account {}:{}',
                           transaction_id,
                           card_id,
                           billing_currency)
            return False

        else:
            return True
