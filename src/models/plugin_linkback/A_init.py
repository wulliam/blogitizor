#!/bin/python
"""
This plugin implements linkback specifications for web2py.

The current implementations include Pingback and Trackback.

The pingback specification can be located at
http://www.hixie.ch/specs/pingback/pingback

The trackback specification can be located at
http://www.sixapart.com/pronet/docs/trackback_spec

Common Variables:
source - URL of the article located on YOUR site. LOCAL
target - URL of the article that is being linked to. EXTERNAL
server_url - URL of the linkback server to notify
data - Dictionary of information to send server

"""

if not 'db' in globals() or not 'service' in globals():
    raise HTTP(500, 'plugin_linkback requires ``db`` and ``service``')

from gluon.tools import Storage
linkback = local_import('plugin_linkback')
#-----------------------------------------------------------------------
# 
# Default error codes from the pingback specification.
#
PINGBACK_SOURCE_DOES_NOT_EXIST = 0x0010
PINGBACK_SOURCE_DOES_NOT_LINK  = 0x0011
PINGBACK_TARGET_DOES_NOT_EXIST = 0x0020
PINGBACK_TARGET_CANNOT_BE_USED = 0x0021
PINGBACK_ALREADY_REGISTERED    = 0x0030
PINGBACK_ACCESS_DENIED         = 0x0031
PINGBACK_UPSTREAM_ERROR        = 0x0032
PINGBACK_OK                    = 'OK'
#-----------------------------------------------------------------------
plugin_linkback = Storage()

plugin_linkback.meta = {
    'title': 'Track the Pings',
    'author': 'Thadeus Burgess <thadeusb@thadeusb.com>',
    'keywords': 'trackback, pingback',
    'description': 'Provides a framework for posting and receiving trackbacks and pingbacks',
    'copyright': 'GPL v2',
}
#-----------------------------------------------------------------------
#FIXME: use request.server

#
# This is the URL that points to the pingback and trackback public
# functions. This exposes the reception of trackback form POST and
# pingback xmlrpc handler.
#
plugin_linkback_pingback_server = "http://10.0.0.100:8000" + URL(r=request, c='plugin_linkback', f='call', args='xmlrpc')
plugin_linkback_trackback_server = "http://10.0.0.100:8000" + URL(r=request, c='plugin_linkback', f='receive_trackback')

#-----------------------------------------------------------------------

# Adds pingback headers as to specification.
# You must expose the trackback RDF tags manually.

response.headers['X-Pingback'] = plugin_linkback_pingback_server
response.files.append('<link rel="pingback" href="'+plugin_linkback_pingback_server+'" />')
#-----------------------------------------------------------------------
plugin_linkback.settings = Storage()

# This function is EXTREMELY important for integration with your
# web2py site. All incoming trackback/pingback requests are saved
# to the database, which contains a ``table_name`` and ``record_id`` 
# field. These fields identify which database table and record 
# that this is referring to. This is like a semi-foriegn-key relationship.
#
# The specification will pass a dictionary of data to this function,
# by using this data this function will determine three things.
# 1) The ``table_name`` for the records
# 2) The ``record_id`` of the record being referenced
# 3) If the record is a valid source that can be linked against.
#
# Refer to the plug-ins example app.
def record_identifier(data):
    elements = data['target_url'].split('/')
    
    record_id = elements[-1]
    
    table_name = 'page'
    return table_name, record_id

plugin_linkback.settings.get_record_identifier = record_identifier
