import json
import re
import bcrypt
import time
from bson.objectid import ObjectId
import tornado.web
from con import Database

class ResetHandler(tornado.web.RequestHandler, Database):
    userTable = Database.db['user']

    async def post(self):
        code = 4014
        status = False
        message = ''

        try:
            # Parse the request body as JSON
            try:
                self.request.arguments = json.loads(self.request.body.decode())
            except Exception as e:
                code = 4024
                message = "Invalid JSON"
                raise

            otp = self.request.arguments.get('otp')

            if not otp:
                code = 4037
                message = 'OTP is required'
                raise Exception
            

            mPassword = self.request.arguments.get('new_password')

            if not mPassword:
                code = 4041
                message = 'New Password is required'
                raise Exception

            # Password complexity requirements
            if len(mPassword) < 8:
                code = 4042
                message = 'Password should be at least 8 characters long'
                raise Exception

            if not any(char.islower() for char in mPassword):
                code = 4044
                message = 'Password should contain at least one lowercase letter'
                raise Exception

            if not any(char.isdigit() for char in mPassword):
                code = 4045
                message = 'Password should contain at least one digit'
                raise Exception
            
            mConfirmPassword = self.request.arguments.get('confirm_password')
            
            if not mConfirmPassword:
                code = 4048
                message = 'Confirm password is required'
                raise Exception


            if mPassword != mConfirmPassword:
                code = 1003
                message = 'Passwords do not match'
                raise Exception
             
            
            mEmail = self.request.arguments.get('email')

            user = await self.userTable.find_one({'otp': otp, 'email': mEmail})
            if not user:
                code = 4049
                message = 'Invalid OTP or Email'
                raise Exception

            # Verify OTP expiration time
            otp_expiry = user.get('otp_expiry')
            if not otp_expiry or time.time() > otp_expiry:
                code = 4052
                message = 'OTP has expired'
                raise Exception

            # Hash the new password
            hashed_password = bcrypt.hashpw(mPassword.encode(), bcrypt.gensalt())

            result = await self.userTable.update_one(
                {'_id': user['_id']},
                {'$set': {'password': hashed_password}, '$unset': {'otp': '', 'otp_expiry': ''}}
            )

            if result.modified_count > 0:
                code = 1000
                status = True
                message = 'Password reset successfully'
            else:
                code = 1005
                message = 'Failed to reset password'

        except Exception as e:
            message = 'Internal Server Error'
            code = 1005
            print(e)

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