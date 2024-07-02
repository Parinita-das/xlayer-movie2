import datetime
from bson import ObjectId
import tornado.web
import json
from con import Database
from authorization.JwtConfiguration.auth import xenProtocol

class EditMovieHandler(tornado.web.RequestHandler):
    movie_table = Database.db['movies']
    usersTable = Database.db['user']

    @xenProtocol
    async def post(self):
        code = 1000
        status = False
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
            
            request_data = json.loads(self.request.body)
            movie_title = request_data.get('title')
            updated_data = request_data.get('updated_data', {})

            movie_table = Database.db['movies']

            movie = await movie_table.find_one({'title': movie_title})

            if movie:
                if 'title' in updated_data:
                    title = updated_data['title']

                    if not title:
                        message = 'title is required'
                        code = 4001
                        raise Exception

                    elif len(title) > 50:
                        message = 'Length should be within 50'
                        code = 4003
                        raise Exception

                    elif not isinstance(title[0], str):
                        message = 'Invalid title format'
                        code = 4004
                        raise Exception

                if 'genre' in updated_data:
                    genre = updated_data['genre']

                    if not genre:
                        message = 'genre is required'
                        code = 3001
                        raise Exception

                    elif not isinstance(genre[0], str):
                        message = 'Invalid genre format'
                        code = 3004
                        raise Exception

                if 'duration' in updated_data:
                    duration = updated_data['duration']

                    if not duration:
                        message = 'duration is required'
                        code = 5001
                        raise Exception

                    elif not isinstance(duration, str):
                        message = 'Invalid duration format'
                        code = 7002
                        raise Exception

                if 'release_date' in updated_data:
                    release_date = updated_data['release_date']

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

                if 'director' in updated_data:
                    director = updated_data['director']

                    if not director:
                        message = 'director is required'
                        code = 7001
                        raise Exception

                    elif len(director) > 50:
                        message = 'Length should be within 50'
                        code = 7003
                        raise Exception

                    elif not isinstance(director, str):
                        message = 'Invalid director format'
                        code = 7002
                        raise Exception

                if 'showtimes' in updated_data:
                    showtimes = updated_data['showtimes']

                    if not showtimes:
                        message = 'showtimes are required'
                        code = 9001
                        raise Exception

                    elif not isinstance(showtimes, list):
                        message = 'Invalid showtimes format'
                        code = 9002
                        raise Exception

                    elif any(not isinstance(time, str) for time in showtimes):
                        message = 'Invalid showtimes format. All entries must be strings.'
                        code = 9003
                        raise Exception

                if 'show_start_date' in updated_data:
                    show_start_date = updated_data['show_start_date']

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

                if 'show_end_date' in updated_data:
                    show_end_date = updated_data['show_end_date']

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

                if 'seat_price' in updated_data:
                    seat_price = updated_data['seat_price']

                    if not seat_price:
                        message = 'seat_price is required'
                        code = 9001
                        raise Exception

                    try:
                        seat_price = float(seat_price)
                        if seat_price <= 0:
                            raise ValueError
                    except ValueError:
                        message = 'Invalid seat_price format. Must be a positive number.'
                        code = 9002
                        raise Exception

                updated_movie = {**movie, **updated_data}
                update_result = await movie_table.replace_one({'title': movie_title}, updated_movie)

                if update_result.modified_count > 0:
                    code = 2000
                    status = True
                    message = "Movie updated successfully"
                else:
                    code = 1007
                    message = "Update operation failed"
                    raise Exception(message)
            else:
                code = 1007
                message = "Movie not found"

        except ValueError as ve:
            code = 4000  
            message = str(ve)
        except Exception as e:
            code = 1003
            message = 'Internal error'
            print(e)

        response = {
            'code': code,
            'message': message,
            'status': status,
        }

        self.write(response)
        self.finish()