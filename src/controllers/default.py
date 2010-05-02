# coding: utf8

response.display_sidebar = False

def index():
    """
    example action using the internationalization operator T and flash
    rendered by views/default/index.html or views/generic.html
    """
    
    latest_posts = db(qry_blog).select(orderby=~db.page.posted_on, limitby=(0, 6))
    
    response.accessories.append(WIKI("""
Hello World
    """))
    
    return dict(latest_posts=latest_posts)

def error():
    """
    This will handle all application errors for thadeusb.com domain.
    
    URLS that will need to be handled from wordpress.
    
    #POST
    >>>/2009/04/15/pygame-font-and-py2exe/
    #ARCHIVES
    >>>/2009/04/
    /$year/$month/$day/$post_slug/
    
    #PROJECT PAGE
    >>>/portfolioprojects/
    >>>/portfolioprojects/space-invaders-java/
    /$page/$subpage/
    /$page/
    """
    if request.vars.requested_uri:
        uri = filter(lambda a: a != '', request.vars.requested_uri.split('/'))
            
        slug = uri[-1].replace('-', '_')
        slug = slug.replace(' ', '_')
        
        pages = db(db.page.slug == slug)(qry_publish).select()
        
        if len(pages) > 0:
            session.flash = "You have been redirected from a 404 error"
            redirect(get_permalink(pages.first()), how=301)
        else:
            v = {'q': slug.replace('_', ' '), 'error': '404'}
            session.flash = "404 - Page not found"
            redirect(URL(r=request, a='', c='search', f='index', vars=v))
    
    return dict(
        message=T('Sorry. There was an internal failure. A ticket has been logged.'),
    )

def user():
    """
    exposes:
    http://..../[app]/default/user/login 
    http://..../[app]/default/user/logout
    http://..../[app]/default/user/register
    http://..../[app]/default/user/profile
    http://..../[app]/default/user/retrieve_password
    http://..../[app]/default/user/change_password
    use @auth.requires_login()
        @auth.requires_membership('group name')
        @auth.requires_permission('read','table name',record_id)
    to decorate functions that need access control
    """
    return dict(form=auth())

def download():
    file_id = int(request.args(0)) or None
    
    file = db(db.file.id == file_id).select().first()
    
    redirect(URL(r=request, f='raw_download', args=[file.id, file.uploaded_data]))
    
def raw_download():
    """
    allows downloading of uploaded files
    http://..../[app]/default/download/[filename]
    """
    return response.download(request,db)


def call():
    """
    exposes services. for example:
    http://..../[app]/default/call/jsonrpc
    decorate with @services.jsonrpc the functions to expose
    supports xml, json, xmlrpc, jsonrpc, amfrpc, rss, csv
    """
    session.forget()
    return service()
