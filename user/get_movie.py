import datetime
from bson import ObjectId
import tornado.web
import json
from con import Database  
import re

class GetMoviesHandler(tornado.web.RequestHandler, Database):
    movie_table = Database.db['movies']
    usersTable = Database.db['user']

    async def get(self):
        try:
            movies = await self.movie_table.find({}).to_list(length=None)
            if movies:
                result = []
                for movie in movies:
                        release_date = movie['release_date'].isoformat() if isinstance(movie['release_date'], datetime.datetime) else movie['release_date']
                        show_start_date = movie['show_start_date'].isoformat() if isinstance(movie['show_start_date'], datetime.datetime) else movie['show_start_date']
                        show_end_date = movie['show_end_date'].isoformat() if isinstance(movie['show_end_date'], datetime.datetime) else movie['show_end_date']

                        for img in movie.get('images', []):
                            img['link'] = 'http://10.10.10.136/uploads/{}'.format(img.get('fileName'))
                            
                        result.append({
                            'image_url': image_url,
                            'title': movie['title'],
                            'genre': movie['genre'],
                            'duration': movie['duration'],
                            'release_date': release_date,
                            'director': movie['director'],
                            'showtimes': movie['showtimes'],
                            'show_start_date': show_start_date,
                            'show_end_date': show_end_date,
                            'seat_price': movie['seat_price']
                        })

                message = 'Movies fetched successfully'
                response = {
                    'code': 200,
                    'status': True,
                    'message': message,
                    'result': result
                }
            else:
                response = {
                    'code': 404,
                    'status': False,
                    'message': 'No movies found',
                    'result': []
                }

        except Exception as e:
            print(e)
            response = {
                'code': 500,
                'status': False,
                'message': 'Internal error',
                'result': []
            }

        self.set_status(response['code'])
        self.write(response)
        self.finish()
