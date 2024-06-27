import tornado.web
import json
from con import Database 
from bson import ObjectId

class DeleteCityHandler(tornado.web.RequestHandler):
    admin_table = Database.db['admin']
    city_table = Database.db['city'] 

    async def post(self):
        code = 1000
        status = False
        message = ''

        try:
            # Parse request body as JSON.
            request_data = json.loads(self.request.body)
            city_name = request_data.get('city')

            city_table = Database.db['city']  

            # Delete the city and all associated objects
            delete_result = await city_table.delete_many({'city': city_name})

            if delete_result.deleted_count > 0:
                code = 2000
                status = True
                message = "City deleted successfully"
            else:
                code = 1007
                message = "City not found"
                raise Exception

        except Exception as e:
            code = 1003
            message = 'Internal error'
            print(e)

        response = {
            'code': code,
            'message': message,
            'status': status,
        }

        self.write(response)
        self.finish()