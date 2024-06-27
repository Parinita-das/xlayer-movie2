import tornado.ioloop
import tornado.web
import tornado

from admin.add_city import AddCityHandler
from admin.add_movie import AddMovieHandler
from authorization.admin_login import AdLoginHandler
from user.available_seat import SeatAvailabilityHandler
from user.booking import BookingHandler
from admin.del_city import DeleteCityHandler
from admin.del_movie import DeleteMovieHandler
from admin.edit_movie import EditMovieHandler
from user.booking_history import BookingHistoryHandler
from user.get_seats import BookedSeatsHandler
from user.select_city import CityDropdownHandler  
from authorization.signup import UserHandler
from user.search_movie import SearchHandlerByTitle
from authorization.user_login import LoginHandler

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        response = {
            'message': 'Hello, world!'
        }
        self.write(response)

        #.

def make_app():
    return tornado.web.Application([
        (r"/api", MainHandler),
        (r"/api/users", UserHandler),
        (r"/api/login", LoginHandler),
        (r"/api/admin_login", AdLoginHandler),
        (r"/api/add_movie", AddMovieHandler),
        (r"/api/del_movie", DeleteMovieHandler),
        (r"/api/edit_movie", EditMovieHandler),
        (r"/api/search_movie", SearchHandlerByTitle),
        (r"/api/add_city", AddCityHandler),
        (r"/api/del_city", DeleteCityHandler),
        (r"/api/select_city", CityDropdownHandler),
        (r"/api/booking", BookingHandler),
        (r"/api/get_seats", BookedSeatsHandler),
        (r"/api/booking_history", BookingHistoryHandler),
        (r"/available_seat", SeatAvailabilityHandler),


    ])

if __name__ == "__main__":
    app = make_app()
    app.listen(2002)
    print("Server is running on http://localhost:2002")
    tornado.ioloop.IOLoop.current().start()