# Item Catalog


## Background
The last project in the Back-end/Database module for Udacity's Full-Stack Nanodegree. The assignment is to build a web application using virtual-box, vagrant, the Flask framework, and Google Auth which will allow users to browse a sports item catalog. With this catalog, users can register with their Google Account and then add, edit, delete (essentially perform all of the CRUD operations) on items which they own. The purpose of the project is to utilize the skills we have learned about responsive web design with the newly learnt database and authorization principles from this module.

## Pre-Requisites
1. Python (At least 2.7)
2. Vagrant
3. Virtual Box

## How to use

 1. Unzip the project file to your machine
 2. Open command line in the vagrant folder
 3. Launch the vagrant virtual machine with the command
 `vagrant up`
 4. Next, start Ubuntu with
 `vagrant ssh`
 5. Navigate to the correct folder
 `cd /vagrant/catalog`
 6. The database is initially empty so populate it with
 `python starter_data.py`
 7. Finally, run the app by typing
 `python app.py`
 8. In your web browser, navigate to
 `http://localhost:5000/`
 9. All items in the catalog can be viewed at
 `http://localhost:5000/catalog/JSON`

## Technologies used
 - JavaScript
 - jQuery
 - CSS
 - Python
 - Flask
 - Virtual Box
 - Vagrant
 - Google Auth
