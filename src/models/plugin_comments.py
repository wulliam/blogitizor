# REQUIRES AND IMPORTS
###########################################################
if not 'db' in globals() or not 'auth' in globals():
    raise HTTP(500, 'plugin_comments requires "db" and "auth"')

from gluon.tools import Storage

#response.files.append(URL(r=request, c='static', f='plugin_comments/comments.css'))

# META INFO
###########################################################
plugin_comments = Storage()

plugin_comments.meta = {
    'title': 'Commentizor',
    'author': 'Thadeus Burgess <thadeusb@thadeusb.com>',
    'keywords': 'comments, commenting, blog',
    'description': 'Provides a comment framework',
    'copyright': 'GPL v2'
}

# SETTINGS
###########################################################
plugin_comments.settings = Storage()

# Enable recaptcha to post comments
plugin_comments.settings.recaptcha = True

# Should users that are logged into auth get a captcha?
plugin_comments.settings.no_recaptcha_for_users = True

# If a user is logged in, should it prefill their name/email/website information?
plugin_comments.settings.auto_fill_users = True

# If we do auto fill, and the user is logged in, set the defaults.
if plugin_comments.settings.auto_fill_users and auth.is_logged_in():
        plugin_comments.settings.auth_name = "%(first_name)s %(last_name)s" % auth.user
        plugin_comments.settings.auth_email = "%(email)s" % auth.user
        plugin_comments.settings.auth_site = "%(site)s" % auth.user

# MARKDOWN SETTINGS
###########################################################
# Formats available
# 'text' - text/plain
# 'wiki' - markdown
# 'xml' - permitted tags

# Format
plugin_comments.settings.markdown = 'wiki'

# Permitted Tags (xml format only)
plugin_comments.settings.markdown_permitted_tags = ['b', 'blockquote', 'br/', 'i', 'li', 'ol', 'ul', 'p', 'cite', 'code', 'pre']

# WMD, javascript markdown WYSIWYM textarea editor (wiki only)
# Path to javascript
plugin_comments.settings.markdown_wmd_loc = URL(r=request, c='static', f='js/wmd/wmd.js')

# WMD Buttons
plugin_comments.settings.markdown_wmd_btn = "heading bold italic | link blockquote code image | ol ul hr"

# Location to WIKI preview (ajax based)
plugin_comments.settings.markdown_wmd_prv = URL(r=request, c='plugin_comments', f='preview_markdown')

#if false, will use wmd builtin preview functionality
# Not Implemented.
#TODO: Implement.
plugin_comments.settings.markdown_wmd_ajax = True
       

# RSS SETTINGS
###########################################################
# Link to where RSS feed is located.
plugin_comments.settings.rss = 'http://'+request.env.http_host+'/'+request.application+'/plugin_comments/feed.rss/%(table_name)s/%(record_id)s'
# Link to the actual comment.
plugin_comments.settings.rss_link = 'http://1'+request.env.http_host+'/'+request.application+'/plugin_comments/comment/%(table_name)s/%(record_id)s#comment-%(comment_id)s'
# Data to fill into rss_link.. Should be a dict.
# This will use python's % operator to insert the data into the string.
plugin_comments.settings.rss_link_dict = dict(table_name='-default', record_id='-2', comment_id='-1')

# Recaptcha widget.
if plugin_comments.settings.recaptcha:
    plugin_comments_captcha = lambda f,v: Recaptcha(request, configure.read('blogitizor', 'recaptcha_public'), configure.read('blogitizor', 'recaptcha_private'))

# DATABASE DEFINITIONS
###########################################################
# Comment
db.define_table('plugin_comments_comment',
    Field('r_name'),
    Field('r_email', requires=IS_EMAIL()),
    Field('r_site', requires=IS_NULL_OR(IS_URL())),
    Field('content', 'text', requires=IS_NOT_EMPTY()),
    Field('posted_on', 'datetime', default=request.now, writable=False, readable=False),
)

# Links a comment to a table_name / record_id
db.define_table('plugin_comments_link',
    Field('comment', db.plugin_comments_comment),
    Field('table_name'),
    Field('record_id', 'integer'),
    Field('linked_on', 'datetime', default=request.now, writable=False, readable=False),
)

# Orderby.
plugin_comments.settings.orderby = db.plugin_comments_link.linked_on


# DATABASE COMMENTS / LABELS
###########################################################
# Comment if wiki or xml.
if plugin_comments.settings.markdown == 'wiki':
    from gluon.contrib.markdown import WIKI
    msg = """
    <b><a href="http://daringfireball.net/projects/markdown/syntax">Markdown</a> syntax is supported for comments.</b>
    """
elif plugin_comments.settings.markdown == 'xml':
    msg = """
    <b>HTML formatting is supported. Permitted tags: ['b','blockquote','br/','i','li','ol','ul','p','cite','code','pre']</b>
    """
else:
    msg = """
    <b>Comments are in text/plain format.</b>
    """

db.plugin_comments_comment.content.comment = XML(msg)

db.plugin_comments_link.comment.requires = IS_IN_DB(db, 'plugin_comments_comment.id')


# COMMENT FUNCTIONS / QUERIES
###########################################################

def plugin_comments_for(table_name, record_id):
    """
    Get comments for ``table_name`` and ``record_id``
    Returns a web2py query object, you will need to perform your own
    .select() to get the results.
    
    Keyword arguments:
    table_name -- Name of the table for foriegn key relationship
    record_id -- ID of the record in foriegn key table.
    
    Returns:
    query object.
    """
    return db(db.plugin_comments_link.table_name == table_name)(db.plugin_comments_link.record_id == record_id)
    
def plugin_comments_load(table_name, record_id):
    """
    Returns web2py's LoadFactory for ``table_name`` and ``record_id``
    Calls the plugin's comment action.
    """
    return LOAD('plugin_comments', 'comment', args=(table_name, record_id))
    
def plugin_comments_feed_items(table_name, record_id):
    """
    Creates a RSS dictionary for ``table_name`` and ``record_id``.
    This dictionary is formatted for web2py's RSS and can be returned directly
    from an rss action as the items attribute.
    """
    # Get comments
    comments = plugin_comments_for(table_name, record_id).select(orderby=plugin_comments.settings.orderby)
    items = []
    
    plugin_comments.settings.rss_link_dict['table_name'] = table_name
    plugin_comments.settings.rss_link_dict['record_id'] = record_id
    
    # Build the rss.
    for row in comments:
        plugin_comments.settings.rss_link_dict['comment_id'] = row.comment.id
            
        item = dict(
            title=row.comment.r_name or 'Anonymous',
            link = plugin_comments.settings.rss_link % (plugin_comments.settings.rss_link_dict),
            description=XML(row.comment.content, sanitize=True, permitted_tags=[]).xml(),
            created_on=row.comment.posted_on,
        )
        items.append(item)
    return items
    
# LABELS
db.plugin_comments_comment.r_name.label = "Name"
db.plugin_comments_comment.r_email.label = "Email Address (required)"
db.plugin_comments_comment.r_email.comment = "Will not be published"
db.plugin_comments_comment.r_site.label = "Website"
db.plugin_comments_comment.content.label = "Your Message"

# GRAVATAR
###########################################################
def plugin_comments_gravatar_url(email="", default="http://"+request.env.http_host+"/"+request.application+'/static/plugin_comments/default_gravatar.jpg', size=40):
    """
    Generates a gravatar url for comments using email
    
    Keyword arguments:
    email -- Email to encode for gravatar
    default -- Link to location of the default image if gravatar does not exist
    size -- Size of gravatar image.
    """
    # import code for encoding urls and generating md5 hashes
    import urllib, hashlib
    
    if not email:
        email=""
    gravatar_url = "http://www.gravatar.com/avatar.php?"
    gravatar_url += urllib.urlencode({'gravatar_id':hashlib.md5(email).hexdigest(),
            'default': default, 'size':str(size)})
    return gravatar_url
    
    
    
