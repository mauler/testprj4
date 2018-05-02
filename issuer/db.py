import abc


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
