from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status

from cards.api.serializers import AuthorisationSerializer
from cards import issuer
from issuer.db import AccountNotFound


class AuthorisationView(APIView):

    def post(self, request, format=None):
        serializer = AuthorisationSerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.data
            try:
                success = issuer.service.make_authorisation(
                    card_id=data['card_id'],
                    transaction_id=data['transaction_id'],
                    merchant_name=data['merchant_name'],
                    merchant_country=data['merchant_country'],
                    merchant_mcc=data['merchant_mcc'],
                    billing_amount=data['billing_amount'],
                    billing_currency=data['billing_currency'],
                    transaction_amount=data['transaction_amount'],
                    transaction_currency=data['transaction_currency'])

            except AccountNotFound:
                return Response(status=status.HTTP_404_NOT_FOUND)

            else:
                if success:
                    return Response(status=status.HTTP_201_CREATED)

                else:
                    return Response(status=status.HTTP_403_FORBIDDEN)
        else:
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)
