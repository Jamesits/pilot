#!/usr/bin/env python3

import sys
sys.path.append('./gobgp_interface')

from project import create_app

# Call the Application Factory function to construct a Flask application instance
# using the standard configuration defined in /instance/flask.cfg
app = create_app('flask.cfg')
