import json
from bson.objectid import ObjectId
import tornado.web
import re
from datetime import datetime
from con import Database
from authorization.JwtConfiguration.auth import xenProtocol

class BookedSeatsHandler(tornado.web.RequestHandler, Database):
    bookingTable = Database.db['booking']
    movieTable = Database.db['movies']
    cityTable = Database.db['city']
    userTable = Database.db['user']

    @xenProtocol
    async def get(self):
        code = 1000
        status = False
        result = []
        message = ''

        try:
            movie_id = self.get_argument('movie_id', None)

            if not movie_id:
                message = 'movie_id is required'
                code = 1002
                raise Exception
            
            movie_id = ObjectId(movie_id)

            showdate = self.get_argument('showdate', None)

            if not showdate:
                message = 'showdate is required'
                code = 1002
                raise Exception
            try:
                date_obj = datetime.strptime(showdate, '%Y-%m-%d').date()
            except ValueError:
                message = 'Invalid date format, should be YYYY-MM-DD'
                code = 1005
                raise Exception
            
            showtime = self.get_argument('showtime', None)

            if not showtime:
                message = 'showtime is required'
                code = 1002
                raise Exception
            if not isinstance(showtime, str) or not re.match(r'^\d{2}:\d{2}$', showtime):
                message = 'Invalid showtime format, should be HH:MM'
                code = 1006
                raise Exception

            booking = self.bookingTable.find({
                'movie_id': movie_id,
                'showdate': showdate,
                'showtime': showtime
            })

            async for i in booking:
                result.extend(i.get("seats")) 

            if result:
                code = 2000
                status = True
                message = 'Booked seats found'
            else:
                code = 4002
                message = 'No booked seats found'

        except Exception as e:
            print(e)
            if not message:
                message = 'Internal error'
                code = 5000

        response = {
            'code': code,
            'status': status,
            'message': message,
            'result': result
        }

        self.set_header('Content-Type', 'application/json')
        self.write(response)
        await self.finish()