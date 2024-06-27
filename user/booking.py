from datetime import datetime
import json
from bson.objectid import ObjectId
import tornado.web
import re
from con import Database

class BookingHandler(tornado.web.RequestHandler, Database):
    bookingTable = Database.db['booking']
    movieTable = Database.db['movies']
    # cityTable = Database.db['city']
    userTable = Database.db['user']

    #.

    async def post(self):
        code = 1000
        status = False
        result = []
        message = ''

        try:
            # Parse the request body as JSON
            try:
                request_data = json.loads(self.request.body.decode())
            except Exception as e:
                code = 1001
                message = "Invalid JSON"
                raise Exception

            movie_id = request_data.get('movie_id')

            if not movie_id:
                message = 'movie_id is required'
                code = 1002
                raise Exception
            movie_id = ObjectId(movie_id)

            # city_id = request_data.get('city_id')

            # if not (city_id): 
            #     message = 'city_id is required'
            #     code = 1002
            #     raise Exception

            
            showdate = request_data.get('showdate')

            if not (showdate):
                message = 'showdate is required'
                code = 1002
                raise Exception

            try:
                date_obj = datetime.strptime(showdate, '%Y-%m-%d').date()
            except ValueError:
                message = 'Invalid date format, should be YYYY-MM-DD'
                code = 1005
                raise Exception

            showtime = request_data.get('showtime')

            if not (showtime):
                message = 'showtime is required'
                code = 1002
                raise Exception

            if not isinstance(showtime, str) or not re.match(r'^\d{2}:\d{2}$', showtime):
                message = 'Invalid showtime format, should be HH:MM'
                code = 1006
                raise Exception
            
            screen = request_data.get('screen')

            if not (screen):
                message = 'screen is required'
                code = 1002
                raise Exception
            
            elif screen not in ['1', '2', '3']:
                message = 'Invalid screen number.'
                code = 1003
                raise Exception

            seats = request_data.get('seats') #[1, 2, 50]

            if not (seats):
                message = 'seats is required'
                code = 1002
                raise Exception
            
            seat_pattern = re.compile(r'^[A-H][1-9]|10$')

            for seat in seats:
                if not seat_pattern.match(seat):
                    message = f'Invalid seat format: seats Should be in format A1 to H10.'
                    code = 1003
                    raise Exception

            # if not isinstance(seats, list) or not all(isinstance(seat, str) for seat in seats):
            #     message = 'Seats should be a list of strings'
            #     code = 1007
            #     raise Exception

            movie = await self.movieTable.find_one({
                '_id': movie_id,
                'showtimes': showtime
            })

            if not movie:
                message = 'Movie not found'
                code = 1008
                raise Exception

            # city = await self.cityTable.find_one({'_id': ObjectId(city_id)})

            # if not city:
            #     message = 'City not found'
            #     code = 1009
            #     raise Exception
            
            
            total_price  = movie.get('seat_price') * len(seats)
            

            booking = {
                'movie_id': movie['_id'],
                # 'city_id': ObjectId(city_id),
                'showdate': showdate,
                'showtime': showtime,
                'screen' : screen,
                'seats': seats,
                'total_price': total_price
            }

            addBooking = await self.bookingTable.insert_one(booking)

            if addBooking.inserted_id:
                code = 2000
                status = True
                message = 'Booking created successfully'
                result.append({
                    'booking_id': str(addBooking.inserted_id)
                })
            else:
                code = 1010
                message = 'Failed to create booking'
                raise Exception

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
