import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)
# FOR DEBUGGING PURPOSES
REQUIRED_LOGIN = False

'''
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
'''
#db_drop_and_create_all()

"""
https://review.udacity.com/#!/rubrics/2593/view
Barista access is limited:

    can get drinks
    can get drink-details

Manager access is limited

    can get drinks
    can get drink details
    can post drinks
    can patch drinks
"""
    
## ROUTES
###########################################################################
#                               GET /drinks [Permissions: All]
###########################################################################
'''
@TODO implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
#  [OK] TESTED GET : https://127.0.0.1:5001/drinks
@app.route('/drinks')
# no login required for this end point (general view)
def get_drinks():
    try:
        # Get all drinks from database
        all_drinks = Drink.query.all()
        
        # Successful query, return 200 with drinks data
        return jsonify({
            'drinks': [drink.short() for drink in all_drinks],
            'success': True,
        }), 200
    # FAILED: return 422 response
    except Exception:
        abort(422)
###########################################################################
#                               GET /drinks-detail [Permissions: Barista & Manager]
###########################################################################
'''
@TODO implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
#[OK] TESTES GET : https://127.0.0.1:5001/drinks-detail
@app.route('/drinks-detail')
#if REQUIRED_LOGIN is True:
@requires_auth('get:drinks-detail')
def get_drinks_detail(token):
#def get_drinks_detail():
    try:
        # get all the available drinks detail
        all_drinks = Drink.query.all()
        #REQUIRED: it should contain the drink.long() data representation
        return jsonify({
            'drinks': [drink.long() for drink in all_drinks],
            'success': True,
        }), 200
    except Exception:
        abort(422)
        
###########################################################################
#                               POST /drinks [Permissions: Manager ONLY]
###########################################################################
'''
@TODO implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''
# [OK] - TESTED - see postman example below to insert
@app.route('/drinks', methods=['POST'])
#@requires_auth('post:drinks')
#def create_drink(jwt):
def post_drink():
    try:
        # get data from form and assign a the value to a variable called data
        data = dict(request.form or request.json or request.data)
        #Assing the drink title with none as the default value
        title = data.get('title', None)
        #Assign the cepipe blob details with none as the default value
        recipe = data.get('recipe', None)
        # format the data into a drink object
        drink = Drink(title=title, recipe=json.dumps(recipe))
        # add the drink details into the database
        drink.insert()

        # On sucessful, return the json object with the new drink. You can view this using Postman on the backend server
        return jsonify({
            'drinks': drink.long(),
            'success': True,
        }), 200
    except Exception:
        abort(500)
"""
EXAMPLE POSTMAN INSERT NEW COFFEE DRINK
POST: https://127.0.0.1:5001/drinks
OPTIONS: Body > raw[x] > JSON^
{
    "title": "expresso",
    "recipe": [{
        "color": "blue", 
        "name":"mr. express", 
        "parts":1
        }]

}
"""        
 ###########################################################################
#                               PATCH /drinks/<id> [Permissions: Manager ONLY]
###########################################################################       

'''
@TODO implement endpoint
    PATCH /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should update the corresponding row for <id>
        it should require the 'patch:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the updated drink
        or appropriate status code indicating reason for failure
'''
#[OK] - POST https://127.0.0.1:5001/drinks/1
@app.route('/drinks/<int:id>', methods=['PATCH'])
#@requires_auth('patch:drinks')
def patch_drink(id):
    print("id =" + str(id))
    try:
        # get data from form and assign a the value to a variable called data
        data = dict(request.form or request.json or request.data)
        # find drink id in database
        drink = drink = Drink.query.filter(Drink.id == id).one_or_none()
         # if drink id not found, return a 404 error
         # it should respond with a 404 error if <id> is not found
        if drink:
            # Since drink id was found in db, lets update the newly submitted details if any
            drink.title = data.get('title') if data.get('title') else drink.title
            #create object of submittted data if any
            recipe = data.get('recipe') if data.get('recipe') else drink.recipe
            #assigned submitted recipe details
            drink.recipe = recipe if type(recipe) == str else json.dumps(recipe)
            #it should update the corresponding row for <id>
            drink.update()
            #SUCCESSFUL, NO ERRORS
            return json.dumps({
                #it should contain the drink.long() data representation
                'drinks': [drink.long()],
                'success': True
            }), 200
        else:
            # Return 404 error because this drink id was not found. example id = 10000
            return json.dumps({
                'success':False,
                'error':'Drink id =' + str(id) + ' was not found.'
            }), 404
    except:
        return json.dumps({
            'success': False,
            'error': "An error occurred"
        }), 422
"""
EXAMPLE POSTMAN INSERT NEW COFFEE DRINK
POST: https://127.0.0.1:5001/drinks/1
OPTIONS: Body > raw[x] > JSON^
{
    "title": "4TH edited",
    "id": 100,
    "recipe": [{
        "color": "yellow", 
        "name":"name2", 
        "parts":1
        }]

}
"""  


###########################################################################
#                               DELETE /drinks/<id> [Permissions: Manager ONLY]
###########################################################################
'''
@TODO implement endpoint
    DELETE /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
    returns status code 200 and json {"success": True, "delete": id} where id is the id of the deleted record
        or appropriate status code indicating reason for failure
'''
# [OK] TESTED - DELETE https://127.0.0.1:5001/drinks/3
@app.route('/drinks/<int:id>', methods=['DELETE'])
#@requires_auth('delete:drinks')
#def delete_drink(jwt, id):
def delete_drink(id):
    
    drink = Drink.query.filter(Drink.id == id).one_or_none()
    # it should respond with a 404 error if <id> is not found
    if drink is None:
        abort(404)

    try:
        #it should delete the corresponding row for <id>
        drink.delete()
    except BaseException:
        abort(400)
    return jsonify({
        'delete': id,
        'success': True, 
        }), 200

# ~~~~~~~~~~~~~~~~~~~~~~~        Error Handling      ~~~~~~~~~~~~~~~~~~~~~~~

###########################################################################
#                               422
###########################################################################
'''
Example error handling for unprocessable entity
'''
@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
                    "success": False, 
                    "error": 422,
                    "message": "unprocessable"
                    }), 422
###########################################################################
#                               404
###########################################################################
'''
@TODO implement error handlers using the @app.errorhandler(error) decorator
    each error handler should return (with approprate messages):
             jsonify({
                    "success": False, 
                    "error": 404,
                    "message": "resource not found"
                    }), 404

'''
@app.errorhandler(404)
def resource_not_found(error):
    return jsonify({
                    "success": False, 
                    "error": 404,
                    "message": "resource not found"
                    }), 404
    
###########################################################################
#                               400
###########################################################################    
@app.errorhandler(400)
def bad_request(error):
    return jsonify({
                    "success": False, 
                    "error": 400,
                    "message": "bad request"
                    }), 400
###########################################################################
#                               500
###########################################################################    
@app.errorhandler(500)
def internal_server_error(error):
    return jsonify({
                    "success": False, 
                    "error": 500,
                    "message": "internal server error"
                    }), 500
###########################################################################
#                               error handler
###########################################################################     
'''
@TODO implement error handler for AuthError
    error handler should conform to general task above 
'''
@app.errorhandler(AuthError)
def auth_error(error):
    return jsonify({
        "success": False,
        "error": error.status_code,
        "message": error.error['description']
    }), error.status_code