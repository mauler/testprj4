from django.db import models

from cards.accounting.managers import AccountManager


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
