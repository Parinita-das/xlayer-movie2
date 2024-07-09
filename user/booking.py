from datetime import datetime
import json
from bson.objectid import ObjectId
import tornado.web
import re
from con import Database
from authorization.JwtConfiguration.auth import xenProtocol
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart    

SECRET_KEY = "Xlayer.in"
EMAIL_SENDER = "parinitaofficial95@gmail.com"  
EMAIL_PASSWORD = "mdzwgkyfcjircoky"   

class BookingHandler(tornado.web.RequestHandler, Database):
    bookingTable = Database.db['booking']
    movieTable = Database.db['movies']
    userTable = Database.db['user']

    @xenProtocol
    async def post(self):
        code = 1000
        status = False
        result = []
        message = ''

        try:
            # Parse the request body as JSON
            try:
                request_data = json.loads(self.request.body.decode())
            except Exception as e:
                code = 1001
                message = "Invalid JSON"
                raise Exception

            movie_id = request_data.get('movie_id')

            if not movie_id:
                message = 'movie_id is required'
                code = 1002
                raise Exception
            movie_id = ObjectId(movie_id)



            email = request_data.get('email')

            if not email:
                message = 'email is required'
                code = 1002
                raise Exception
            
            user = await self.userTable.find_one({'_id': self.user_id})
            if not user:
                message = 'User not found'
                code = 1017
                raise Exception

            showdate = request_data.get('showdate')

            if not (showdate):
                message = 'showdate is required'
                code = 1002
                raise Exception

            try:
                date_obj = datetime.strptime(showdate, '%Y-%m-%d').date()
            except ValueError:
                message = 'Invalid date format, should be YYYY-MM-DD'
                code = 1005
                raise Exception
            
            movies = await self.movieTable.find_one({
                '_id': movie_id
            })

            if not movies:
                message = 'Movie not found'
                code = 1008
                raise Exception
            
            show_start_date = movies.get('show_start_date')
            show_end_date = movies.get('show_end_date')

             # Convert show_end_date to datetime.date if it's not already
            if isinstance(show_end_date, str):
                show_end_date = datetime.strptime(show_end_date, '%Y-%m-%d').date()

            if isinstance(show_start_date, str):
                show_start_date = datetime.strptime(show_start_date, '%Y-%m-%d').date()
    
            if date_obj < datetime.now().date():
                message = 'Showdate must be from current date onwards'
                code = 1013
                raise Exception
            
            if date_obj < show_start_date:
                message = 'Showdate must be after movie show_start_date'
                code = 1015
                raise Exception

            if date_obj > show_end_date:
                message = 'Showdate exceeds movie show_end_date'
                code = 1014
                raise Exception

            showtime = request_data.get('showtime')

            if not (showtime):
                message = 'showtime is required'
                code = 1002
                raise Exception
            
            if not isinstance(showtime, str) or not re.match(r'^\d{2}:\d{2}$', showtime):
                message = 'Invalid showtime format, should be HH:MM'
                code = 1006
                raise Exception
            
            if showtime not in movies.get('showtimes', []):
                message = 'Invalid showtime. Please select a valid showtime for the movie.'
                code = 1016
                raise Exception

            seats = request_data.get('seats') 

            if not (seats):
                message = 'seats is required'
                code = 1002
                raise Exception
            
            seat_pattern = re.compile(r'^[A-H][1-9]|10$')

            for seat in seats:
                if not seat_pattern.match(seat):
                    message = f'Invalid seat format: seats Should be in format A1 to H10.'
                    code = 1003
                    raise Exception
                
            # Check for duplicate seats
            if len(seats) != len(set(seats)):
                message = 'Duplicate seats found in the booking request'
                code = 1008  
                raise Exception    

            if not isinstance(seats, list) or not all(isinstance(seat, str) for seat in seats):
                message = 'Seats should be a list of strings'
                code = 1007
                raise Exception
            
            # Check if any of the seats are already booked for the given showdate and showtime
            existing_bookings = await self.bookingTable.find({
                'movie_id': movie_id,
                'showdate': showdate,
                'showtime': showtime,
                'seats': {'$in': seats}
            }).to_list(length=None)

            if existing_bookings:
                booked_seats = set()
                for booking in existing_bookings:
                    booked_seats.update(booking['seats'])

                conflicting_seats = set(seats) & booked_seats
                if conflicting_seats:
                    message = f'Seats {", ".join(conflicting_seats)} already booked for this showtime and showdate'
                    code = 1009
                    raise Exception

            total_price = 0.0

            seat_price_standard = movies.get('seat_price', {}).get('standard', 0.0)
            seat_price_recliner = movies.get('seat_price', {}).get('recliner', 0.0)

            for seat in seats:
                if seat.startswith('A'):
                    total_price += seat_price_recliner
                elif seat.startswith('B') or seat.startswith('C') or seat.startswith('D') or seat.startswith('E') or seat.startswith('F') or seat.startswith('G') or seat.startswith('H'):
                    total_price += seat_price_standard
                else:
                    message = 'Invalid seat category'
                    code = 1010
                    raise Exception

            booking = {
                'movie_id': movies['_id'],
                'user_id':user['_id'],
                'showdate': showdate,
                'showtime': showtime,
                'seats': seats,
                'total_price': total_price
            }

            addBooking = await self.bookingTable.insert_one(booking)

            if addBooking.inserted_id:
                code = 2000
                status = True
                message = 'Booking created successfully'
                result.append({
                    'booking_id': str(addBooking.inserted_id),
                    'total_price': total_price
                })

                # Send confirmation email to the user
                await self.send_booking_confirmation_email(user['email'], movies, showdate, showtime, seats, total_price)
            
            else:
                code = 1010
                message = 'Failed to create booking'
                raise Exception

        except Exception as e:
            print(e)
            if not message:
                message = 'Internal error'
                code = 1011

        response = {
            'code': code,
            'status': status,
            'message': message,
            'result': result
        }

        self.set_status(400 if code >= 1000 and code < 1100 else 500)  
        self.write(response)
        self.finish()

    async def send_booking_confirmation_email(self, to_email, movie, showdate, showtime, seats, total_price):
        try:
            msg = MIMEMultipart()
            msg['From'] = EMAIL_SENDER
            msg['To'] = to_email
            msg['Subject'] = 'Booking Confirmation'

            seat_categories = {
            'A': 'Recliner',
            'B': 'Standard',
            'C': 'Standard',
            'D': 'Standard',
            'E': 'Standard',
            'F': 'Standard',
            'G': 'Standard',
            'H': 'Standard'
            }

            grouped_seats = {
                'Recliner': [],
                'Standard': []
            }
            for seat in seats:
                category = seat_categories.get(seat[0], 'Unknown')
                grouped_seats[category].append(seat)

            seat_category_messages = []
            for category, seat_list in grouped_seats.items():
                if seat_list:
                    seat_category_messages.append(f"{category}: {', '.join(seat_list)}")


            seat_category_message = "\n".join(seat_category_messages)

            email_body = f"Hello,\n\nYour booking for the movie '{movie['title']}' has been confirmed.\n\nMovie Details:\nTitle: {movie['title']}\nShowdate: {showdate}\nShowtime: {showtime}\nSeats: {', '.join(seats)}\n\nSeat category:\n{seat_category_message}\n\nTotal Price: {total_price}\n\nThank you for booking with us!\n\nBest regards,\nYour App Team"

            msg.attach(MIMEText(email_body, 'plain'))
            print('Hello')

            server = smtplib.SMTP('smtp.gmail.com', 587)  # Update SMTP server details
            server.starttls()
            server.login(EMAIL_SENDER, EMAIL_PASSWORD)
            server.sendmail(EMAIL_SENDER, to_email, msg.as_string())
            server.quit()

        except Exception as e:
            print(f"Error sending email: {e}")
            raise Exception('Failed to send booking confirmation email')

