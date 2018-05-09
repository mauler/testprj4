from django.urls import reverse_lazy

from rest_framework import status
from rest_framework.test import APITestCase, APIRequestFactory

from cards.accounting.models import Account, Batch
from cards.api.views import AuthorisationView


class AuthorisationTests(APITestCase):
    AUTHORISATION_URL = reverse_lazy('authorisation')

    CARD_ID = 'CARD123'
    CURRENCY = 'BRL'

    TRANSACTION_ID = 'IDDQD666'

    MERCHANT_NAME = 'Game Store'
    MERCHANT_COUNTRY = 'BR'
    MERCHANT_MCC = 1234

    BILLING_AMOUNT = 100
    BILLING_CURRENCY = 'BRL'

    TRANSACTION_AMOUNT = 100
    TRANSACTION_CURRENCY = 'BRL'

    POST_DATA = {
        'card_id': CARD_ID,
        'transaction_id': TRANSACTION_ID,
        'merchant_name': MERCHANT_NAME,
        'merchant_country': MERCHANT_COUNTRY,
        'merchant_mcc': MERCHANT_MCC,
        'billing_amount': BILLING_AMOUNT,
        'billing_currency': BILLING_CURRENCY,
        'transaction_amount': TRANSACTION_AMOUNT,
        'transaction_currency': TRANSACTION_CURRENCY,
    }

    def _create_account(self):
        Account.objects.create(card_id=self.CARD_ID,
                               currency=self.BILLING_CURRENCY)

    def _add_funds(self, amount=BILLING_AMOUNT):
        acc, nil = Account.objects.get_or_create(
            card_id=self.CARD_ID,
            currency=self.BILLING_CURRENCY)

        # Here we are loading funds into account in the wrong way.
        acc.journals.create(amount=amount, batch=Batch.objects.create())

    def setUp(self):
        self.factory = APIRequestFactory()
        self.view = AuthorisationView.as_view()

    def test_authorization_400_invalid_params(self):
        # NOTE: This test isn't optimal, it's necessary to test search field
        # behaviour.
        request = self.factory.post(self.AUTHORISATION_URL,
                                    {'invalid-fields': 'invalid-values'})
        response = self.view(request)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_authorization_404_account_not_found(self):
        request = self.factory.post(self.AUTHORISATION_URL, self.POST_DATA)
        response = self.view(request)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_authorization_201_success(self):

        self._create_account()
        self._add_funds()

        request = self.factory.post(self.AUTHORISATION_URL, self.POST_DATA)
        response = self.view(request)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_authorization_403_no_funds(self):

        self._create_account()

        request = self.factory.post(self.AUTHORISATION_URL, self.POST_DATA)
        response = self.view(request)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
