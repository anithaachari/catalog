## Item Catalog Web App

## By Kuduthuru Anitha This web app is a project for the Udacity FSND Course.

About

This project is a RESTful web application utilizing the Flask framework which accesses a SQL database that populates hotels and hotelmenus. OAuth2 provides authentication for further CRUD functionality on the application. Currently OAuth2 is implemented for Google Accounts.

In This Project

This project has one main Python module project.py which runs the Flask application. A SQL database is created using the database_setup.py module and you can populate the database with test data using hoteldata.py. The Flask application uses stored HTML templates in the templates folder to build the front-end of the application.

Skills Required
Python
HTML
CSS
OAuth
Flask Framework
sqlalchemy
Installation
There are some dependancies and a few instructions on how to run the application. Seperate instructions are provided to get GConnect working also.
Dependencies
Vagrant
Udacity Vagrantfile
VirtualBox
How to Install
Install Vagrant & VirtualBox
Clone the Udacity Vagrantfile
Go to Vagrant directory and either clone this repo or download and place zip here
Launch the Vagrant VM (vagrant up)
Log into Vagrant VM (vagrant ssh)
Navigate to cd /vagrant as instructed in terminal

The app imports requests which is not on this vm. Run pip install requests
Or you can simply Install the dependency libraries (Flask, sqlalchemy, requests,psycopg2 and oauth2client) by running pip install -r 
requirements.txt

Setup application database python/myhotel2/database_setup.py
*Insert sample data python/myhotel2/hoteldata.py
Run application using python /myhotel2/project.py
Access the application locally using http://localhost:8000
*Optional step(s)

Using Google Login

To get the Google login working there are a few additional steps:

Go to Google Dev Console

Sign up or Login if prompted

Go to Credentials

Select Create Crendentials > OAuth Client ID

Select Web application

Enter name 'HotelMenu Project'

Authorized JavaScript origins = 'http://localhost:8000'

Authorized redirect URIs = 'http://localhost:8000/login' && 'http://localhost:8000/gconnect'

Select Create

Copy the Client ID and paste it into the data-clientid in login.html

On the Dev Console Select Download JSON

Rename JSON file to client_secrets.json

Place JSON file in myhotel2 directory that you cloned from here

Run application using python/hotel/project.py

JSON Endpoints

The following are open to the public:

Hotel Catolog JSON: /hotel/JSON - Displays the all hotels catalog.

Hotel Menu JSON: /hotel/hotelmenu/JSON-Displays all hotel menus.

Hotel menu JSON: /hotel/<int:hotel_id>/menu/JSON - Displays menus of specific hotel. 

Hotel Menu JSON:/hotel/<int:hotel_id>/menu/<int:menu_id>/JSON  - Displays the menu of specific hotel in hotels.


Miscellaneous

This project is inspiration from gmawji.
