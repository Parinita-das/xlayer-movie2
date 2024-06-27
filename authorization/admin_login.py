import tornado.web
import json
from con import Database  
class AdLoginHandler(tornado.web.RequestHandler, Database):
    admin_table = Database.db['admin']

    async def post(self):
        code = 1000
        status = False
        result = []
        message = ''

        try:
            # Parse the request body as JSON.
            try:
                self.request.arguments = json.loads(self.request.body.decode())
            except Exception as e:
                code = 1001
                message = "Invalid JSON"
                raise Exception

            username = self.request.arguments.get('username')
            password = self.request.arguments.get('password')

            query = {
                'username': username,
                'password': password
            }
            admin = await self.admin_table.find_one(query)

            if admin:
                code = 2000
                status = True
                message = "Login successful"
                result.append({
                    'adminId': str(admin['_id'])
                })
            else:
                code = 1002
                message = "Invalid username or password"
                raise Exception

        except Exception as e:
            code = 1003
            if not len(message):
                message = 'Internal error'
                print(e)
                raise Exception

        response = {
            'code': code,
            'message': message,
            'status': status,
        }

        try:
            if len(result):
                response['result'] = result
            self.write(response)
            self.finish()
        except Exception as e:
            message = 'There is some issue'
            code = 1004
            raise Exception