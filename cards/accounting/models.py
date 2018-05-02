from django.db import models


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
    card_id = models.CharField(max_length=10, db_index=True)

    currency = models.CharField(max_length=3, db_index=True)

    balance = models.DecimalField(max_digits=9,
                                  decimal_places=2,
                                  default=0)

    class Meta:
        unique_together = ('card_id', 'currency')
