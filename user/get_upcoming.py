import datetime
from bson import ObjectId
import tornado.web
import json
from con import Database  
from authorization.JwtConfiguration.auth import xenProtocol
import re

class GetUpcomingHandler(tornado.web.RequestHandler, Database):
    upcoming_movieTable = Database.db['upcoming']
    usersTable = Database.db['user']

    @xenProtocol
    async def get(self):
        code = 1000
        status = False
        result = []
        message = ''

        try:
            movies = await self.upcoming_movieTable.find({}).to_list(length=None)

            if movies:
                status = True
                for movie in movies:
                    try:
                        release_date = movie['release_date'].isoformat() if isinstance(movie['release_date'], datetime.datetime) else movie['release_date']

                        result.append({
                            'movie_id': str(movie['_id']),
                            'image_url':str(movie['image_url']),
                            'title': movie['title'],
                            'genre': movie['genre'],
                            'duration': movie['duration'],
                            'release_date': release_date,
                            'director': movie['director'],
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
