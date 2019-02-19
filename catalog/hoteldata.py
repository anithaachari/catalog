from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Hotel, Base, HotelMenu, User
engine = create_engine('sqlite:///hotels.db')
# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine
DBsession = sessionmaker(bind=engine)
session = DBsession()
# to delete the content in the table
session.query(User).delete()
# delete content if existing.
session.query(Hotel).delete()
# delete content if existing.
session.query(HotelMenu).delete()
# create sample user
user1 = User(name="anitha achari", email="adiuma504@gmail.com",
             picture='puppy.jpg')
session.add(user1)
session.commit()
# create sample hotel and it's menu
hotel1 = Hotel(user_id=1, name=" Andhrapradesh Hotels")
session.add(hotel1)
session.commit()
hotelmenu1 = HotelMenu(user_id=1, name='Hotel Rajahamsa', price='4454/-',
                       description='good facilities with free WiFi',
                       Address='Opposite APS RTC bustand Lane,'
                               'Venugopal Nagar,Old Town, Anantapur,'
                               'Andhra Pradesh 515001', hotel=hotel1)
session.add(hotelmenu1)
session.commit()
hotelmenu2 = HotelMenu(user_id=1, name='SRS Regency Hotel',
                       price='6553/-',
                       description='3-star hotel and with free WiFi',
                       Address='Near Sri Khantam Circle, Kamalanagar,'
                               'Anantapur, Andhra Pradesh 515001',
                               hotel=hotel1)
session.add(hotelmenu2)
session.commit()
hotel2 = Hotel(user_id=1, name='Karntaka Hotels')
session.add(hotel2)
session.commit()
hotelmenu1 = HotelMenu(user_id=1, name='Hotel Mayura Chalukya',
                       price='850/-', description='1-star hotel',
                       Address='Ramdurg Road, PWD Compound,'
                               'Badami, Karnataka 587201', hotel=hotel2)
session.add(hotelmenu1)
session.commit()
hotelmenu2 = HotelMenu(user_id=1, name='Hotel Malligi',
                       price='3742/-', description='3-star hotel',
                       Address='10/90 J.N.Road,'
                               'Near lakshmi Saraswati Theatres,'
                               'Hosapete, Karnataka 583201', hotel=hotel2)
session.add(hotelmenu2)
session.commit()
print "added menu items"
