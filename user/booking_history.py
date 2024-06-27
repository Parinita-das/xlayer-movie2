import json
from bson.objectid import ObjectId
import tornado.web
from con import Database

class BookingHistoryHandler(tornado.web.RequestHandler, Database):
    bookingTable = Database.db['booking']
    movieTable = Database.db['movies']
    cityTable = Database.db['city']
    userTable = Database.db['user']

    #.

    async def get(self):
        code = 2000
        status = False
        result = []
        message = ''

        try:
            user_id = self.get_argument('user_id', None)

            if not user_id:
                message = 'user_id is required'
                code = 1002
                raise Exception
            
            user_id = ObjectId(user_id)

            user = await self.userTable.find_one({'_id': user_id})

            if not user:
                message = 'User not found'
                code = 1003
                raise Exception

            user_bookings = []
            for booking_id in user.get('bookings', []):
                booking = await self.bookingTable.find_one({'_id': booking_id})
                if booking:
                    user_bookings.append({
                        'booking_id': str(booking['_id']),
                        'movie_id': str(booking['movie_id']),
                        'city_id': str(booking['city_id']),
                        'showdate': booking['showdate'],
                        'showtime': booking['showtime'],
                        'seats': booking['seats'],
                        'total_price': booking['total_price']
                    })

            if user_bookings:
                code = 2000
                status = True
                message = 'Booking history retrieved successfully'
                result = user_bookings
            else:
                code = 1004
                message = 'No booking history found for the user'

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