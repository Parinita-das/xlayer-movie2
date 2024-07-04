from datetime import datetime
import json
from bson.objectid import ObjectId
import tornado.web
from con import Database  # Adjust the import path as per your project structure
from authorization.JwtConfiguration.auth import xenProtocol  # Adjust the import path as per your project structure

class SessionHandler(tornado.web.RequestHandler, Database):
    
    userTable = Database.db['user']
    sessionTable = Database.db['session']

    @xenProtocol  # Decorator for authorization, adjust as per your implementation
    async def get(self):
        code = 4000
        status = False
        result = []
        message = ''

        try:
            # Ensure the requesting user is authorized (e.g., admin role)
            user = await self.userTable.find_one({'_id': ObjectId(self.user_id)})
            if not user:
                message = 'User not found'
                code = 4002
                raise tornado.web.HTTPError(400, reason=message)

            mUserRole = user.get('role')
            if mUserRole != 'admin':
                message = 'Unauthorized access'
                code = 4030
                raise tornado.web.HTTPError(403, reason=message)
            
            # Retrieve and validate user_id from request arguments
            mUserId = self.get_argument('user_id')
            if not mUserId:
                code = 4511
                message = "User ID is required"
                raise Exception("User ID is required")
            mUserId = ObjectId(mUserId)
            query = {'user_id': mUserId}
            
            # Aggregate session data for the given user_id
            aggregation_pipeline = [
                {
                    '$match': query
                },
                {
                    '$lookup': {
                        'from': 'user',
                        'localField': 'user_id',
                        'foreignField': '_id',
                        'as': 'user_details'
                    }
                },
                {
                    '$addFields': {
                        'user_details': {
                            '$first': '$user_details'
                        }
                    }
                },
                {
                    '$project': {
                        '_id': {'$toString': '$_id'},
                        'userId': {'$toString': '$user_id'},
                        'name': '$user_details.name',
                        'login_time': 1,
                        'logout_time': 1,
                        'duration': 1,
                    }
                }
            ]
            
            cursor = self.sessionTable.aggregate(aggregation_pipeline)
            async for session in cursor:
                session['login_time'] = format_timestamp(session.get('login_time'))
                session['logout_time'] = format_timestamp(session.get('logout_time'))
                session['duration'] = format_duration(session.get('duration'))
                result.append(session)
            
            if result:
                message = 'Found'
                code = 2000
                status = True
            else:
                message = 'No data found for the given user_id'
                status = False
                code = 4002

        except tornado.web.HTTPError as e:
            code = e.status_code
            message = e.reason
        except Exception as e:
            if not message:
                message = 'Internal server error'
                code = 5010

        response = {
            'code': code,
            'message': message,
            'status': status,
        }

        try:
            if result:
                response['result'] = result
            self.set_header('Content-Type', 'application/json')
            self.write(json.dumps(response, default=str))
            await self.finish()

        except Exception as e:
            message = 'Error in response serialization'
            code = 5011
            raise Exception(message)

def format_timestamp(timestamp):
    try:
        if timestamp is None:
            return None
        dt_object = datetime.fromtimestamp(timestamp)
        return dt_object.strftime("%A, %d %B %Y, %H:%M:%S")
    except Exception as e:
        print(f"Error formatting timestamp: {e}")
        return "Invalid Date"

def format_duration(duration):
    try:
        if duration is None:
            return None
        duration_seconds = int(duration)
        hours, remainder = divmod(duration_seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{hours}h {minutes}m {seconds}s"
    except Exception as e:
        print(f"Error formatting duration: {e}")
        return "Invalid Duration"
