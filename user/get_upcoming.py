import datetime
from bson import ObjectId
import tornado.web
import json
from con import Database  
import re

class GetUpcomingHandler(tornado.web.RequestHandler, Database):
    upcoming_movieTable = Database.db['upcoming']
    usersTable = Database.db['user']

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
                        
                        image_urls = []
                        for img in movie.get('images', []):
                            img_url = 'http://10.10.10.139/uploads/{}'.format(img.get('fileName'))
                            image_urls.append(img_url)

                        result.append({
                            'image_url': image_urls,
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
