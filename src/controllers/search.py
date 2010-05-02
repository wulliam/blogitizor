# coding: utf8

response.title = "Search"
response.display_sidebar = False

display_count = 20

# shortcuts
w = web2py_utils.w
ws = web2py_utils.ws

def index():
    if request.vars.q:
        q = search.stop_words_list.sub('', request.vars.q)
        
        query = (
              db.page.title.lower().like(w(q)) 
            | db.page.content.lower().like(ws(q))
        )
        
        for qs in filter(lambda a: a != '', q.split(' ')):
            query = query | db.page.content.lower().like(w(qs.strip()))
        
        paginate = Pagination(db, query, 
                                    ~db.page.posted_on,
                                   display_count = 25,
                                   cache=(cache.ram, 5),
                                   r=request, res=response)
        
        pages = paginate.get_set()
                
        results = {'pages': pages}
        response.title += ': ' + q
    else:
        query = None
        results = None
        
    return dict(results=results, query=request.vars.q)
