'''
	Author: Brian Sea & Sean Cavalieri
	Setup the routes used by our server
'''


from server import app
from flask import render_template, request, redirect, url_for, make_response, flash

from uuid import uuid4
from hashlib import sha1
import re

from server import database


# The in-memory tokens used to manage CSRF and sessions
sessionTokens = dict()
csrfTokens = dict()

'''
The main route of the server. Shows the login form
''' 
@app.route('/')
def index():

	# If the user is already logged in, redirect them to the view
    sessionID = request.cookies.get('userID')
    if sessionID in sessionTokens:
        return redirect(url_for('view'))


	# Make a CSRF token and send back our index
    token = uuid4()
    csrfTokens[str(token)]=True
    return render_template('index.html', csrf=token)

'''
 Logs the user out
'''
@app.route('/logout')
def logout():

    # Verify CRSF token
    token = request.args.get("csrf")
    if not( token in csrfTokens ):
        flash('Invalid form request')
        return redirect('view')
    del csrfTokens[token]
	
	# If the user is logged in, get rid of the session token
    sessionID = request.cookies.get('userID')
    if sessionID in sessionTokens:
        del sessionTokens[sessionID]

    return redirect(url_for('index'))

'''
Allow the user to register an account
'''
@app.route('/register')
def register():

	# If the user is logged in, redirect them to the view
    sessionID = request.cookies.get('userID')
    if sessionID in sessionTokens:
        return redirect(url_for('view'))

	# Make a CSRF token and send back the register page

    token = uuid4()
    csrfTokens[str(token)]=True
    return render_template('register.html', csrf=token)

'''
Attempt to register a new account
'''
@app.route('/register', methods=['POST'])
def registerPOST():

	# Grab the CSRF token and verify it
    token = request.form.get('token_csrf')
    if not( token in csrfTokens ):
       flash("Invalid Form Request")
       return redirect(url_for('register'))

    # Get rid of the token, so it can't be reused
    del csrfTokens[token]
    username = request.form.get('username')
    sessionID = request.cookies.get('userID')

    # If the user is logged in, then the change is coming from /view
	# We need to redirect them differently
    redirectName = 'register'
    if sessionID in sessionTokens:
        redirectName = 'view'

    password = request.form.get('password')
    if password != request.form.get('vpassword'):
        flash('Passwords do not match')
        return redirect(url_for(redirectName))

    # If the user is logged in, then we just change the password
    if sessionID in sessionTokens:
        username = sessionTokens[sessionID]
    else: 
        if database.isUsernameTaken(username):
            flash( 'Username is already in use.')
            return redirect(url_for(redirectName))
        else:
            # Use regular expressions code from geeksforgeeks to validate username is an email address
            regex = "^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$"
            if not (re.search(regex, username)): 
                # Not an email, invalid. 
                flash('Username must be a valid email address')
                return redirect(url_for(redirectName))
                

	# On success, then we may want to redirect to index
        # Note: This line either changes the password or creates the user depending on whether logged in (has session token)
    if sessionID in sessionTokens:
        # Logged in, so change password
        if not database.changePassword(username, sha1(password.encode()).hexdigest()):
            flash("Failed to Change Password")
    else:
        # Not logged in, so create the user
        database.createUser(username, sha1(password.encode()).hexdigest())

    if redirectName != 'view':
        redirectName = 'index'

    return redirect(url_for(redirectName))

'''
Allows the user to see their profile page
'''
@app.route('/view')
def view():
    sessionID = request.cookies.get('userID')
    if not(sessionID in sessionTokens):
        return redirect(url_for('index'))
    
    # Get url data to check whose profile to view
    id = request.args.get("id")
    if id:
        # url parameter found
        myInfo = database.viewProfileOf(sessionTokens[sessionID])
        theirInfo = database.viewProfileByID(id)
        if theirInfo == []:
            # Invalid id
            return redirect(url_for("view"))
        elif myInfo[0] != theirInfo[0]:
            # Ensure that this isn't the current user's account
            return render_template('view.html', info=myInfo, theirInfo=theirInfo)
        # If here: This is the logged in user's account. Pass through to case of no parameter
            
    # No url parameter found (or chosen user is self)
    token = uuid4()
    csrfTokens[str(token)]=True
    info = database.viewProfileOf(sessionTokens[sessionID])
    return render_template('view.html', csrf=token, info=info)

'''
Attempt to log into an account
'''
@app.route('/view', methods=['POST'])
def login():

	# Verify CRSF token
    token = request.form.get('token_csrf')
    if not( token in csrfTokens ):
        flash('Invalid form request')
        return redirect('view')
    del csrfTokens[token]

    username = request.form.get('username')
    password = request.form.get('password')
    password = sha1(password.encode()).hexdigest()

	# Check that the username and password matches
    if database.authenticate(username, password):
		# Setup a redirect to view
        resp = make_response(redirect(url_for('view')))
        sessToken = str(uuid4())

		# Create a session token and cookie
        sessionTokens[sessToken] = username
        resp.set_cookie('userID', sessToken)
        return resp

	# Invalid... redirect to index
    flash('Invalid username or password')
    return redirect(url_for('index'))

'''
Change the User's Name
'''
@app.route('/changeName', methods=['POST'])
def changeName():

    # Verify CRSF token
    token = request.form.get('token_csrf2')
    if not( token in csrfTokens ):
        flash('Invalid form request')
        return redirect('view')
    del csrfTokens[token]

    # Get info from form and change first and last names
    sessionID = request.cookies.get('userID')
    username = sessionTokens[sessionID]
    newFirstName = request.form.get("fName")
    newLastName = request.form.get("lName")
    userID = request.form.get("userID")
    database.changeFirstLast(userID, newFirstName, newLastName)

    return redirect(url_for('view'))

'''
 Deletes the currently logged in User's Account
'''
@app.route('/deleteAccount')
def deleteAccount():

    # Verify CRSF token
    token = request.args.get("csrf")
    if not( token in csrfTokens ):
        flash('Invalid form request')
        return redirect('view')
    del csrfTokens[token]

    # Delete the User from the Databse
    sessionID = request.cookies.get('userID')
    database.deleteUser(sessionTokens[sessionID])

    # Remove their session token
    sessionID = request.cookies.get('userID')
    if sessionID in sessionTokens:
        del sessionTokens[sessionID]

    return redirect(url_for('index'))

'''
 Shows all Members, and links to their profiles
'''
@app.route('/members')
def members():
    # Must be logged in to view
    sessionID = request.cookies.get('userID')
    if not(sessionID in sessionTokens):
        return redirect(url_for('index'))
    
    info = database.viewProfileOf(sessionTokens[sessionID])
    members = database.viewAllAccounts()
    print(members)
    return render_template('members.html', info=info, members=members)
