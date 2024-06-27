import tornado.web
import json
from con import Database
from bson import json_util

class CityDropdownHandler(tornado.web.RequestHandler, Database):
    
    city_table = Database.db['city']  
    userTable = Database.db['user']

    #.
    
    async def get(self):
        code = 4000
        status = False
        result = []
        message = ''

        try:
            cities = await self.city_table.find({}, {'city': 1}).to_list(length=None)

            if cities:
                result = [city['city'] for city in cities]

                message = 'Cities fetched successfully'
                code = 2000
                status = True
            else:
                message = 'No cities found'
                code = 4002

        except Exception as e:
            message = 'Internal server error'
            code = 5010
            print(e)

        response = {
            'code': code,
            'message': message,
            'status': status,
            'result': result
        }

        try:
            self.set_header('Content-Type', 'application/json')
            self.write(json.dumps(response, default=json_util.default))
            await self.finish()

        except Exception as e:
            print(e)
            message = 'There is some issue'
            code = 5011
            raise Exception