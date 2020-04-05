'''
	Author: Brian Sea
	Setup the routes used by our server
'''


from server import app
from flask import render_template, request, redirect, url_for, make_response, flash

from uuid import uuid4
from hashlib import sha1


# TODO: Add Database import here
# TODO: Database code should be a DIFFERENT file

userPasswords = dict()

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
    elif username in userPasswords:
        flash( 'Username is already in use.')
        return redirect(url_for(redirectName))

	# On success, then we may want to redirect to index
    userPasswords[username] = sha1(password.encode()).hexdigest()
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

    token = uuid4()
    csrfTokens[str(token)]=True
    return render_template('view.html', csrf=token, username=sessionTokens[sessionID])

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
    if username in userPasswords and userPasswords[username] == password:
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
