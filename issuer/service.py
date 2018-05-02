from decimal import Decimal
import logging


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

    def load_money(self, card_id, amount, currency):
        """Load money into an Account.

        :param card_id: The card unique identification
        :type card_id: str

        :param amount: Amount to be loaded
        :type amount: Decimal

        :param currency: Currency code, 3 char long.
        :type currency: str

        :raises: AccountNotFound
        """
        if currency not in self._currencies:
            raise ValueError('Currency "{}" not available.'.format(currency))

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
