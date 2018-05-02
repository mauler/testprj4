from django.conf import settings
from django.db.models import F

from cards.accounting.models import Account

from issuer.db import IssuerDatabase
from issuer.service import IssuerService


class CardsIssuerDatabase(IssuerDatabase):

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

    def load_money(self, card_id, amount, currency):
        """Increases the balance attribute of a specific Account instance.

        :param card_id: The card unique identification
        :type card_id: str

        :param amount: Amount to be loaded
        :type amount: Decimal

        :param currency: Currency code, 3 char long.
        :type currency: str
        """
        if self.account_exists(card_id, currency):
            (Account.objects
                .filter(card_id=card_id, currency=currency)
                .update(balance=F('balance') + amount))


service = IssuerService(CardsIssuerDatabase(), settings.CURRENCIES)
