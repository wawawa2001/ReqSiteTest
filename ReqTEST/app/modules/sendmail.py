import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from .settings import FROM

class SendMail:
    
    def send_email(receiver_email, subject, body):
        # MIME形式のメッセージを作成
        msg = MIMEMultipart()
        msg['From'] = FROM
        msg['To'] = receiver_email
        msg['Subject'] = subject

        # メール本文を添付
        msg.attach(MIMEText(body, 'plain'))

        # SMTPサーバーに接続してメールを送信
        try:
            server = smtplib.SMTP("localhost")
            server.sendmail(FROM, receiver_email, msg.as_string())
            print("Email sent successfully!")
        except Exception as e:
            print(f"Failed to send email: {e}")
        finally:
            server.quit()
