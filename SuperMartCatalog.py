import random
import string
import requests
from flask import make_response
import json
import httplib2
from oauth2client.client import FlowExchangeError
from oauth2client.client import flow_from_clientsecrets
from flask import session as login_session
from flask import Flask, render_template, redirect, url_for, request, jsonify, flash
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database import Base, SuperMart, Categories,USER
app = Flask(__name__)


engine = create_engine('sqlite:///supermartwithusers.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

app = Flask(__name__)

CLIENT_ID=json.loads(open('client_secrets.json',
                          'r').read())['web']['client_id']


@app.route('/login')
def Login():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in range(32))
    login_session['state'] = state
    # return "The current session state is %s" % login_session['state']
    return render_template('login.html', STATE=state)


@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token
    # print("inside gconnect")
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
        # print("except")
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads((h.request(url, 'GET')[1]).decode())
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
        print("Token's client ID does not match app's.")
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('Current user is already connected.'),
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
    login_session['email'] = data['email']



    user_id = getUserId(login_session['email'])
    if not user_id:
        user_id = CreateUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    print("done!")
    return output

def CreateUser(login_session):
    newuser=USER(username=login_session['username'],email=login_session['email'])
    session.add(newuser)
    session.commit()
    user=session.query(USER).filter_by(email=login_session['email']).one()
    return user.id

def GetUserInfo(user_id):
    user=session.query(USER).filter_by(id=user_id).one()
    return user

def getUserId(email):
    try:
        user=session.query(USER).filter_by(email=email).one()
        return user.id
    except:
        return None



#LOGOUT USING /gdisconnect

@app.route('/gdisconnect')
def gdisconnect():
    access_token = login_session.get('access_token')
    if access_token is None:
        print ('Access Token is None')
        response = make_response(json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    print ('In gdisconnect access token is %s', access_token)
    print ('User name is: ')
    print (login_session['username'])
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % login_session['access_token']
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    print ('result is ')
    print (result)
    if result['status'] == '200':
        del login_session['access_token']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    else:
        response = make_response(json.dumps('Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response

#MAIN SUPERMART APP PAGE
@app.route('/')
@app.route('/supermart/')
def SuperMartCategories():
    items = session.query(SuperMart).all()
    if 'username' not in login_session:
         return render_template('publicsupermart.html',items=items)
    else:
        return render_template('supermartcategory.html', items=items)

# ADDED JSON END POINT
@app.route('/')
@app.route('/supermart/JSON')
def SuperMartCategoriesJSON():
    items = session.query(SuperMart).all()
    return jsonify(Category=[i.serialize for i in items])

#TO ADD CATEGORY TO SUPERMART
@app.route('/supermart/addcategory/', methods=['GET', 'POST'])
def AddCategory():
    if 'username' not in login_session:
        return redirect('/login')
    if request.method == 'POST':
        newCategory = SuperMart(category=request.form['category'],user_id= login_session["user_id"])
        session.add(newCategory)
        session.commit()
        flash("NEW CATEGORY ADDED TO SUPERMART !")
        return redirect(url_for('SuperMartCategories'))
    else:
        return render_template('addcategory.html')

#TO DELETE CATEGORY FROM SUPERMART
@app.route('/supermart/<int:supermart_category_id>/deletecategory', methods=['GET', 'POST'])
def DeleteCategory(supermart_category_id):
    deleteCategory = session.query(SuperMart).filter_by(
        id=supermart_category_id).one()
    if 'username' not in login_session:
        return redirect('/login')
    if request.method == 'POST':
        session.delete(deleteCategory)
        session.commit()
        return redirect(url_for('SuperMartCategories'))
    else:
        return render_template('deletecategory.html', supermart_category_id= supermart_category_id, x=deleteCategory)

#TO VIEW SPECIFIC SUPERMART CATEGORY
@app.route('/supermart/<int:supermart_category_id>/')
def ShowCategory(supermart_category_id):
    supermart = session.query(SuperMart).filter_by(
        id=supermart_category_id).one()
    items = session.query(Categories).filter_by(
        supermart_category_id=supermart_category_id)
    if 'username' not in login_session:
         return render_template('publicshowcategory.html',supermart_category_id=supermart_category_id,items=items,x=supermart)
    else:
        return render_template('newcategory.html', supermart_category_id=supermart_category_id, items=items, x=supermart)


# ADDED JSON END POINT

@app.route('/supermart/<int:supermart_category_id>/JSON')
def ShowCategoryJSON(supermart_category_id):
    supermart = session.query(SuperMart).filter_by(
        id=supermart_category_id).one()
    items = session.query(Categories).filter_by(
        supermart_category_id=supermart_category_id)
    # return render_template('newcategory.html', supermart_category_id=supermart_category_id, items=items, x=supermart)
    return jsonify(SupermartCategory=[i.serialize for i in items])

# ADDED JSON end point
@app.route('/supermart/<int:supermart_category_id>/<int:category_id>/JSON')
def ShowItemCategoryJSON(supermart_category_id, category_id):
    itemCategory = session.query(Categories).filter_by(
        id=category_id).one()
    return jsonify(CategoryItem=itemCategory.serialize)


#TO ADD ITEMS OF A PARTICULAR CATEGORY
@app.route('/supermart/<int:supermart_category_id>/additems/', methods=['GET', 'POST'])
def AddNewItem(supermart_category_id):
    if 'username' not in login_session:
        return redirect('/login')
    if request.method == 'POST':
        newCategoryItem = Categories(name=request.form['name'], description=request.form['description'],
                                     price=request.form['price'], offer=request.form['offer'], supermart_category_id=supermart_category_id,user_id=login_session['user_id'] )
        print(login_session['user_id'])
        session.add(newCategoryItem)
        session.commit()
        return redirect(url_for('ShowCategory', supermart_category_id=supermart_category_id))
    else:
        return render_template('newitem.html', supermart_category_id=supermart_category_id)

#TO DELETE ITEM 
@app.route('/supermart/<int:supermart_category_id>/<int:category_id>/deleteitem', methods=['GET', 'POST'])
def DeleteItem(supermart_category_id, category_id):
    if 'username' not in login_session:
        return redirect('/login')
    deleteItem = session.query(Categories).filter_by(
        supermart_category_id=supermart_category_id, id=category_id).one()
    if request.method == 'GET':
        return render_template('deleteitem.html', supermart_category_id=supermart_category_id, category_id=category_id, x=deleteItem)
    if request.method == 'POST':
        session.delete(deleteItem)
        session.commit()
        return redirect(url_for('ShowCategory', supermart_category_id=supermart_category_id))

#TO EDIT AN ITEM
@app.route('/supermart/<int:supermart_category_id>/<int:category_id>/edititem', methods=['GET', 'POST'])
def EditItem(supermart_category_id, category_id):
    if 'username' not in login_session:
        return redirect('/login')
    editCategoryItem = session.query(Categories).filter_by(
        supermart_category_id=supermart_category_id, id=category_id).one()
    if request.method == 'POST':
        if request.form['name']:
            editCategoryItem.name = request.form['name']
        if request.form['description']:
            editCategoryItem.description = request.form['description']
        if request.form['price']:
            editCategoryItem.price = request.form['price']
        if request.form['offer']:
            editCategoryItem.offer = request.form['offer']
        session.add(editCategoryItem)
        session.commit()
        flash("Item edited !")
        return redirect(url_for('ShowCategory', supermart_category_id=supermart_category_id))
    else:
        return render_template('edititem.html', supermart_category_id=supermart_category_id, category_id=category_id, x=editCategoryItem)


if __name__ == '__main__':
    app.debug = True
    app.secret_key = 'the_secretKey'
    app.run(host='0.0.0.0', port=5000, threaded=False)
