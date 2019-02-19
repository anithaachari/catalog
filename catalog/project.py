from flask import Flask, render_template, request
from flask import redirect, jsonify, url_for, flash
from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Hotel, HotelMenu, User
from flask import session as login_session
import random
import string
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests
app = Flask(__name__)
CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Hotel Menu"
engine = create_engine('sqlite:///hotels.db',
                       connect_args={'check_same_thread': False},
                       echo=True)
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

hotelsList = session.query(Hotel)


@app.route('/')
@app.route('/login')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    hotel = session.query(Hotel).all()
    # return "The current session state is %s" % login_session['state']
    return render_template('login.html', STATE=state, hotels=hotel)


@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
                json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print ("Token's client ID does not match app's.")
        response.headers['Content-Type'] = 'application/json'
        return response
    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps
                                 ('Current user is already connected.'),
                                 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)
    data = answer.json()
    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']
    print (login_session['email'])
    # See if a user exists, if it doesn't make a new one
    login_session['provider'] = 'google'
    # see if user exists, if it doesn't make a new one
    user_id = getUserID(login_session["email"])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id
    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style ="width: 300px; height: 300px;border-radius: 150px;'
    '-webkit-border-radius: 150px;-moz-border-radius: 150px;">'
    flash("you are now logged in as %s" % login_session['username'])
    print ("done!")
    return output


# User Helper Functions
def createUser(login_session):
    newUser = User(name=login_session['username'], email=login_session[
                   'email'], picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


def getUserInfo(user_id):
    user = session.query(User).filter_by(id=user_id).one()
    return user


def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None


@app.route('/gdisconnect')
def gdisconnect():
    # Only disconnect a connected user.
    access_token = login_session.get('access_token')
    if access_token is None:
        response = make_response(
            json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    if result['status'] == '200':
        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    else:
        response = make_response(json.dumps
                                 ('Failed to revoke token for given user.',
                                  400))
        response.headers['Content-Type'] = 'application/json'
        return response


@app.route('/hotel/hotelmenu/JSON')
def itemsJSON():
    items = session.query(HotelMenu).all()
    return jsonify(hotelmenu=[i.serialize for i in items])


@app.route('/hotel/<int:hotel_id>/hotelmenu/JSON')
def hotelMenuJSON(hotel_id):
    hotel = session.query(Hotel).filter_by(id=hotel_id).one()
    hotelmenus = session.query(HotelMenu).filter_by(hotel_id=hotel_id).all()
    return jsonify(hotelMenus=[i.serialize for i in hotelmenus])


@app.route('/hotel/<int:hotel_id>/menu/<int:menu_id>/JSON')
def hotelmenuJSON(hotel_id, menu_id):
    hotelmenu = session.query(HotelMenu).filter_by(id=menu_id).one()
    return jsonify(hotelmenu=hotelmenu.serialize)


@app.route('/hotel/JSON')
def hotelsJSON():
    hotels = session.query(Hotel).all()
    return jsonify(hotels=[r.serialize for r in hotels])


# Home
@app.route('/hotel')
def showMenu():
    hotel = session.query(Hotel).all()
    if 'username' not in login_session:
        return redirect('/login')
    else:
        return render_template('hotels.html', hotels=hotel)


# add new hotel
@app.route('/hotel/new/', methods=['GET', 'POST'])
def newHotel():
    if 'username' not in login_session:
        return redirect('/login')
    if request.method == 'POST':
        newHotel = Hotel(name=request.form['name'],
                         user_id=login_session['user_id'])
        session.add(newHotel)
        session.commit()
        return redirect(url_for('showMenu'))
    else:
        return render_template('newHotel.html', hotels=hotelsList)


# edit hotel
@app.route('/hotel/<int:hotel_id>/edit/', methods=['GET', 'POST'])
def editHotel(hotel_id):
    editedHotel = session.query(Hotel).filter_by(id=hotel_id).one()
    if 'username' not in login_session:
        return redirect('/login')
    creator = getUserInfo(editedHotel.user_id)
    user = getUserInfo(login_session['user_id'])
    # If logged in user != item owner redirect them
    if creator.id != login_session['user_id']:
        flash("You cannot edit this hotel name."
              "This is belongs to %s" % creator.name)
        return redirect(url_for('showMenu'))
    if request.method == 'POST':
        editedHotel.name = request.form['name']
        return redirect(url_for('showMenu'))
    else:
        return render_template('editHotel.html', hotel=editedHotel,
                               hotels=hotelsList)


# delete hotel name
@app.route('/hotel/<int:hotel_id>/delete/', methods=['GET', 'POST'])
def deleteHotel(hotel_id):
    hotelToDelete = session.query(Hotel).filter_by(id=hotel_id).one()
    if 'username' not in login_session:
        return redirect('/login')
    creator = getUserInfo(hotelToDelete.user_id)
    user = getUserInfo(login_session['user_id'])
    # If logged in user != item owner redirect them
    if creator.id != login_session['user_id']:
        flash("You cannot delete this hotel name."
              "This is belongs to %s" % creator.name)
        return redirect(url_for('showMenu'))
    if request.method == 'POST':
        session.delete(hotelToDelete)
        session.commit()
        return redirect(url_for('showMenu', hotel_id=hotel_id))
    else:
        return render_template('deleteHotel.html',
                               hotel=hotelToDelete, hotels=hotelsList)


# show hotel menu
@app.route('/hotel/<int:hotel_id>/')
@app.route('/hotel/<int:hotel_id>/hotelmenu')
def showHotelMenu(hotel_id):
    hotel = session.query(Hotel).filter_by(id=hotel_id).one()
    hotelmenu = session.query(HotelMenu).filter_by(hotel_id=hotel_id).all()
    return render_template('hotelmenu.html', hotel=hotel,
                           hotelmenu=hotelmenu,
                           hotels=hotelsList)


# add new hotel menu
@app.route('/hotel/<int:hotel_id>/hotelmenu/new', methods=['GET', 'POST'])
def newHotelMenu(hotel_id):
    hotel = session.query(Hotel).filter_by(id=hotel_id).one()
    if 'username' not in login_session:
        return redirect('/login')
    creator = getUserInfo(hotel.user_id)
    user = getUserInfo(login_session['user_id'])
    # If logged in user != item owner redirect them
    if creator.id != login_session['user_id']:
        flash("You cannot add new hotel menu."
              "This is belongs to %s" % creator.name)
        return redirect(url_for('showHotelMenu', hotel_id=hotel_id))
    if request.method == 'POST':
        newMenu = HotelMenu(name=request.form['name'],
                            description=request.form['description'],
                            price=request.form['price'],
                            Address=request.form['Address'],
                            hotel_id=hotel_id, user_id=hotel.user_id)
        session.add(newMenu)
        session.commit()
        flash('New Menu %s Item Successfully Created' % (newMenu.name))
        return redirect(url_for('showHotelMenu', hotel_id=hotel_id))
    else:
        return render_template('newhotelmenu.html', hotel_id=hotel_id,
                               hotels=hotelsList)


# edit existing hotel menu
@app.route('/hotel/<int:hotel_id>/hotelmenu/<int:menu_id>/edit',
           methods=['GET', 'POST'])
def editHotelMenu(hotel_id, menu_id):
    if 'username' not in login_session:
        return redirect('/login')
    editedMenu = session.query(HotelMenu).filter_by(id=menu_id).one()
    hotel = session.query(Hotel).filter_by(id=hotel_id).one()
    creator = getUserInfo(editedMenu.user_id)
    user = getUserInfo(login_session['user_id'])
    # If logged in user != item owner redirect them
    if creator.id != login_session['user_id']:
        flash("You cannot edit this hotel name."
              "This is belongs to %s" % creator.name)
        return redirect(url_for('showHotelMenu', hotel_id=hotel_id))
    if request.method == 'POST':
        if request.form['name']:
            editedMenu.name = request.form['name']
        if request.form['description']:
            editedMenu.description = request.form['description']
        if request.form['price']:
            editedMenu.price = request.form['price']
        if request.form['Address']:
            editedMenu.Address = request.form['Address']
        session.add(editedMenu)
        session.commit()
        flash('HotelMenu Successfully Edited')
        return redirect(url_for('showHotelMenu', hotel_id=hotel_id))
    else:
        return render_template('edithotelmenu.html', hotel_id=hotel_id,
                               menu_id=menu_id, item=editedMenu,
                               hotels=hotelsList)


# delete hotel menu
@app.route('/hotel/<int:hotel_id>/hotelmenu/<int:menu_id>/delete',
           methods=['GET', 'POST'])
def deleteHotelMenu(hotel_id, menu_id):
    hotel = session.query(Hotel).filter_by(id=hotel_id).one()
    menuToDelete = session.query(HotelMenu).filter_by(id=menu_id).one()
    if 'username' not in login_session:
        return redirect('/login')
    creator = getUserInfo(menuToDelete.user_id)
    user = getUserInfo(login_session['user_id'])
    # If logged in user != item owner redirect them
    if creator.id != login_session['user_id']:
        flash("You cannot Delete this hotel name."
              "This is belongs to %s" % creator.name)
        return redirect(url_for('showHotelMenu', hotel_id=hotel_id))
    if request.method == 'POST':
        session.delete(menuToDelete)
        session.commit()
        flash('Menu Item Successfully Deleted')
        return redirect(url_for('showHotelMenu', hotel_id=hotel_id))
    else:
        return render_template('deletehotelmenu.html',
                               item=menuToDelete, hotels=hotelsList)


# logout or to disconnect
@app.route('/disconnect')
def disconnect():
    if 'provider' in login_session:
        if login_session['provider'] == 'google':
            gdisconnect()
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        del login_session['user_id']
        del login_session['provider']
        flash("You have successfully been logged out.")
        return redirect(url_for('showLogin'))
    else:
        flash("You were not logged in")
        return redirect(url_for('showHotel'))


if __name__ == '__main__':
    global hotelsList
    app.secret_key = "super_secret_key"
    app.debug = True
    app.run(host='0.0.0.0', port=8000)
