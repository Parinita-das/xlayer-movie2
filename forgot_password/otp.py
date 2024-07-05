import json
import random
import tornado.web
from email.mime.text import MIMEText
import smtplib
from con import Database
import time

SECRET_KEY = "Xlayer.in"

# Email configuration
smtp_server = "smtp.gmail.com"
smtp_port = 587
EMAIL_SENDER = "parinitaofficial95@gmail.com"  
EMAIL_PASSWORD = "mdzwgkyfcjircoky"   


class OTPHandler(tornado.web.RequestHandler, Database):
    userTable = Database.db['user']

    async def post(self):
        code = 4014
        status = False
        message = ''
        otp = None

        try:
            # Parse the request body as JSON
            try:
                self.request.arguments = json.loads(self.request.body.decode())
            except Exception as e:
                code = 4024
                message = "Invalid JSON"
                raise Exception

            mEmail = self.request.arguments.get('email')

            if not mEmail:
                code = 4037
                message = 'Email is required'
                raise Exception

            user = await self.userTable.find_one({'email': mEmail})
            if not user:
                code = 4049
                message = 'User not found'
                raise Exception

            # Generate a 6-digit OTP
            otp = str(random.randint(100000, 999999))

            # Update user document with OTP and expiration time
            await self.userTable.update_one(
                {'_id': user['_id']},
                {'$set': {'otp': otp, 'otp_expiry': time.time() + 300}}
            )

            # Send email
            email_subject = "Password Reset Request"
            email_message = f"Please use this OTP for password reset: {otp}"
            email_sent = send_email(mEmail, email_subject, email_message)

            if not email_sent:
                raise Exception("Failed to send password reset email")

            code = 1000
            status = True
            message = 'OTP sent successfully'

        except json.JSONDecodeError:
            message = 'Invalid JSON in request body'
            code = 4024
        except ValueError as ve:
            message = str(ve)
        except Exception as e:
            message = 'Internal Server Error'
            code = 1005

        response = {
            'code': code,
            'message': message,
            'status': status,
        }

        try:
            self.set_header("Content-Type", "application/json")
            self.write(response)
            self.finish()
        except Exception as e:
            message = 'There is some issue'
            code = 1006
            raise Exception



def send_email(to_email, subject, message):
    try:
        # Create the email message
        msg = MIMEText(message)
        msg["Subject"] = subject
        msg["From"] = EMAIL_SENDER
        msg["To"] = to_email

        # Send the email
        server = smtplib.SMTP('smtp.gmail.com', 587)  # Update SMTP server details
        server.starttls()
        server.login(EMAIL_SENDER, EMAIL_PASSWORD)
        server.sendmail(EMAIL_SENDER, to_email, msg.as_string())
        server.quit()

        return True
    except smtplib.SMTPException as e:
        print(f"Failed to send email: {str(e)}")
        return False
    except Exception as e:
        print(f"An unexpected error occurred: {str(e)}")
        return False