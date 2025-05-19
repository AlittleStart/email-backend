from flask import Flask, request, jsonify
from flask_cors import CORS
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import base64
import os

app = Flask(__name__)
CORS(app)

SENDER_EMAIL = "shashankab12@gmail.com"          # Replace with your Gmail
SENDER_PASSWORD = "sijq utqf jqea yzcw"          # Replace with your Gmail App Password

def send_email(recipient_emails, subject, body, attachments=[]):
    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as session:
            session.login(SENDER_EMAIL, SENDER_PASSWORD)

            for email in recipient_emails:
                message = MIMEMultipart()
                message['From'] = SENDER_EMAIL
                message['To'] = email
                message['Subject'] = subject

                # Anti-spam headers
                message['X-Priority'] = '3'
                message['X-Mailer'] = 'Custom Mailer'
                message['X-MSMail-Priority'] = 'Normal'

                message.attach(MIMEText(body, 'plain'))

                for attachment in attachments:
                    file_path = f"temp_{attachment['name']}"
                    with open(file_path, 'wb') as f:
                        f.write(base64.b64decode(attachment['content']))

                    with open(file_path, 'rb') as attach_file:
                        payload = MIMEBase('application', 'octet-stream')
                        payload.set_payload(attach_file.read())
                        encoders.encode_base64(payload)
                        payload.add_header('Content-Disposition', 'attachment', filename=attachment['name'])
                        message.attach(payload)

                    os.remove(file_path)

                text = message.as_string()
                session.sendmail(SENDER_EMAIL, email, text)

        return True
    except Exception as e:
        print(f"Error sending email: {e}")
        return False

@app.route('/send-emails', methods=['POST', 'OPTIONS'])
def send_emails():
    if request.method == 'OPTIONS':
        return jsonify({'status': 'ok'}), 200

    data = request.json
    try:
        success = send_email(
            data.get('emails', []),
            data.get('subject', ''),
            data.get('body', ''),
            data.get('attachments', [])
        )

        return jsonify({
            'success': success,
            'message': 'Emails sent successfully!' if success else 'Failed to send emails'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Server error: {str(e)}'
        }), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
