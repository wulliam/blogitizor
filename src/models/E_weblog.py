# SETTINGS
###########################################################
if 0:
    from gluon.sql import *
    from gluon.sqlhtml import *
    from gluon.tools import *
    from gluon.html import *
    from gluon.http import *
    from gluon.storage import *
    from thadeusb.modules.utils import *
    db = DAL
    configure = Configure

configure.verify('page', {
    'display_count': {
        'value': 4,
        'description': "Number of posts to display per-page",
    },
    'rss_display_count': {
        'value': 15,
        'description': "Number of posts to display on RSS feed",
    }
})

# TABLE DEFINITIONS
###########################################################
db.define_table('page',
    Field('author', db.auth_user, writable=False),
    Field('title', required=True),
    Field('slug', unique=True, required=True),
    Field('type', required=True, default='post'),
    Field('categories'),
    Field('content', 'text'),
    Field('posted_on', 'datetime', default=request.now),
    Field('status', default='draft'),
    migrate=migrate_db
)

class Page():    
    def url(self):
        return lambda: URL(r=request, c=WEBLOG, f='view', args=self.page.slug)
    def permalink(self):
        return lambda: URL(r=request, c=WEBLOG, f='archive', args=[self.page.posted_on.year, self.page.posted_on.month, self.page.posted_on.day, self.page.slug, self.page.id])

db.page.virtualfields.append(Page())
    
db.page.author.default = auth.user.id if auth.user else 0
db.page.author.represent = lambda id: db.auth_user[id].username
db.page.author.requires = IS_IN_DB(db, 'auth_user.id', 'auth_user.username')

db.page.title.requires = IS_NOT_EMPTY()

db.page.slug.requires = [IS_ALPHANUMERIC(), IS_NOT_IN_DB(db, 'page.slug')]

db.page.type.requires = IS_IN_SET(['post', 'page', 'project'])

db.page.status.requires = IS_IN_SET(['draft', 'review', 'publish', 'stone'])

db.page.categories.requires = IS_NULL_OR(dbcategory.requires(True))
db.page.categories.widget = dbcategory.checkboxes_widget()
db.page.categories.represent = dbcategory.represent(', ')

db.page.content.widget = RESIZABLE.widget
db.page.content.requires = IS_NOT_EMPTY()

db.define_table('file',
    Field('title'),
    Field('uploaded_data', 'upload'),
    Field('type'),
    Field('created_on', 'datetime', writable=False, default=request.now)
)
db.file.uploaded_data.autodelete=True
db.file.type.requires = IS_IN_SET(('image', 'document', 'movie', 'text', 'other'))

db.define_table('file_links',
    Field('page', db.page),
    Field('file', db.file)
)

db.file_links.page.requires = IS_NULL_OR(IS_IN_DB(db, 'page.id', 'page.title'))
db.file_links.file.requires = IS_NULL_OR(IS_IN_DB(db, 'file.id', 'file.title'))

###########################################################

# QUERIES
###########################################################
qry_publish = (db.page.status == 'publish')
qry_blog = (db.page.type == 'post') & qry_publish
qry_page = (db.page.type == 'page') & qry_publish
###########################################################

# FUNCTIONS
###########################################################
def get_categories(page):
    return filter(lambda a: a != '', page.categories.split('|'))

def get_permalink(page):
    return URL(r=request, c=WEBLOG, f='archive', args=[page.posted_on.year, page.posted_on.month, page.posted_on.day, page.slug, page.id])

def get_page(record_id):
    return db(db.page.id == record_id).select().first()

def file_permalink(file):
    return URL(r=request, c='default', f='download', args=[file.id])

def file_download_url(file):
    return URL(r=request, c='default', f='raw_download', args=[file.id, file.uploaded_data])
###########################################################
