'''
	Author: Brian Sea

	Initialize our flask server.  Also include any server configuration needed.
'''


from flask import Flask

app = Flask(__name__)
app.secret_key = b'my_Wonderous_Secret_key'

from server import routes
