from flask import current_app as app
from .settings import API_KEY, API_SECRET, MERCHANT_ID
from uuid import uuid4
import time

import paypayopa

client = paypayopa.Client(auth=(API_KEY, API_SECRET), production_mode=False)
client.set_assume_merchant(MERCHANT_ID)

class PayPay:
	def create_qr_and_redirect(amount=None):
		if amount is not None:
			print(amount)
			merchant_payment_id = str(uuid4())

			request_data = {
				"merchantPaymentId": merchant_payment_id,
				"codeType": "ORDER_QR",
				"redirectUrl": app.config["HOST"]+"/pay_status",
				"redirectType": "WEB_LINK",
				"orderDescription": "Example - Content Test Shop",
				"orderItems": [{
					"name": "Test Product",
					"category": "Movie",
					"quantity": 1,
					"productId": "1000",
					"unitPrice": {
						"amount": 1000,
						"currency": "JPY"
					}
				}],
				"amount": {
					"amount": amount,
					"currency": "JPY"
				},
			}

			response = client.Code.create_qr_code(request_data)
			print(response['resultInfo'])
			
			qr_code_url = response['data']['url']
			return merchant_payment_id, qr_code_url
		return False
	
	def payment_status(merchant_payment_id):
		
		max_retries = 5
		retry_interval = 2  # seconds

		for _ in range(max_retries):
			payment_details = client.Code.get_payment_details(merchant_payment_id)
			status = payment_details['data']['status']

			if status == 'COMPLETED':
				return True
			elif status in ['FAILED', 'CANCELED']:
				return False
			
			time.sleep(retry_interval)

		return False