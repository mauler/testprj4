from django.db import models

from cards.accounting.managers import AccountManager, TransactionManager


class Account(models.Model):
    """Holds account/card balance for a specific currency. An Account it's
    unique based on card_id and currency.

    :param card_id: The card identification string
    :type card_id: str

    :param currency: The account currency code, 3 characters lengh
    :type currency: str

    :param balance: The consolided balance
    :type balance: Decimal
    """
    objects = AccountManager()

    card_id = models.CharField(max_length=10, db_index=True)

    currency = models.CharField(max_length=3, db_index=True)

    class Meta:
        unique_together = ('card_id', 'currency')


class Transfer(models.Model):
    """Holds generic transfer to an Account debit or credit.

    :params account: The transfer Account
    :type account: Account

    :param description: Generic description of the transfer
    :type description: str

    :param amount: The amount, raw value to be summarized as balance.
    :type amount: Decimal
    """
    account = models.ForeignKey('Account',
                                related_name='transfers',
                                on_delete=models.CASCADE)

    description = models.TextField()

    amount = models.DecimalField(max_digits=9,
                                 decimal_places=2)

    creation_date = models.DateTimeField(auto_now_add=True)

    modification_date = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('creation_date', )


class Transaction(models.Model):
    """Holds cards transactions. A Transaction can be an authorisation or
    either a presentment.

    :params account: The transfer Account
    :type account: Account

    :param transaction_id: Transaction unique ID.
    :type description: str

    :param transaction_type: Current status/type of the transaction.
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

    :param settlement_amount: Amount on settlement
    :type settlement_amount: Decimal

    :param settlement_currency: Settlement currency code, 3 char long.
    :type settlement_currency: str

    """
    AUTHORISATION = 'a'
    PRESENTMENT = 'p'
    TRANSACTION_TYPE_CHOICES = (
        (AUTHORISATION, 'authorisation'),
        (PRESENTMENT, 'presentment'),
    )

    objects = TransactionManager()

    account = models.ForeignKey('Account',
                                related_name='transactions',
                                on_delete=models.SET_NULL,
                                null=True)

    transaction_id = models.CharField(db_index=True,
                                      max_length=10)

    transaction_type = models.CharField(db_index=True,
                                        default=AUTHORISATION,
                                        max_length=1,
                                        choices=TRANSACTION_TYPE_CHOICES)

    merchant_name = models.CharField(max_length=100)

    merchant_country = models.CharField(max_length=5)

    merchant_mcc = models.PositiveIntegerField()

    billing_amount = models.DecimalField(max_digits=9,
                                         decimal_places=2)

    billing_currency = models.CharField(max_length=3)

    transaction_amount = models.DecimalField(max_digits=9,
                                             decimal_places=2)

    transaction_currency = models.CharField(max_length=3)

    settlement_amount = models.DecimalField(max_digits=9,
                                            decimal_places=2,
                                            null=True)

    settlement_currency = models.CharField(max_length=3,
                                           null=True)

    creation_date = models.DateTimeField(auto_now_add=True)

    modification_date = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('creation_date', )

    def __str__(self):
        return '{} => {}'.format(
            self.transaction_id,
            self.get_transaction_type_display())
