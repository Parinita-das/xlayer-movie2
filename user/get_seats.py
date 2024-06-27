import json
from bson.objectid import ObjectId
import tornado.web
import re
from datetime import datetime
from con import Database

class BookedSeatsHandler(tornado.web.RequestHandler, Database):
    bookingTable = Database.db['booking']
    movieTable = Database.db['movies']
    cityTable = Database.db['city']
    userTable = Database.db['user']

    #.

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

            showtime = self.get_argument('showtime', None)

            if not showtime:
                message = 'showtime is required'
                code = 1002
                raise Exception

            bookings = self.bookingTable.find({
                'movie_id': movie_id,
                'showtime': showtime
            })

            async for i in bookings:
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