from bson import ObjectId
from con import Database
import jwt

SECRET_KEY = "Xlayer.in"

userTable = Database.db['user'] 
sessionTable = Database.db['session']

def xenProtocol(method):
    async def wrapper(self, *args, **kwargs):
        auth_header = self.request.headers.get("Authorization")
        if not auth_header or "Bearer " not in auth_header:
            self.set_status(401)
            self.write({
                'code': 4026,
                'message': "Authorization header missing",
                'status': False
            })
            self.finish()
            return
        token = auth_header.split()[1]
        
        try:
            # token = auth_header.split()[1]
            decoded = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            self.sessionId = decoded.get("_id")


            # Validate session in sessionTable
            session = await sessionTable.find_one({"_id": ObjectId(self.sessionId)})
            if not session or session.get('blacklisted'):
                self.set_status(401)
                self.write({
                    'code': 4077,
                    'message': 'Invalid or blacklisted token',
                    'status': False
                })
                self.finish()
                return
            
        
            # find user by session_id
            user = await sessionTable.find_one({"_id": ObjectId(self.sessionId)})
            if not user:
                self.set_status(401)
                self.write({
                    'code': 4078,
                    'message': 'User not found or inactive',
                    'status': False
                })
                self.finish()
                return
            self.user_id = ObjectId(user.get('user_id'))
        


        except jwt.ExpiredSignatureError:
            self.set_status(401)
            self.write({
                'code': 4012,
                'message': 'Token has expired, Login again!',
                'status': False
            })
            self.finish()
            return
        except jwt.InvalidTokenError:
            self.set_status(401)
            self.write({
                    'code': 4020,
                    'message': 'Invalid token',
                    'status': False
            })
            self.finish()
            return
        except Exception as e:
            self.set_status(500)
            self.write({
                'code': 5000,
                'message': str(e),
                'status': False
            })
            self.finish()
            return

        await method(self, *args, **kwargs)
    return wrapper