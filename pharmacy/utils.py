import requests
import json
from decouple import config

def make_paypal_payment(amount, currency, return_url, cancel_url):
    client_id = config("PAYPAL_ID")
    secret = config("PAYPAL_SECRET")
    url = config("PAYPAL_BASE_URL")

    token_url = f"{url}/v1/oauth2/token"
    payment_url = f"{url}/v1/payments/payment"

    # Request access token
    token_payload = {'grant_type': 'client_credentials'}
    token_headers = {'Accept': 'application/json', 'Accept-Language': 'en_US'}
    token_response = requests.post(token_url, auth=(client_id, secret), data=token_payload, headers=token_headers)

    if token_response.status_code != 200:
        return False, "Failed to authenticate with PayPal API", None

    access_token = token_response.json()['access_token']

    payment_payload = {
        'intent': 'sale',
        'payer': {'payment_method': 'paypal'},
        'transactions': [{
            'amount': {'total': str(amount), 'currency': currency},
            'description': 'Service payment'
        }],
        'redirect_urls': {
            'return_url': return_url,
            'cancel_url': cancel_url
        }
    }


    # Create payment request
    payment_headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {access_token}'
    }

    payment_response = requests.post(payment_url, data=json.dumps(payment_payload), headers=payment_headers)

    if payment_response.status_code != 201:
        return False, "Failed to create PayPal payment", None

    payment_id = payment_response.json()['id']
    approval_url = next(link['href'] for link in payment_response.json()['links'] if link['rel'] == 'approval_url')

    return True, payment_id, approval_url


def verify_paypal_payment(payment_id):
    client_id = config("PAYPAL_ID")
    secret = config("PAYPAL_SECRET")
    url = config("PAYPAL_BASE_URL")

    token_url = f"{url}/v1/oauth2/token"
    payment_url = f"{url}/v1/payments/payment"

    # Request access token
    token_payload = {'grant_type': 'client_credentials'}
    token_headers = {'Accept': 'application/json', 'Accept-Language': 'en_US'}
    token_response = requests.post(token_url, auth=(client_id, secret), data=token_payload, headers=token_headers)

    if token_response.status_code != 200:
        return False

    access_token = token_response.json()['access_token']

    # Retrieve payment details
    payment_headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {access_token}'
    }

    payment_details_url = f"{payment_url}/{payment_id}"
    payment_details_response = requests.get(payment_details_url, headers=payment_headers)

    if payment_details_response.status_code != 200:
        return False

    payment_status = payment_details_response.json()['state']
    return payment_status == 'approved'
