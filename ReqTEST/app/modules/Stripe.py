from flask import current_app as app
import os
import stripe
from .settings import C_API_KEY, C_SECRET
from uuid import uuid4
import time

stripe.api_key = C_SECRET

class PayMethods:
    @staticmethod
    def create_checkout_session(amount, email):
        print(email)
        customer = stripe.Customer.create(email=email)
        payment_method_types = ['card', 'link', 'konbini', "customer_balance"]
        try:
            # 動的に価格を作成
            price = stripe.Price.create(
                unit_amount=amount,
                currency="jpy",  # 通貨
                product_data={
                    "name": f"Product {uuid4()}",  # 一意の商品名
                },
            )

            # Checkoutセッションを作成
            session = stripe.checkout.Session.create(
                customer = customer.id,
                payment_method_types=payment_method_types,  # 支払い方法のリスト
                line_items=[{
                    'price': price.id,
                    'quantity': 1,
                }],
                mode='payment',
                payment_method_options={
                    "customer_balance": {
                        "funding_type": "bank_transfer",
                        "bank_transfer": {
                            "type": "jp_bank_transfer",  # 日本の銀行振込を指定
                        },
                    },
                },
                success_url= app.config["HOST"]+'/pay_status',  # 成功時のリダイレクトURL
                cancel_url= app.config["HOST"]+'/cancel',      # キャンセル時のリダイレクトURL
            )

            # CheckoutセッションのURLを返す
            return session.payment_intent, session.url

        except stripe.error.StripeError as e:
            # Stripeエラーのハンドリング
            return str(e), 400
        
def check_payment_status(payment_link_id):
    max_retries = 5
    retry_interval = 2  # seconds

    for _ in range(max_retries):
        try:
            # Payment Linkに関連するCheckout Sessionsを取得
            sessions = stripe.checkout.Session.list(payment_link=payment_link_id)

            if not sessions.data:
                # セッションがまだ作成されていない場合
                time.sleep(retry_interval)
                continue

            latest_session = sessions.data[0]
            payment_status = latest_session.payment_status

            if payment_status == 'paid':
                return True
            elif payment_status in ['unpaid', 'no_payment_required']:
                time.sleep(retry_interval)
                continue
            else:
                return False

        except stripe.error.StripeError as e:
            print(f"Error checking payment status: {str(e)}")
            return False

    # 最大リトライ回数に達した場合
    return False
