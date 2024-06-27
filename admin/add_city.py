import tornado.web
import json
from con import Database

class AddCityHandler(tornado.web.RequestHandler, Database):
    city_table = Database.db['city'] 
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

            city_name = self.request.arguments.get('city')

            if not city_name:
                message = 'city is required'
                code = 6001
                raise Exception(message)
            
            elif not isinstance(city_name, str):
                message = 'Invalid city format'
                code = 6002
                raise Exception(message)
        
            elif len(city_name) > 30:
                message = 'Length should be within 30'
                code = 6003
                raise Exception

            country_name = self.request.arguments.get('country')

            if not country_name:
                message = 'country is required'
                code = 7001
                raise Exception(message)

            elif country_name != 'India':
                message = 'Only "India" is allowed as country name'
                code = 7002
                raise Exception(message)

            city_data = {
                'city': city_name,
                'country': country_name,
            }

            city_result = await self.city_table.insert_one(city_data)

            if city_result.inserted_id:
                code = 2000
                status = True
                message = "City added successfully"
                result.append({
                    'cityId': str(city_result.inserted_id)
                })
            else:
                code = 1006
                message = "Failed to add city"
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