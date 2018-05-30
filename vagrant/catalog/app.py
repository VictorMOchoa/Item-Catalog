from flask import Flask, render_template, url_for, request, redirect
from flask import flash, jsonify, make_response
from flask import session as login_session
from sqlalchemy import create_engine, asc, desc
from sqlalchemy.orm import sessionmaker
from database_setup import *
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
from login_decorator import login_required
import json
import httplib2
import random
import string
import os
import requests

# Create a new instance of flask
app = Flask(__name__)

# G-Client preperation
CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "ItemCatalog"

# Connect to the database and bind
engine = create_engine('sqlite:///item_catalog.db?check_same_thread=False')
Base.metadata.bind = engine
# Create a new database session
DBSession = sessionmaker(bind=engine)
session = DBSession()


# Create anti-forgery state token
@app.route('/login')
def showLogin():
    state = ''.join(
        random.choice(string.ascii_uppercase + string.digits)
        for x in range(32))
    login_session['state'] = state
    return render_template('login.html', STATE=state)


# This function enables the user to log in with their google account
@app.route('/gconnect', methods=['POST'])
def gconnect():
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    request.get_data()
    code = request.data.decode('utf-8')

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
    # Submit request, parse response - Python3 compatible
    h = httplib2.Http()
    response = h.request(url, 'GET')[1]
    str_response = response.decode('utf-8')
    result = json.loads(str_response)

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
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(json
                                 .dumps('Current user is already connected.'),
                                 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['access_token'] = access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    # see if user exists, if it doesn't make a new one
    user_id = getUserIdByEmail(login_session['email'])
    if not user_id:
        user_id = createNewUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;'\
              '-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    flash("you are now logged in as %s" % login_session['username'])
    print "done!"
    return output


# This function will execute if trying to disconnect a logged in user
@app.route('/gdisconnect')
def gdisconnect():
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
        # Refresh all user settings
        del login_session['access_token']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        # Send the user back to the home page
        response = redirect('http://localhost:5000/', code=302)
        return response
    else:
        response = make_response(
            json.dumps('Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response


# The below functions will help with user registration as far as lookup
# and preventing conflict
def createNewUser(login_session):
    newUser = User(name=login_session['username'], email=login_session[
                   'email'], picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


def getUserIdByEmail(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None


# This function retrieves the
def getOwnerInfo(user_id):
    user = session.query(User).filter_by(id=user_id).one()
    return user


# If the user is on the home page or catalog page, show the latest items
@app.route('/')
@app.route('/catalog/')
def showCatalog():
    categories = session.query(Category).order_by(asc(Category.name))
    items = session.query(Item).order_by(desc(Item.name)).limit(4)
    return render_template('catalog.html', categories=categories, items=items)


# This function is used to display the details of an individual item
@app.route('/catalog/<path:category_name>/<path:item_name>/')
def showItem(category_name, item_name):
    item = session.query(Item).filter_by(name=item_name).one()
    item_owner = getOwnerInfo(item.user_id)
    categories = session.query(Category).order_by(asc(Category.name))
    # If the user is not logged in, they will not be able to modify their items
    if 'username' not in login_session:
        return render_template('public_item_details.html', item=item,
                               category=category_name, categories=categories)
    else:
        return render_template('item_details.html', item=item,
                               category=category_name, categories=categories,
                               item_owner=item_owner,
                               current_user=login_session['user_id'])


# This function is used to display all of the items in a category
@app.route('/catalog/<path:category_name>/items/')
def showCategory(category_name):
    categories = session.query(Category).order_by(asc(Category.name))
    category = session.query(Category).filter_by(name=category_name).one()
    items = session.query(Item).filter_by(category=category).order_by(asc(Item.name)).all()
    count = session.query(Item).filter_by(category=category).count()
    # If no user logged in, go to item page with no add item button
    if 'username' not in login_session:
        return render_template('public_items.html', category=category.name,
                               categories=categories,
                               items=items, count=count)
    else:
        return render_template('items.html', category=category.name,
                               categories=categories, items=items, count=count)


# Below are the CRUD Operations for the site
# Create a new item
@app.route('/catalog/add_new_item', methods=['GET', 'POST'])
@login_required
def addNewItem():
    categories = session.query(Category).all()
    if request.method == 'POST':
        tempItem = Item(
            name=request.form['name'],
            description=request.form['description'],
            picture=request.form['picture'],
            category=session.query(Category)
            .filter_by(name=request.form['category']).one(),
            user_id=login_session['user_id'])
        session.add(tempItem)
        session.commit()
        return redirect(url_for('showCatalog'))
    else:
        return render_template('add_new_item.html',
                               categories=categories)


# Edit an existing item in the catalog (if you are the owner)
@app.route('/catalog/<path:category_name>/<path:item_name>/edit',
           methods=['GET', 'POST'])
@login_required
def editItem(category_name, item_name):
    modifiedItem = session.query(Item).filter_by(name=item_name).one()
    categories = session.query(Category).all()
    if request.method == 'POST':
        if request.form['name']:
            modifiedItem.name = request.form['name']
        if request.form['description']:
            modifiedItem.description = request.form['description']
        if request.form['picture']:
            modifiedItem.picture = request.form['picture']
        if request.form['category']:
            category = session.query(Category)
            .filter_by(name=request.form['category']).one()
            modifiedItem.category = category
        session.add(modifiedItem)
        session.commit()

        return redirect(url_for('showCategory',
                                category_name=modifiedItem.category.name))
    else:
        return render_template('edit_item.html', item=modifiedItem,
                               categories=categories)


# This function is used by owners to delete one of their items
@app.route('/catalog/<path:category_name>/<path:item_name>/delete',
           methods=['GET', 'POST'])
@login_required
def deleteItem(category_name, item_name):
    itemToDelete = session.query(Item).filter_by(name=item_name).one()
    category = session.query(Category).filter_by(name=category_name).one()
    categories = session.query(Category).all()
    if request.method == 'POST':
        session.delete(itemToDelete)
        session.commit()
        return redirect(url_for('showCategory', category_name=category.name))
    else:
        return render_template('delete_item.html', item=itemToDelete)


@app.route('/catalog/JSON')
def allItemsJSON():
    categories = session.query(Category).all()
    category_items = [category.serialize for category in categories]
    for category in range(len(category_items)):
        items = [i.serialize for i in session.query(Item)
                 .filter_by(category_id=category_items[category]["id"]).all()]
        if items:
            category_items[category]["Item"] = items
    return jsonify(Category=category_items)

if __name__ == '__main__':
    app.secret_key = 'secret'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
