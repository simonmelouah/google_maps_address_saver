# Google maps address saver
## Summary ##
A small Django application that combines fusion tables with google maps to store clicked locations.
See https://youtu.be/ljYlj4fH_ng for a video summary of its functionality in action.

## Features ##
* Authenticate with google account
* Creates a fusion table and stores it in your google drive
* Renders a google map
* When a location is clicked it checks to see if the address is valid
* If the address is valid it stores it in a sqlite table and the fusion table
* A marker is then set on the map with all the places that were clicked
* Users can reset the fusion and sqlite table with the delete button

## How to run locally ##
* Pull code down locally
* Create a virtualenv and activate it
* run `pip3 install requirements.txt ; python3 manage.py migrate ; python3 manage.py runserver`
* Open a browser window and navigate to http://localhost:8000/install
