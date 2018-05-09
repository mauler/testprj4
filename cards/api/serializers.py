from functools import partial

from django.conf import settings

from rest_framework import serializers


CURRENCY_CHOICES = [(i, i) for i in settings.CURRENCIES]

DECIMAL_FIELD = partial(serializers.DecimalField,
                        decimal_places=2,
                        max_digits=11,
                        min_value=1,
                        coerce_to_string=False)


class AuthorisationSerializer(serializers.Serializer):
    """Serialization for Authorisation.

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

    :param transaction_amount: Transaction amount to be billed
    :type transaction_amount: Decimal

    :param transaction_currency: Transaction currency code, 3 char long.
    :type transaction_currency: str
    """

    card_id = serializers.CharField()

    transaction_id = serializers.CharField()

    merchant_name = serializers.CharField()

    merchant_country = serializers.CharField()

    merchant_mcc = serializers.IntegerField()

    billing_amount = DECIMAL_FIELD()

    billing_currency = serializers.ChoiceField(CURRENCY_CHOICES)

    transaction_amount = DECIMAL_FIELD()

    transaction_currency = serializers.ChoiceField(CURRENCY_CHOICES)


class PresentmentSerializer(serializers.Serializer):
    """Serialization for Authorisation.

    :param transaction_id:  Unique transaction id
    :type transaction_id: str

    :param settlement_amount: Settlement amount.
    :type settlement_amount: Decimal

    :param settlement_currency: Settlement currency code, 3 char long.
    :type settlement_currency: str
    """

    transaction_id = serializers.CharField()

    settlement_amount = DECIMAL_FIELD()

    settlement_currency = serializers.ChoiceField(CURRENCY_CHOICES)
