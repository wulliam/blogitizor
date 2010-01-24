# coding: utf8

# Meta
###########################################################
__author__ = "Thadeus Burgess <thadeusb@thadeusb.com>"
__copyright__ = "Copyright 2009-2010 Thadeus Burgess. GNU GPL v3."
__site_name__ = "Blogitizer"
__version__ = ".05"
###########################################################

# Imports
###########################################################
from gluon.tools import *
from gluon.contrib.markdown import WIKI

plugin_category = local_import('plugin_category')
plugin_py2jquery = local_import('plugin_py2jquery')
utils = local_import('utils')
###########################################################

# Non Database Global Settings
###########################################################
if request.env.http_host.endswith('8000'):
    dal_connection = 'sqlite://blogitizor.sqlite'
    pool_size = 1
    cache.ram.clear()
    cache.disk.clear()
else:
    dal_connection = 'xxx'
    pool_size = 10

migrate_db = True
WEBLOG = 'weblog'
###########################################################

# DAL
###########################################################
db = DAL(dal_connection, pool_size=pool_size)
###########################################################

# Database Stored Settings
###########################################################
configure = utils.Configure(db)

configure.verify('blogitizor', {
    'recaptcha_public': {
        'value': 'xxx',
        'description': 'Your recaptcha public key',
    },
    'recaptcha_private': {
        'value': 'xxx',
        'description': 'Your recaptcha private key',
    },
    'mail_server': {
        'value': 'xxx.com',
        'description': 'Server to send mail from (smtp)',
    },
    'mail_sender': {
        'value': 'xxx@xxx.com',
        'description': 'Email address to send mail as',
    },
    'mail_login': {
        'value': 'xxx@xxx.com:xxx',
        'description': 'Login for the server',
    },
    'ga_tracker': {
        'value': 'xxx',
        'description': 'Your google analytics unique id key'
    }
})
###########################################################
