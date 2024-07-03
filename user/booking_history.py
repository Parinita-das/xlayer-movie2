from datetime import datetime
import json
from bson.objectid import ObjectId
import tornado.web
import re
from con import Database
from authorization.JwtConfiguration.auth import xenProtocol

class BookingHistoryHandler(tornado.web.RequestHandler, Database):
    bookingTable = Database.db['booking']
    movieTable = Database.db['movies']
    userTable = Database.db['user']
    
    @xenProtocol
    async def get(self):
        code = 1000
        status = False
        result = []
        message = ''

        try:
            user_id = self.get_argument('user_id')  # Get user_id from query parameter

            if not user_id:
                message = 'user_id is required'
                code = 1002
                raise Exception
            user_id = ObjectId(user_id)

            # Retrieve booking history for the user_id
            bookings = await self.bookingTable.find({'user_id': user_id}).to_list(length=None)

            if bookings:
                status = True
                message = f'Found {len(bookings)} bookings'
                result = [{
                    'booking_id': str(booking['_id']),
                    'movie_id': str(booking['movie_id']),
                    'showdate': booking['showdate'],
                    'showtime': booking['showtime'],
                    'screen': booking['screen'],
                    'seats': booking['seats'],
                    'total_price': booking['total_price']
                } for booking in bookings]
            else:
                message = 'No bookings found for the user'
                code = 1012

        except Exception as e:
            print(e)
            if not message:
                message = 'Internal error'
                code = 1011

        response = {
            'code': code,
            'status': status,
            'message': message,
            'result': result
        }

        self.set_status(400 if code >= 1000 and code < 1100 else 500)
        self.write(response)
        self.finish()
