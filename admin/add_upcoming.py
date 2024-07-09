import datetime
from bson import ObjectId
import tornado.web
import json
from authorization.JwtConfiguration.auth import xenProtocol
from con import Database  
import re

class AddUpcomingHandler(tornado.web.RequestHandler, Database):
    upcoming_movieTable = Database.db['upcoming']
    usersTable = Database.db['user']
    
    @xenProtocol
    async def post(self):
        code = 1000
        status = False
        result = []
        message = ''

        try:
            user = await self.usersTable.find_one({'_id': ObjectId(self.user_id)})
            print(user)
            if not user:
                message = 'User not found'
                code = 4002
                raise tornado.web.HTTPError(400, reason=message)

            mUserRole = user.get('role')
            print(mUserRole)
            if mUserRole != 'admin':
                message = 'Unauthorized access'
                code = 4030
                raise tornado.web.HTTPError(403, reason=message)


            # Parse the request body as JSON.
            try:
                self.request.arguments = json.loads(self.request.body.decode())
            except Exception as e:
                code = 1001
                message = "Invalid JSON"
                raise Exception
            
            image_url = self.request.arguments.get('image_url')

            if image_url and not isinstance(image_url, str):
                message = 'Invalid image_url format. Must be a string.'
                code = 4006
                raise Exception

            title = self.request.arguments.get('title')

            if not title:
                message = 'title is required'
                code = 4001
                raise Exception

            elif len(title) > 50:
                message = 'Length should be within 50'
                code = 4003
                raise Exception

            elif not isinstance(title, str):
                message = 'Invalid title format'
                code = 4004
                raise Exception
            
            # Check if movie with the same title already exists
            existing_movie = await self.upcoming_movieTable.find_one({'title': title})
            if existing_movie:
                message = 'Movie with the same title already exists'
                code = 4005
                raise Exception

            genre = self.request.arguments.get('genre')

            if not genre:
                message = 'genre is required'
                code = 3001
                raise Exception

            elif not isinstance(genre, list):
                message = 'Invalid genre format. Should be a list of strings.'
                code = 3004
                raise Exception

            duration = self.request.arguments.get('duration')

            if not duration:
                message = 'duration is required'
                code = 5001
                raise Exception

            elif not isinstance(duration, str):
                message = 'Invalid duration format'
                code = 7002
                raise Exception

            release_date = self.request.arguments.get('release_date')

            if not release_date:
                message = 'release_date is required'
                code = 10001
                raise Exception

            try:
                datetime.datetime.fromisoformat(release_date)
            except ValueError:
                message = 'Invalid release_date format. Use ISO date format (YYYY-MM-DD).'
                code = 10002
                raise Exception

            director = self.request.arguments.get('director')

            if not director:
                message = 'director is required'
                code = 7001
                raise Exception

            elif len(director) > 50:
                message = 'Length should be within 50'
                code = 7003
                raise Exception

            upcoming_movie_data = {
                'image_url': image_url, 
                'title': title,
                'genre': genre,
                'duration': duration,
                'release_date': release_date,
                'director': director,
            }

            upcoming_movie_result = await self.upcoming_movieTable.insert_one(upcoming_movie_data)

            if upcoming_movie_result.inserted_id:
                code = 2000
                status = True
                message = "Movie added successfully"
                result.append({
                    'movieId': str(upcoming_movie_result.inserted_id)
                })
            else:
                code = 1006
                message = "Failed to add movie"
                raise Exception

        except Exception as e:
            code = 1003
            if not len(message):
                message = 'Internal error'
                print(e)
                raise Exception

        response = {
            'code': code,
            'message': message,
            'status': status,
        }

        try:
            if len(result):
                response['result'] = result
            self.write(response)
            self.finish()
        except Exception as e:
            message = 'There is some issue'
            code = 1004
            raise Exception
