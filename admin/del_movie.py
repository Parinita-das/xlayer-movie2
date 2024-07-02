from bson import ObjectId
import tornado.web
import json
from con import Database 
from authorization.JwtConfiguration.auth import xenProtocol

class DeleteMovieHandler(tornado.web.RequestHandler):
    movie_table = Database.db['movies'] 
    usersTable = Database.db['user']

    @xenProtocol
    async def post(self):
        code = 1000
        status = False
        message = ''

        try:
            user = await self.usersTable.find_one({'_id': ObjectId(self.user_id)})
            print(user)
            if not user:
                message = 'User not found'
                code = 4002
                raise tornado.web.HTTPError(400, reason=message)

            mUserRole = user.get('role')
            print(mUserRole)
            if mUserRole != 'admin':
                message = 'Unauthorized access'
                code = 4030
                raise tornado.web.HTTPError(403, reason=message)
            
            request_data = json.loads(self.request.body)
            movie_title = request_data.get('title')

            movie_table = Database.db['movies']

            delete_result = await movie_table.delete_one({'title': movie_title})

            if delete_result.deleted_count > 0:
                code = 2000
                status = True
                message = "Movie deleted successfully"
            else:
                code = 1007
                message = "Movie not found or delete operation failed"
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