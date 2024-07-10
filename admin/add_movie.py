import datetime
from bson import ObjectId
import tornado.web
import json
from authorization.JwtConfiguration.auth import xenProtocol
from con import Database  
import re
from mimetypes import MimeTypes
from uuid import uuid4

class AddMovieHandler(tornado.web.RequestHandler, Database):
    movie_table = Database.db['movies']
    usersTable = Database.db['user']
    
    @xenProtocol
    async def post(self):
        code = 1000
        status = False
        result = []
        message = ''

        try:
            user = await self.usersTable.find_one({'_id': ObjectId(self.user_id)})

            if not user:
                message = 'User not found'
                code = 4002
                raise tornado.web.HTTPError(400, reason=message)

            mUserRole = user.get('role')
            if mUserRole != 'admin':
                message = 'Unauthorized access'
                code = 4030
                raise tornado.web.HTTPError(403, reason=message)
            
            try:
                files = {}
                args = {}
                b = self.request.headers.get('Content-Type')
                tornado.httputil.parse_body_arguments(b, self.request.body, args, files)
                data = json.loads(args['basic'][0])
            except Exception as e:
                message = 'Expected type in Form-Data.'
                code = 4036
                raise Exception


            files = self.request.files.get('photos', [])  
            images = []
            for index, mPhoto in enumerate(files):
                try:
                    if not mPhoto:
                        raise Exception(f'{index} photo is missing')
                    mImage = self.save_photo(mPhoto, f'photo_{index}')
                    images.append({'fileName': mImage})
                except Exception as e:
                    message = str(e)
                    code = 4553
                    raise Exception
            
            if not images:
                message = 'Photos are required'
                code = 4054
                raise Exception

            title = data.get('title')

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
            existing_movie = await self.movie_table.find_one({'title': title})
            if existing_movie:
                message = 'Movie with the same title already exists'
                code = 4005
                raise Exception

            genre = data.get('genre')

            if not genre:
                message = 'genre is required'
                code = 3001
                raise Exception

            elif not isinstance(genre, list):
                message = 'Invalid genre format. Should be a list of strings.'
                code = 3004
                raise Exception

            duration = data.get('duration')

            if not duration:
                message = 'duration is required'
                code = 5001
                raise Exception

            elif not isinstance(duration, str):
                message = 'Invalid duration format'
                code = 7002
                raise Exception

            release_date = data.get('release_date')

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

            director = data.get('director')

            if not director:
                message = 'director is required'
                code = 7001
                raise Exception

            elif len(director) > 50:
                message = 'Length should be within 50'
                code = 7003
                raise Exception

            showtimes = data.get('showtimes')

            if not showtimes:
                message = 'showtimes are required'
                code = 9001
                raise Exception

            elif not isinstance(showtimes, list):
                message = 'Invalid showtimes format. Should be a list of strings.'
                code = 9002
                raise Exception

            elif any(not isinstance(time, str) for time in showtimes):
                message = 'Invalid showtimes format. All entries must be strings.'
                code = 9003
                raise Exception

            for time in showtimes:
                if not re.match(r'^\d{2}:\d{2}$', time):
                    message = 'Invalid showtimes format. Each entry should be in HH:MM format.'
                    code = 1006
                    raise Exception

            show_start_date = data.get('show_start_date')

            if not show_start_date:
                message = 'show_start_date is required'
                code = 9101
                raise Exception

            try:
                datetime.datetime.fromisoformat(show_start_date)
            except ValueError:
                message = 'Invalid show_start_date format. Use ISO date format (YYYY-MM-DD).'
                code = 8002
                raise Exception

            show_end_date = data.get('show_end_date')

            if not show_end_date:
                message = 'show_end_date is required'
                code = 9102
                raise Exception

            try:
                datetime.datetime.fromisoformat(show_end_date)
            except ValueError:
                message = 'Invalid show_end_date format. Use ISO date format (YYYY-MM-DD).'
                code = 8002
                raise Exception

            seat_price_standard = data.get('seat_price_standard')

            if not seat_price_standard:
                message = 'seat_price_standard is required'
                code = 9001
                raise Exception

            try:
                seat_price_standard = float(seat_price_standard)
                if seat_price_standard <= 0:
                    raise ValueError
            except ValueError:
                message = 'Invalid seat_price_standard format. Must be a positive number.'
                code = 9002
                raise Exception

            seat_price_recliner = data.get('seat_price_recliner')

            if not seat_price_recliner:
                message = 'seat_price_recliner is required'
                code = 9001
                raise Exception

            try:
                seat_price_recliner = float(seat_price_recliner)
                if seat_price_recliner <= 0:
                    raise ValueError
            except ValueError:
                message = 'Invalid seat_price_recliner format. Must be a positive number.'
                code = 9002
                raise Exception

            movie_data = {
                'image_url': images, 
                'title': title,
                'genre': genre,
                'duration': duration,
                'release_date': release_date,
                'director': director,
                'showtimes': showtimes,
                'show_start_date': show_start_date,
                'show_end_date': show_end_date,
                'seat_price': {
                    'standard': seat_price_standard,
                    'recliner': seat_price_recliner,
                }
            }

            movie_result = await self.movie_table.insert_one(movie_data)

            if movie_result.inserted_id:
                code = 2000
                status = True
                message = "Movie added successfully"
                result.append({
                    'movieId': str(movie_result.inserted_id)
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
    
    def save_photo(self, photo, key):
        unique_id = str(uuid4())
        mime_type, _ = MimeTypes().guess_type(photo['filename'])
        extension = MimeTypes().guess_extension(mime_type)
        file_name = f"{unique_id}{extension}"
        with open("uploads/" + file_name, 'wb') as output_file:
            output_file.write(photo['body'])
        return file_name