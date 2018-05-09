from django.conf import settings
from django.db import transaction

from cards.accounting.models import Account, Transaction, Batch

from issuer.db import (IssuerDatabase, InsufficientFunds, AccountNotFound,
                       AuthorisationNotFound, )
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
    ISSUER_CARD_ID = '__ISSUER_CARD_ID__'
    SCHEME_CARD_ID = '__SCHEME_CARD_ID__'

    def _get_issuer_account(self, currency):
        """Returns the Issuer account for a specific currency..

        :param card_id: The card unique identification
        :type card_id: str

        :param currency: Currency code, 3 char long.
        :type currency: str
        """

        # Tries to create the Account if it doesn't exists.
        account, created = (Account.objects
                            .get_or_create(card_id=self.ISSUER_CARD_ID,
                                           currency=currency))
        return account

    def _get_scheme_account(self, currency):
        """Returns the Scheme account for a specific currency..

        :param card_id: The card unique identification
        :type card_id: str

        :param currency: Currency code, 3 char long.
        :type currency: str
        """

        # Tries to create the Account if it doesn't exists.
        account, created = (Account.objects
                            .get_or_create(card_id=self.SCHEME_CARD_ID,
                                           currency=currency))
        return account

    def _make_presentment_batch(self, transaction):
        """Creates funds movement for a presentment.

        :param transaction: The transaction instance
        :type transaction: Transaction

        :returns: The batch created.
        :rtype: Batch
        """
        batch = Batch.objects.create()

        # Debits billing from cardholder account
        batch.journals.create(account=transaction.account,
                              amount=transaction.billing_amount * -1)

        # Credits the settlement into Schemer account
        acc = self._get_scheme_account(transaction.settlement_currency)
        batch.journals.create(account=acc,
                              amount=transaction.settlement_amount)

        # Credits profits into Issuer account
        profits = transaction.billing_amount - transaction.settlement_amount

        acc = self._get_issuer_account(transaction.settlement_currency)
        batch.journals.create(account=acc,
                              amount=profits)

        return batch

    def _make_transfer(self, debit_account, credit_account, amount):
        """Creates a Batch instance with Tranfer instances connected to
        represent duble check accouting.

        :param debit_account: The debit account
        :type debit_account: Account

        :param credit_account: The credit account
        :type credit_account: Account

        :param amount: The batch journal account
        :type amount: Decimal

        """
        batch = Batch.objects.create()

        # Double entry
        batch.journals.create(account=debit_account,
                              amount=amount * -1)

        batch.journals.create(account=credit_account,
                              amount=amount)

        return batch

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
        issuer_acc = self._get_issuer_account(currency)

        # Make funds transfer between accounts
        self._make_transfer(issuer_acc, acc, amount)

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

    @transaction.atomic
    def set_presentment(self, transaction_id, settlement_amount,
                        settlement_currency):
        """Tries to retrieve Authorisation Transaction  from the database,
        raises AuthorisationNotFound is none available.

        :param transaction_id:  Unique transaction id
        :type transaction_id: str

        :param settlement_amount: Amount on settlement.
        :type settlement_amount: Decimal

        :param settlement_currency: Settlement currency code, 3 char long.
        :type settlement_currency: str

        :raises: AuthorisationNotFound
        """
        try:
            tr = Transaction.objects.get(
                transaction_id=transaction_id,
                transaction_type=Transaction.AUTHORISATION)

        except Transaction.DoesNotExist:
            raise AuthorisationNotFound

        tr.transaction_type = Transaction.PRESENTMENT
        tr.settlement_amount = settlement_amount
        tr.settlement_currency = settlement_currency

        # Sets transaction to presentment
        tr.save(update_fields=['transaction_type',
                               'settlement_currency',
                               'settlement_amount'])

        # Creates transaction presentment batch in the same database
        # transaction
        tr.presentment_batch = self._make_presentment_batch(tr)
        tr.save(update_fields=['presentment_batch'])


service = IssuerService(CardsIssuerDatabase(), settings.CURRENCIES)
