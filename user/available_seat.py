import json
from bson.objectid import ObjectId
import tornado.web
import re
from datetime import datetime
from con import Database

class SeatAvailabilityHandler(tornado.web.RequestHandler, Database):
    bookingTable = Database.db['booking']
    movieTable = Database.db['movies']
    cityTable = Database.db['city']
    # userTable = Database.db['user'].

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

            movie = await self.movieTable.find_one({'_id': movie_id})
            if not movie:
                message = 'Movie not found'
                code = 1008
                raise Exception

            total_seats=80
            total_seats = movie.get('total_seats', 0)

            bookings = self.bookingTable.find({
                'movie_id': movie_id,
                'showtime': showtime
            })

            booked_seats = set()
            async for booking in bookings:
                booked_seats.update(booking.get('seats', []))

            available_seats = [str(i) for i in range(1, total_seats + 1) if str(i) not in booked_seats]

            code = 2000
            status = True
            message = 'Seat availability retrieved successfully'
            result = {
                'total_seats': total_seats,
                'booked_seats': list(booked_seats),
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