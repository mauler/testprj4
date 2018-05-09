import abc


class AuthorisationNotFound(Exception):
    """Raises when an Authorisation Transaction isn't available on the
    database."""


class InsufficientFunds(Exception):
    """Raised when an Account doesn't have enough funds."""


class AccountNotFound(Exception):
    """Raised when an Account doesn't exists on the database."""


class IssuerDatabase(metaclass=abc.ABCMeta):

    @abc.abstractmethod
    def account_exists(self, card_id, currency):
        """Check if an Account exists on the database.

        :param card_id: The card unique identification
        :type card_id: str

        :param amount: Amount to be loaded
        :type amount: Decimal

        :param currency: Currency code, 3 char long.
        :type currency: str

        :returns: bool -- If the Account is present over the database.
        """

    @abc.abstractmethod
    def load_money(self, card_id, amount, currency):
        """Load money into an existent Account at the database.

        :param card_id: The card unique identification
        :type card_id: str

        :param amount: Amount to be loaded
        :type amount: Decimal

        :param currency: Currency code, 3 char long.
        :type currency: str
        """

    @abc.abstractmethod
    def make_authorisation(self, card_id, transaction_id, merchant_name,
                           merchant_country, merchant_mcc, billing_amount,
                           billing_currency, transaction_amount,
                           transaction_currency):
        """Register a new authorisation into database, it's important to make
        sure balance checking and insertion is made at the same transaction.

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

        :raises: InsufficientFunds
        """

    def set_presentment(self, transaction_id, settlement_amount,
                        settlement_currency):
        """Sets a authorisation transaction to presentment.

        :param transaction_id:  Unique transaction id
        :type transaction_id: str

        :param settlement_amount: Amount on settlement.
        :type settlement_amount: Decimal

        :param settlement_currency: Settlement currency code, 3 char long.
        :type settlement_currency: str

        :raises: AuthorisationNotFound
        """
