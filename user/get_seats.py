import json
from bson.objectid import ObjectId
import tornado.web
import re
from datetime import datetime
from con import Database

class BookedSeatsHandler(tornado.web.RequestHandler, Database):
    bookingTable = Database.db['booking']
    movieTable = Database.db['movies']
    userTable = Database.db['user']

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

            movies = await self.movieTable.find_one({'_id': movie_id})

            if not movies:
                message = 'Movie not found'
                code = 1008
                raise Exception

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
            
            show_start_date = movies.get('show_start_date')
            show_end_date = movies.get('show_end_date')

             # Convert show_end_date to datetime.date if it's not already
            if isinstance(show_end_date, str):
                show_end_date = datetime.strptime(show_end_date, '%Y-%m-%d').date()

            if isinstance(show_start_date, str):
                show_start_date = datetime.strptime(show_start_date, '%Y-%m-%d').date()
    
            if date_obj < datetime.now().date():
                message = 'Showdate must be from current date onwards'
                code = 1013
                raise Exception
            
            if date_obj < show_start_date:
                message = 'Showdate must be after movie show_start_date'
                code = 1015
                raise Exception

            if date_obj > show_end_date:
                message = 'Showdate exceeds movie show_end_date'
                code = 1014
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
            if showtime not in movies.get('showtimes', []):
                message = 'Invalid showtime. Please select a valid showtime for the movie.'
                code = 1016
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