import datetime
from bson import ObjectId
import tornado.web
import json
from con import Database  
from authorization.JwtConfiguration.auth import xenProtocol
import re

class GetMoviesHandler(tornado.web.RequestHandler, Database):
    movie_table = Database.db['movies']
    usersTable = Database.db['user']

    @xenProtocol
    async def get(self):
        code = 1000
        status = False
        result = []
        message = ''

        try:
            movies = await self.movie_table.find({}).to_list(length=None)

            if movies:
                status = True
                for movie in movies:

                    try:
                        
                        # release_date = movie['release_date'].isoformat() if isinstance(movie['release_date'], datetime.datetime) else movie['release_date']
                        # show_start_date = movie['show_start_date'].isoformat() if isinstance(movie['show_start_date'], datetime.datetime) else movie['show_start_date']
                        # show_end_date = movie['show_end_date'].isoformat() if isinstance(movie['show_end_date'], datetime.datetime) else movie['show_end_date']
                        
                        result.append({
                            'title': movie['title']

                        # result.append({
                        #     'movie_id': str(movie['_id']),
                        #     'title': movie['title'],
                        #     'genre': movie['genre'],
                        #     'duration': movie['duration'],
                        #     'release_date': movie['release_date'],
                        #     'director': movie['director'],
                        #     'showtimes': movie['showtimes'],
                        #     'show_start_date': movie['show_start_date'].isoformat(),
                        #     'show_end_date': movie['show_end_date'].isoformat(),
                        #     'seat_price': movie['seat_price'],
                        })
                        
                      
                        
                    except Exception as e:
                        print(f"Error processing movie ID {str(movie['_id'])}: {e}")
                        continue  # Skip this movie if there's an error  
                      
                message = 'Movies fetched successfully'
            else:
                code = 1007
                message = 'No movies found'

        except Exception as e:
            print(e)
            code = 1011
            message = 'Internal error'

        response = {
            'code': code,
            'status': status,
            'message': message,
            'result': result
        }

        self.set_status(400 if code >= 1000 and code < 1100 else 500)
        self.write(response)
        self.finish()


