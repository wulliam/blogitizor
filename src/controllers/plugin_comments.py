import re

# Shorten some variables
db_comment = db.plugin_comments_comment
db_link = db.plugin_comments_link
settings = plugin_comments.settings
do_captcha = settings.recaptcha
no_captcha_for_user = settings.no_recaptcha_for_users

# Auto Fill
if settings.auto_fill_users and auth.is_logged_in():
    db_comment.r_name.default = settings.auth_name
    db_comment.r_email.default = settings.auth_email
    db_comment.r_site.default = settings.auth_site
    
    db_comment.r_name.writable = False
    db_comment.r_email.writable = False
    db_comment.r_site.writable = False

def captcha_form(private=True):
    """
    Returns an SQLFORM with a recaptcha field
    """
    return SQLFORM.factory(
                db_comment.r_name,
                db_comment.r_email,
                db_comment.r_site,
                db_comment.content,
                Field('anti_spam', widget=plugin_comments_captcha, default=''),
            )
def regular_form(private=True):
    """
    Returns an SQLFORM of just a comment.
    """
    return SQLFORM(db_comment)   
    
def preview_markdown():
    """
    Returns a preview of the content using web2py WIKI markdown syntax
    """
    if request.vars.no_table_content:
        preview = WIKI(request.vars.no_table_content).xml()
        return preview
    if request.vars.plugin_comments_comment_content:
        preview = WIKI(request.vars.plugin_comments_comment_content).xml()
        return preview
    return ''
    
def feed():
    """
    Base feed of comments. This is considered a "latest_comments" feed.
    """
    table_name = request.args(0) or None
    record_id = request.args(1) or None
    
    if table_name and record_id:
        settings.rss_link_dict['table_name'] = table_name
        settings.rss_link_dict['record_id'] = record_id 
        
        rss = {
            'title': 'Comment Feed',
            'link': settings.rss % settings.rss_link_dict,
            'description': 'Latest comments',
            'items': plugin_comments_feed_items(table_name, record_id)
        }
    else:
        rss = {
            'title': 'Latest Comments Feed',
            'link': URL(r=request, c='default', f='index'),
            'description': 'All Latest comments',
            'items': []
        }
        
        comments = db(db_comment.id > 0).select(orderby=~db_comment.posted_on, limitby=(0, 15))
        
        for row in comments:
            rss['items'].append(dict(
                title=row.r_name or 'Anonymous',
                link = plugin_comments.settings.rss_link % (plugin_comments.settings.rss_link_dict),
                description=XML(row.content, sanitize=True, permitted_tags=[]).xml(),
                created_on=row.posted_on,
            ))
    
    return rss

def comment():
    """
    Gathers a list of comments, and generates a comment form.
    """
    table_name = request.args(0)
    record_id = request.args(1)
    
    settings.rss_link_dict['table_name'] = table_name
    settings.rss_link_dict['record_id'] = record_id
    
    if request.get_vars.content:
        db_comment.content.default = request.get_vars.content
    if request.get_vars.content and request.post_vars.content:
        request.vars.content = request.post_vars.content
        
    if do_captcha:
        if no_captcha_for_user and auth.is_logged_in():
            form = regular_form()
        else:
            form = captcha_form()
    else:
        form = regular_form()
    
    if form.accepts(request.vars, session, keepvalues=False):
        if 'anti_spam' in form.fields:
            c = db_comment.insert(
                r_name = request.vars.r_name,
                r_email = request.vars.r_email,
                r_site = request.vars.r_site,
                content = request.vars.content
            )
        else:
            c = form.vars.id
            
        link = db_link.insert(
            comment = c,
            table_name = table_name,
            record_id = record_id,
        )
    
    rows = plugin_comments_for(table_name, record_id).select(orderby=settings.orderby)

    return dict(form=form, rows=rows, settings=settings)




