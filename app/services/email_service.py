import logging
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from app.config import EMAIL_FROM, SMTP_HOST, SMTP_PASSWORD, SMTP_PORT, SMTP_USER

logger = logging.getLogger(__name__)


def send_invoice_email(bill_data: dict) -> None:
    """
    Send an invoice email to the customer. Called as a FastAPI BackgroundTask
    so it runs asynchronously after the response is returned.
    """
    if not SMTP_USER or not SMTP_PASSWORD:
        logger.warning(
            "SMTP not configured. Invoice for %s logged instead of emailed.",
            bill_data["customer_email"],
        )
        logger.info("Invoice data: %s", bill_data)
        return

    customer_email = bill_data["customer_email"]
    html = _build_invoice_html(bill_data)

    msg = MIMEMultipart("alternative")
    msg["Subject"] = "Your Invoice - Billing System"
    msg["From"] = EMAIL_FROM
    msg["To"] = customer_email
    msg.attach(MIMEText(html, "html"))

    try:
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASSWORD)
            server.sendmail(EMAIL_FROM, customer_email, msg.as_string())
        logger.info("Invoice email sent to %s", customer_email)
    except Exception:
        logger.exception("Failed to send invoice email to %s", customer_email)


def _build_invoice_html(bill_data: dict) -> str:
    """Build the HTML body for the invoice email."""
    items_rows = ""
    for item in bill_data["items"]:
        items_rows += (
            "<tr>"
            f"<td>{item['product_id']}</td>"
            f"<td>{item['unit_price']:.2f}</td>"
            f"<td>{item['quantity']}</td>"
            f"<td>{item['purchase_price']:.2f}</td>"
            f"<td>{item['tax_percentage']:.2f}%</td>"
            f"<td>{item['tax_amount']:.2f}</td>"
            f"<td>{item['total_price']:.2f}</td>"
            "</tr>"
        )

    denom_rows = ""
    for val, count in bill_data["balance_denominations"]:
        denom_rows += f"<tr><td>{val}:</td><td>{count}</td></tr>"

    return f"""
    <html>
    <body>
        <h2>Invoice</h2>
        <p><strong>Customer Email:</strong> {bill_data['customer_email']}</p>
        <table border="1" cellpadding="5" cellspacing="0">
            <tr>
                <th>Product ID</th><th>Unit Price</th><th>Quantity</th>
                <th>Purchase Price</th><th>Tax %</th>
                <th>Tax Payable</th><th>Total Price</th>
            </tr>
            {items_rows}
        </table>
        <br>
        <p><strong>Total price without tax:</strong> {bill_data['total_without_tax']:.2f}</p>
        <p><strong>Total tax payable:</strong> {bill_data['total_tax']:.2f}</p>
        <p><strong>Net price:</strong> {bill_data['net_price']:.2f}</p>
        <p><strong>Rounded down value:</strong> {bill_data['rounded_net_price']:.2f}</p>
        <p><strong>Balance payable to customer:</strong> {bill_data['balance']:.2f}</p>
        <h3>Balance Denomination:</h3>
        <table>{denom_rows}</table>
    </body>
    </html>
    """
