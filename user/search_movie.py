import tornado.web
from bson.objectid import ObjectId
from con import Database

class SearchHandlerByTitle(tornado.web.RequestHandler, Database):
    movieTable = Database.db['movies']
    userTable = Database.db['user']

    async def get(self):
        code = 4000
        status = False
        result = []
        message = ''

        try:
            mSearch = str(self.get_argument('search'))
            if not mSearch:
                message = 'Please enter a movie title'
                code = 2000
                raise Exception

           
            # Execute the query
            mMovies = self.movieTable.find(
                {
                    '$or': [
                        {
                            'title': {
                                '$regex': mSearch,
                                '$options': 'ism'
                            }
                        },
                        {
                            'first_letter': {
                                '$regex': mSearch,
                                '$options': 'ism'
                            }
                        }, 
                    ]      
                }
            )

            async for movie in mMovies:
                movie['_id'] = str(movie.get('_id'))
                result.append(movie)

            if result:
                message = 'Found'
                code = 2000
                status = True
            else:
                message = 'Not found'
                code = 4002
                raise Exception

        except Exception as e:
            if not message:
                message = 'Internal server error'
                code = 5010
            print(e)

        response = {
            'code': code,
            'message': message,
            'status': status,
        }

        try:
            if result:
                response['result'] = result

            self.set_header('Content-Type', 'application/json')
            self.write(response)
            await self.finish()

        except Exception as e:
            print(e)
            message = 'There is some issue'
            code = 5011
            raise Exception