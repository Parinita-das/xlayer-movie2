import json
import bcrypt
from bson.objectid import ObjectId
import tornado.web
from con import Database 
import jwt
import datetime
import time

SECRET_KEY = "Xlayer.in"

class LoginHandler(tornado.web.RequestHandler, Database):
    userTable = Database.db['user']
    sessionTable = Database.db['session']

    async def post(self):
        code = 4014
        status = False
        message = ''
        result = []
        jwt_token = None 

        try:
            # Parse the request body as JSON
            try:
                self.request.arguments = json.loads(self.request.body.decode())
            except Exception as e:
                code = 4024
                message = "Invalid JSON"
                raise Exception

            mEmail = self.request.arguments.get('email')
            mPassword = self.request.arguments.get('password')

            if not (mEmail and mPassword):
                code = 4037
                message = 'Email and password are required'
                raise Exception

            user = await self.userTable.find_one({'email': mEmail})
            if not user:
                code = 4049
                message = 'User not found'
                raise Exception

            # Ensure both mPassword and user['password'] are bytes-like objects
            if not bcrypt.checkpw(mPassword.encode(), user['password'].encode()):
                code = 4050
                message = 'Invalid password'
                raise Exception

            code = 1000
            status = True
            message = 'Login successfully'

            # Create session entry
            session_data = {
                'user_id': str(user['_id']),  
                'login_time': int(time.time()),
                'logout_time': None,
                'duration': None
            }
            result_in = await self.sessionTable.insert_one(session_data)
            session_id = str(result_in.inserted_id)

            # Generate JWT token
            payload = {
                'user_id': str(user['_id']),
                '_id': session_id,
                'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)
            }
            jwt_token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")

            result.append({
                'token': jwt_token 
            })
        except Exception as e:
            
            if not message:
                message = 'Internal Server Error'
                code = 1005
            print(f"Error: {e}")

        response = {
            'code': code,
            'message': message,
            'status': status
        }

        try:
            if result:
                response['result'] = result
            self.set_header("Content-Type", "application/json")
            self.write(json.dumps(response))
            self.finish()
        except Exception as e:
            print(f"Error in response: {e}")
            raise Exception('There is some issue with response')
