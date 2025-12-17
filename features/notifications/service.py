import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

load_dotenv()

class EmailService:
    def __init__(self):
        self.smtp_server = os.getenv("SMTP_SERVER")
        self.smtp_port = int(os.getenv("SMTP_PORT", 587))
        self.smtp_username = os.getenv("SMTP_USERNAME")
        self.smtp_password = os.getenv("SMTP_PASSWORD")

    def _generate_html_content(self, order_details):
        items_html = ""
        for item in order_details.get("items", []):
            items_html += f"""
            <tr>
                <td style="padding: 10px; border-bottom: 1px solid #ddd;">
                    <img src="{item.get('image_url', '')}" alt="{item['name']}" style="width: 50px; height: 50px; object-fit: cover; border-radius: 4px; vertical-align: middle; margin-right: 10px;">
                    {item['name']}
                </td>
                <td style="padding: 10px; border-bottom: 1px solid #ddd; text-align: center;">{item.get('quantity', 1)}</td>
                <td style="padding: 10px; border-bottom: 1px solid #ddd; text-align: right;">${item['price']:.2f}</td>
            </tr>
            """

        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #ddd; border-radius: 8px; background-color: #f9f9f9; }}
                .header {{ text-align: center; margin-bottom: 20px; }}
                .header h1 {{ margin: 0; color: #2c3e50; }}
                .order-details {{ margin-bottom: 20px; background: white; padding: 15px; border-radius: 4px; }}
                .items-table {{ width: 100%; border-collapse: collapse; margin-bottom: 20px; background: white; }}
                .items-table th {{ padding: 10px; border-bottom: 2px solid #2c3e50; text-align: left; }}
                .footer {{ text-align: center; font-size: 12px; color: #777; margin-top: 20px; }}
                .total {{ text-align: right; font-size: 18px; font-weight: bold; margin-top: 10px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Order Confirmation</h1>
                </div>
                <p>Dear Customer,</p>
                <p>Thank you for your purchase via SalesMate! Here are your order details:</p>
                
                <div class="order-details">
                    <p><strong>Order ID:</strong> {order_details.get('order_id')}</p>
                    <p><strong>Payment ID:</strong> {order_details.get('payment_id')}</p>
                    <p><strong>Date:</strong> {order_details.get('created_at')}</p>
                </div>

                <table class="items-table">
                    <thead>
                        <tr>
                            <th>Item</th>
                            <th style="text-align: center;">Qty</th>
                            <th style="text-align: right;">Price</th>
                        </tr>
                    </thead>
                    <tbody>
                        {items_html}
                    </tbody>
                </table>
                
                <div class="total">
                    Total Amount: ${order_details.get('total_amount'):.2f}
                </div>

                <div class="footer">
                    <p>SalesMate Fashion Store</p>
                    <p>If you have any questions, please contact support.</p>
                </div>
            </div>
        </body>
        </html>
        """

    def send_order_confirmation(self, to_email: str, order_details: dict):
        subject = f"Order Confirmation - Order #{order_details.get('order_id')}"
        html_content = self._generate_html_content(order_details)

        if not (self.smtp_server and self.smtp_username and self.smtp_password):
            print("WARNING: SMTP credentials not found. Falling back to log.")
            print(f"--- [MOCK EMAIL] To: {to_email} ---")
            print(f"Subject: {subject}")
            print("Content: HTML Content Generated (Check code for layout)")
            print("-------------------------------------")
            return True

        msg = MIMEMultipart()
        msg['From'] = self.smtp_username
        msg['To'] = to_email
        msg['Subject'] = subject
        msg.attach(MIMEText(html_content, 'html'))

        try:
            print(f"Connecting to {self.smtp_server}:{self.smtp_port}...")
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.smtp_username, self.smtp_password)
            server.sendmail(self.smtp_username, to_email, msg.as_string())
            server.quit()
            print(f"✅ Email sent successfully to {to_email}")
            return True
        except Exception as e:
            print(f"❌ Failed to send email: {e}")
            return False
