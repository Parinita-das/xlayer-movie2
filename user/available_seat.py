import json
from bson.objectid import ObjectId
import tornado.web
import re
from datetime import datetime
from con import Database
from authorization.JwtConfiguration.auth import xenProtocol

class SeatAvailabilityHandler(tornado.web.RequestHandler, Database):
    bookingTable = Database.db['booking']
    movieTable = Database.db['movies']
    # cityTable = Database.db['city']
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

            # Get the movie document
            movie = await self.movieTable.find_one({'_id': movie_id})

            if not movie:
                message = 'Movie not found'
                code = 1008
                raise Exception

            # Define total seats based on rows and columns (A-H, 1-10)
            rows = 'ABCDEFGH'
            columns = 10
            total_seats = [f"{row}{col}" for row in rows for col in range(1, columns + 1)]

            # Find bookings for the specific movie, showdate, and showtime
            bookings = self.bookingTable.find({
                'movie_id': movie_id,
                'showdate': showdate,
                'showtime': showtime
            })

            booked_seats = set()
            async for booking in bookings:
                booked_seats.update(booking.get('seats', []))

            # Calculate available seats by subtracting booked seats from total seats
            available_seats = [seat for seat in total_seats if seat not in booked_seats]

            code = 2000
            status = True
            message = 'Available seats retrieved successfully'
            result = {
                'available_seats': available_seats
            }

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
