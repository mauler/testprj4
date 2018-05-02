from django.conf import settings
from django.core.management.base import BaseCommand

from cards import issuer


class Command(BaseCommand):
    help = 'Loads money into an account.'

    def add_arguments(self, parser):
        parser.add_argument('cardholder', type=str)
        parser.add_argument('amount', type=float)
        parser.add_argument('currency',
                            type=str,
                            choices=settings.CURRENCIES)

    def handle(self, *args, **params):
        issuer.service.load_money(params['cardholder'],
                                  params['amount'],
                                  params['currency'])
        message = 'Loaded {amount} {currency} into Card {card_id}'
        self.stdout.write(self.style.SUCCESS(message.format(**params)))
