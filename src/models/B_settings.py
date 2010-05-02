# coding: utf8

# Meta
###########################################################
__author__ = "Thadeus Burgess <thadeusb@thadeusb.com>"
__copyright__ = "Copyright 2009-2010 Thadeus Burgess. GNU GPL v3."
__site_name__ = "Blogitizer"
__version__ = ".05"
###########################################################

if request.env.http_host.endswith('8000'):
    DEV = True
else:
    DEV = False

# Imports
###########################################################
from gluon.tools import *
from gluon.contrib.markdown import WIKI

# External Imports
###########################################################
import web2py_utils
from web2py_utils import widgets
from web2py_utils.configure import Configure
from web2py_utils.category import CategoryPlugin
from web2py_utils.py2jquery import py2jquery
from web2py_utils.menu import MenuManager
from web2py_utils import auth_patches
from web2py_utils.paginate import Pagination
from web2py_utils import search
from web2py_utils.output import compress_output

# admin = utils.AdminManager(request, URL)

#def admin_test_hello_world_dispatcher():
#    def ielloworld():
#        response.view = 'admin/ielloworld.html'

#        action = request.args(1) or 'index'

#        if action == 'index':
#            return dict(hi=A("hi", _href=admin.url(ielloworld, args=['hi'])), hello=None)
#        elif action == 'hi':
#            return dict(hello=A("hello", _href=admin.url(ielloworld, args=['index'])), hi=None)

#    admin.register(ielloworld)

# Module Imports
###########################################################
###########################################################

# Non Database Global Settings
###########################################################
if DEV:
    pool_size = 1
else:
    pool_size = 10

migrate_db = True

URL = web2py_utils.gURL(request)
widgets.replace_all(SQLFORM, ui=True)

compress_output(response, debug=DEV)
###########################################################

# DAL
###########################################################
db = DAL(dal_connection, pool_size=pool_size)
###########################################################

# OBJECTS
###########################################################
if not 'fixtures' in globals().keys():
    fixtures = {}

configure = Configure(db)
dbcategory = CategoryPlugin(db)(migrate_db)
manager = py2jquery.Manager(globals())
menu = MenuManager(request)

configure.verify('layout', {
    'current': {
        'value': '',
        'description': """
            The current layout to use.
        """,
    },
    'admin_layout': {
        'value': 'admin',
        'description': """
            The layout to use for admin.
        """
    }
})

if request.controller == 'admin':
    LAYOUT_NAME = configure.read('layout', 'admin_layout')
else:
    LAYOUT_NAME = configure.read('layout', 'current')
    
layout = web2py_utils.LayoutManager(request, response, URL, 
                        LAYOUT_NAME)
###########################################################

# Database Stored Settings
###########################################################
configure.verify('site-settings', {
    'recaptcha_public': {
        'value': fixtures.get('site-settings', {}).get('recaptcha_public', ''),
        'description': 'Your recaptcha public key',
    },
    'recaptcha_private': {
        'value': fixtures.get('site-settings', {}).get('recaptcha_private', ''),
        'description': 'Your recaptcha private key',
    },
    'mail_server': {
        'value': fixtures.get('site-settings', {}).get('mail_server', ''),
        'description': 'Server to send mail from (smtp)',
    },
    'mail_sender': {
        'value': fixtures.get('site-settings', {}).get('mail_sender', ''),
        'description': 'Email address to send mail as',
    },
    'mail_login': {
        'value': fixtures.get('site-settings', {}).get('mail_login', ''),
        'description': 'Login for the server',
    },
    'ga_tracker': {
        'value': fixtures.get('site-settings', {}).get('ga_tracker', ''),
        'description': 'Your google analytics unique id key'
    }
})

configure.verify('openid', {
    'provider': {
        'value': fixtures.get('openid', {}).get('provider', ''),
        'description': 'Open ID Provider',
    },
    'local_id': {
        'value': fixtures.get('openid', {}).get('local_id', ''),
        'description': 'Local ID for OpenID',
    },
    'server': {
        'value': fixtures.get('openid', {}).get('server', ''),
        'description': 'Open ID Server',
    },
    'delegate': {
        'value': fixtures.get('openid', {}).get('delegate', ''),
        'description': 'Open ID Delegate'
    }
})
###########################################################
