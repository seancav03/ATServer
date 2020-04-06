'''
	Author: Brian Sea

	Initialize our flask server.  Also include any server configuration needed.
'''


from flask import Flask

app = Flask(__name__)
app.secret_key = b'my_SuUupPP3rrr_Wond3r0us_Secr3t_k3y'

from server import routes
