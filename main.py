import tornado.ioloop
import tornado.web
import tornado

from admin.add_movie import AddMovieHandler
from forgot_password.Reset_pw import ResetHandler
from forgot_password.otp import OTPHandler
from forgot_password.verification_password import VerifyHandler
from getsession import SessionHandler
from authorization.logout import LogOutHandler
from user.available_seat import SeatAvailabilityHandler
from user.booking import BookingHandler
from admin.del_movie import DeleteMovieHandler
from admin.edit_movie import EditMovieHandler
from user.booking_history import BookingHistoryHandler
from user.get_movie import GetMoviesHandler
from user.get_seats import BookedSeatsHandler 
from authorization.signup import UserHandler
from user.search_movie import SearchHandlerByTitle
from authorization.login import LoginHandler


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        response = {
            'message': 'Hello, world!'
        }
        self.write(response)


def make_app():
    return tornado.web.Application([
        (r"/api", MainHandler),
        (r"/api/users", UserHandler),
        (r"/api/login", LoginHandler),
        (r"/api/add_movie", AddMovieHandler),
        (r"/api/get_movie", GetMoviesHandler),
        (r"/api/del_movie", DeleteMovieHandler),
        (r"/api/edit_movie", EditMovieHandler),
        (r"/api/search_movie", SearchHandlerByTitle),
        (r"/api/booking", BookingHandler),
        (r"/api/get_seats", BookedSeatsHandler),
        (r"/api/booking_history", BookingHistoryHandler),
        (r"/api/available_seat", SeatAvailabilityHandler),
        (r"/api/logout", LogOutHandler),
        (r"/api/getsession", SessionHandler),
        ("/api/forgot_password", OTPHandler),       
        ("/api/verification_pw", VerifyHandler),
        ("/api/reset_pw", ResetHandler),





    ])

if __name__ == "__main__":
    app = make_app()
    app.listen(3000)
    print("Server is running on http://localhost:3000")
    tornado.ioloop.IOLoop.current().start()