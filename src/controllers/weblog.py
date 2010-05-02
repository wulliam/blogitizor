# coding: utf8

#########################################
###    GLOBAL VARS
############

response.title = 'Weblog'
response.sidebar_template = 'weblog/sidebar.html'

plugin_comments.settings.rss = 'http://'+request.env.http_host+'/'+request.application+'/weblog/feed.rss/%(record_id)s'
plugin_comments.settings.rss_link = 'http://'+request.env.http_host+'/'+request.application+'/weblog/view/%(slug)s#comment-%(comment_id)s'

display_count = int(configure.read('page', 'display_count'))
rss_display_count = int(configure.read('page', 'rss_display_count'))

## import time
##    t=cache.ram('time',lambda:time.ctime(),time_expire=5)
    
def response_pages(private=True):
    pages = db(qry_page).select(db.page.ALL, 
                                orderby=db.page.posted_on,
                                cache=(cache.disk, 1500))
    items = []
    for page in pages:
        item = [page.title, False, URL(r=request, c='weblog', f='view', args=page.slug)]
        items.append(item)
    return items
response.pages = cache.ram('res_pages', response_pages, time_expire=750)

def response_categories(private=True):
    categories = db().select(dbcategory.table.ALL, cache=(cache.disk, 1500))
    items = []
    for cat in categories:
        count = db(qry_blog)(db.page.categories.like("%|" + str(cat.id) + "|%")).count()
        if count > 0:
            item = [cat.name, count, URL(r=request, c='weblog', f='category', args=cat.name)]
            items.append(item)
    return items
response.categories = cache.ram('res_cats', response_categories, time_expire=750)


#########################################
###    PRIVATE FUNCTIONS
############ 

w = web2py_utils.w

#########################################
###    AJAX FUNCTIONS
############

#########################################
###    PUBLIC FUNCTIONS
############

def trackback():
    table_name = 'page'
    record_id = request.args(0) or None

    value, error = IS_IN_DB(db, 'page.id')(int(record_id))
    
    if error:
        return dict(status = "Error", 
                    message = "Trackback target does not exist")
    
    target_url = URL(r=request, c='weblog', f='trackback', args=[page.id]),
    
    track = linkback.TrackbackServer()
    
    data = track.receive(request.vars)
    
    track.verify(data['source_url'], target_url)
    
    if track.status == linkback.Pingback.PINGBACK_SOURCE_DOES_NOT_LINK:
        return dict(status = "Error",
                    message = "Source does not link")
    
    record_exists = plugin_linkback_incoming_exists(
                             table_name, record_id,
                             data['source_url'])
    
    if record_exists:
        return dict(status="Error",
                    message ="Trackback already registered")
    
    incoming = db.plugin_linkback_incoming.insert(
        url = data['source_url'],
        target = target_url,
        title = data['title'],
    )
    link = db.plugin_linkback_incoming_link.insert(
        incoming = incoming,
        table_name = table_name,
        record_id = record_id
    )
    
    return dict(status="Success",
                message="Success")


def index():
    response.title = "Index"
    
    paginate = Pagination(db, qry_blog, 
                                ~db.page.posted_on,
                                r=request, res=response)
    pages = paginate.get_set()
    
    return dict(pages=pages)

def category():
    response.title = "Categories"
    
    name = request.args(0) or None
    
    
    if name:
            
        name = name.replace('_', ' ')
        
        cat = dbcategory[name].first()
        
        if not cat:
            raise HTTP(404, 'category not found')
                               
        query = db.page.categories.like(w('|'+str(cat.id)+'|'))
        
        paginate = Pagination(db, query & qry_blog, 
                                    ~db.page.posted_on,
                                    r=request, res=response)
        
        pages = paginate.get_set()
        
    else:
        pages = None
        category = None
        cat = Storage(name=None)
    
    return dict(pages=pages, category=cat.name)
    
def tag():
    response.title = "Tags"
    
    query = db.page.id == -1
    
    if request.vars.search_tags:
        names = []
        for name in request.vars.search_tags.split(','):
            names.append(name.strip())
        redirect(URL(r=request, args=names))
        
    names = request.args
    
    for name in names:
        name = name.replace(' ', '_')
        
        tag = db(db.plugin_tagging_tag.name == name).select().first()
        if tag:
            links = plugin_tagging_get_links(tag.name)
            for link in links:
                query = query | (db.page.id == link.record_id)
            
            
    paginate = Pagination(db, query & qry_blog, 
                                ~db.page.posted_on, 
                                r=request, res=response)
    pages = paginate.get_set()
    
    response.related_tags = []
    for page in pages:
        re_row = plugin_tagging_get_tags('page', page.id)
        for re in re_row:
            remeta = (re.tag.name, URL(r=request, f='tag', args=re.tag.name))
            if remeta not in response.related_tags:
                response.related_tags.append(remeta)
                
    response.search_tags = True
                
    return dict(pages=pages)
    
def view():    
    page_slug = request.args(0) or redirect(URL(r=request, f='index'))
    
    page = db(db.page.slug == page_slug).select().first()
    
    if not page:
        raise HTTP(404, "no page")
    
    response.title = page.title
    
    plugin_comments.settings.rss_link_dict['record_id'] = page.slug
    
    tags = plugin_tagging_get_tags('page', page.id)
    
    response.related_entries = []
    
    if len(tags) > 0:
    
        ts = []
        tl = []
        for t in tags:
            ts.append(t.tag.id)
            tl.append(t.id)
    
        links = db(db.plugin_tagging_tag_link.tag.belongs(ts)).select().find(
                lambda row: row.id not in tl
        )
        
        for link in links:
            re = db(db.page.id == link.record_id).select().first()
            remeta = (re.title, URL(r=request, f='view', args=re.slug))
            if remeta not in response.related_entries:
                response.related_entries.append(remeta)
                    
    return dict(page=page)
    
def archive():
    year = request.args(0) or None
    month = request.args(1) or None
    day = request.args(2) or None
    page_slug = request.args(3) or None
    page_id = request.args(4) or None
    
    response.title = "Archive " + " ".join([year or "", month or "", day or ""])+ " "
    
    archive_info = {
        'year': year,
        'month': month,
        'day': day,
        'page_slug': page_slug,
        'page_id': page_id,
    }
    
    query = qry_publish
    try:
        if year:
            query = query & (db.page.posted_on.year() == year)
        if month:
            query = query & (db.page.posted_on.month() == month)
        if day:
            query = query & (db.page.posted_on.day() == day)
        if page_id:
            query = query & (db.page.id == page_id)
    except:
        raise HTTP(404, 'invalid archives')
        
    if year:
        
        paginate = Pagination(db, query, 
                                    ~db.page.posted_on, 
                                    r=request, res=response)
        results = paginate.get_set()
        
        if len(results) == 1:
            page = results.first()
            response.title = page.title
            tags = plugin_tagging_get_tags('page', page.id)
        
            if len(tags) > 0:
                ts = []
                tl = []
                for t in tags:
                    ts.append(t.tag.id)
                    tl.append(t.id)
                                   
                    
                links = db(db.plugin_tagging_tag_link.tag.belongs(ts)).select().find(
                        lambda row: row.id not in tl
                )
                
                response.related_entries = []
                for link in links:
                    re = db(db.page.id == link.record_id).select().first()
                    remeta = (re.title, URL(r=request, f='view', args=re.slug))
                    if remeta not in response.related_entries:
                        response.related_entries.append(remeta)
                    
    else:
        results = []
                
    return dict(results=results, archive=archive_info)
    
#########################################
###    ADMIN FUNCTIONS
############

    
#########################################
###    SERVICES
############

def feed():
    rss = {
        'title': 'ThadeusB Blog Feed',
        'link': 'http://'+request.env.http_host+'/'+request.application+'/weblog/feed.rss/',
        'description': 'Latest blog posts from Thadeus',
        'items': []
    }
    
    page_id = request.args(0) or None
    
    if page_id:
        if page_id == 'category':
            name = request.args(1) or None
            if not name:
                raise HTTP(404, 'no found')
                
            name = name.replace('_', ' ')
        
            cat = dbcategory[name].first()
            
            if not cat:
                raise HTTP(404, 'category not found')
                                   
            query = db.page.categories.like(w('|'+str(cat.id)+'|'))
            
            pages = db(qry_blog)(query).select(orderby=~db.page.posted_on, limitby=(0, rss_display_count))
            
            for row in pages:
                item = dict(
                    title=row.title,
                    link='http://'+request.env.http_host+'/weblog/view/%s' % row.slug,
                    description=str(WIKI(row.content, extras={
                                        'code-color': {'noclasses': True},
                                        'footnotes': None,
                                        'code-friendly': None,
                                    })),
                    created_on=row.posted_on,
                )
                rss['items'].append(item)
            
        else:
            page = db(db.page.slug == page_id).select().first()
            if not page:
                try:
                    page = db(db.page.id == page_id).select().first()
                except:
                    raise HTTP(404, "page not found")
                    
            plugin_comments.settings.rss_link_dict['slug'] = page.slug
            
            rss['title'] = 'ThadeusB Comment Feed'
            rss['link'] = plugin_comments.settings.rss % ({'record_id': page.slug})
            rss['description'] = 'Latest comments on post %s' % page.title
            rss['items'] = plugin_comments_feed_items('page', page.id)
        
    else:
        pages = db(qry_blog).select(orderby=~db.page.posted_on, limitby=(0, rss_display_count))
        
        for row in pages:
            item = dict(
                title=row.title,
                link='http://'+request.env.http_host+'/weblog/view/%s' % row.slug,
                description=str(WIKI(row.content, extras={
                                    'code-color': {'noclasses': True},
                                    'footnotes': None,
                                    'code-friendly': None,
                                })),
                created_on=row.posted_on,
            )
            rss['items'].append(item)
    
    return rss






















