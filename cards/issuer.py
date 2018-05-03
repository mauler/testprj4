from django.conf import settings
from django.db import transaction

from cards.accounting.models import Account, Transaction

from issuer.db import IssuerDatabase, InsufficientFunds, AccountNotFound
from issuer.service import IssuerService


def account_not_found(fn):
    """Decorates a function, when Account.DoesNotExist is catch
    and AccountNotFound is raised.

    :raises: AccountNotFound
    """
    def decorated(*args, **kwargs):
        try:
            return fn(*args, **kwargs)
        except Account.DoesNotExist:
            raise AccountNotFound

    return decorated


class CardsIssuerDatabase(IssuerDatabase):

    def _create_transaction(self, card_id, transaction_id, transaction_type,
                            merchant_name, merchant_country, merchant_mcc,
                            billing_amount, billing_currency,
                            transaction_amount, transaction_currency):
        """Create transaction for a specific Account.

        :param card_id: The card unique identification
        :type card_id: str

        :param transaction_id:  Unique transaction id
        :type transaction_id: str

        :param transaction_type:  Unique transaction id
        :type transaction_type: str

        :param merchant_name: Merchant store name.
        :type merchant_name: str

        :param merchant_country: Merchant country abbreviated.
        :type merchant_country: str

        :param merchant_mcc: Merchant category code, 4 digits
        :type merchant_mcc: int

        :param billing_amount: Amount to be billed
        :type billing_amount: Decimal

        :param billing_currency: Billing currency code, 3 char long.
        :type billing_currency: str

        :param transaction_amount: Transaction to be billed
        :type transaction_amount: Decimal

        :param transaction_currency: Transaction currency code, 3 char long.
        :type transaction_currency: str
        """
        acc = (Account.objects
               .balance()
               .get(card_id=card_id, currency=billing_currency))

        acc.transactions.create(
            transaction_id=transaction_id,
            transaction_type=transaction_type,
            merchant_name=merchant_name,
            merchant_country=merchant_country,
            merchant_mcc=merchant_mcc,
            billing_amount=billing_amount,
            billing_currency=billing_currency,
            transaction_amount=transaction_amount,
            transaction_currency=transaction_currency)

    @account_not_found
    def _get_balance(self, card_id, currency):
        """Returns Account balance

        :param card_id: The card unique identification
        :type card_id: str

        :param amount: Amount to be loaded
        :type amount: Decimal

        :param currency: Currency code, 3 char long.
        :type currency: str

        :returns: bool -- If the Account is present at the database.
        """
        balance = (Account.objects
                   .balance()
                   .get(card_id=card_id, currency=currency)
                   .balance)
        return balance

    def account_exists(self, card_id, currency):
        """Check if an Account model instance exists on the database.

        :param card_id: The card unique identification
        :type card_id: str

        :param amount: Amount to be loaded
        :type amount: Decimal

        :param currency: Currency code, 3 char long.
        :type currency: str

        :returns: bool -- If the Account is present at the database.
        """
        return Account.objects.filter(card_id=card_id,
                                      currency=currency).exists()

    @account_not_found
    def load_money(self, card_id, amount, currency):
        """Increases the balance attribute of a specific Account instance.

        :param card_id: The card unique identification
        :type card_id: str

        :param amount: Amount to be loaded
        :type amount: Decimal

        :param currency: Currency code, 3 char long.
        :type currency: str
        """
        acc = Account.objects.get(card_id=card_id, currency=currency)
        acc.transfers.create(amount=amount,
                             description='Money loaded from command-line')

    @transaction.atomic
    @account_not_found
    def make_authorisation(self, card_id, transaction_id, merchant_name,
                           merchant_country, merchant_mcc, billing_amount,
                           billing_currency, transaction_amount,
                           transaction_currency):
        """Check if Account has enough balance, if there is creates
        authorisation record into database. All operations in the same
        transaction.

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

        :param billing_currency: Billing currency code, 3 char long.
        :type billing_currency: str

        :param transaction_amount: Transaction to be billed
        :type transaction_amount: Decimal

        :param transaction_currency: Transaction currency code, 3 char long.
        :type transaction_currency: str

        :returns: bool -- If the authorisation was created successfully.

        :raises: InsufficientFunds
        """

        if self._get_balance(card_id, billing_currency) < billing_amount:
            raise InsufficientFunds

        else:
            self._create_transaction(
                card_id=card_id,
                transaction_id=transaction_id,
                transaction_type=Transaction.AUTHORISATION,
                merchant_name=merchant_name,
                merchant_country=merchant_country,
                merchant_mcc=merchant_mcc,
                billing_amount=billing_amount,
                billing_currency=billing_currency,
                transaction_amount=transaction_amount,
                transaction_currency=transaction_currency)


service = IssuerService(CardsIssuerDatabase(), settings.CURRENCIES)
