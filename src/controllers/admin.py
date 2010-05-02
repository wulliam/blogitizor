response.menu = []

def expose_to_menu(title, **kw):
    def decorate(f):
        response.menu.insert(kw.get('index', len(response.menu)), 
            [title, False, URL(r=request, c='admin', f=f.__name__), f.__name__, kw.get('float', False)]
        )
        f = expose_to_active(f.__name__)(f)
        return f
    return decorate

def expose_to_active(f_name, **kw):
    def decorate(f):
        for i in range(len(response.menu)):
            if response.menu[i][3] == f_name and \
               request.function == f.__name__:
                response.menu[i][1] = True
        return f
    return decorate


#    def expose_to_menu(title, **kw):
#    def decorate(f):
#        response.menu.insert(kw.get('index', len(response.menu)), 
#            [title, False, URL(r=request, c='admin', f=kw.get('dispatch', '') + f.__name__), f.__name__, kw.get('float', False)]
#        )
#        f = expose_to_active(f.__name__)(f)
#        return f
#    return decorate

#def expose_to_active(f_name, **kw):
#    def decorate(f):
#        for i in range(len(response.menu)):
#            if response.menu[i][3] == f_name:
#                if request.function == f.__name__:
#                    response.menu[i][1] = True
#                elif request.function == 'dispatch' and request.args(0) == f_name:
#                    response.menu[i][1] = True
#        return f
#    return decorate

#for k,v in globals().items():
#    if k.startswith('admin_'):
#        if callable(v):
#            v()

#for name, func in admin.functions.items():
#    expose_to_menu(name.capitalize(), dispatch='dispatch/')(func)

#@auth.requires_login()
#def dispatch():
#    name = request.args(0) or redirect(URL(r=request, f='index'))

#    return admin.functions[name]()

#class list_edit_delete():
#    def __init__(self, name):
#        self.name = name
#        self._llist_data = None
#        self._ledit_data = None
#        self._ldelete_data = None

#    def act(self):
#        if request.args(0) == "edit":
#            if not self._ledit_data:
#                session.flash = "Editing Disabled"
#                redirect(URL(r=request, args='list'))
#            return self._ledit()
#        elif request.args(0) == "delete":
#            if not self._ledit_data or not self._ldelete_data:
#                session.flash = "Deleting Disabled"
#                redirect(URL(r=request, args='list'))
#            return self._ldelete()
#        else:
#            return self._llist()

#    def llist(self, title,
#                query,
#                orderby,
#                pcache,
#                headers,
#                rows,
#                delete_label="(delete)"):
#        self._llist_data = Storage(
#            title=title, query=query, orderby=orderby,
#            pcache=pcache,headers=headers,rows=rows,
#            delete_label=delete_label,
#        )

#    def _llist(self):
#        """
#        Keyword arguments:

#        headers -- name of headers (list)
#        rows -- lambda to generate row item (list)
#        """
#        response.view = 'admin/list.html'

#        paginate = utils.Pagination(db, self._llist_data.query,
#                                        self._llist_data.orderby,
#                                        display_count=35,
#                                        cache=self._llist_data.pcache,
#                                        r=request, res=response)

#        data = paginate.get_set()

#        return dict(headers     =self._llist_data.headers,
#                    rows        =self._llist_data.rows,
#                    data        =data,
#                    delete_label=self._llist_data.delete_label,
#                    ttitle      =self._llist_data.title,
#                    ledname     =self.name) #FIXME: ttitle because title exists (see namespace issues!)

#    def ledit(self, table, onvalidation=None,
#                upload=URL(r=request, f='download', args=request.args[:1]),):
#        self._ledit_data = Storage(
#            table=table, upload=upload, onvalidation=onvalidation,
#        )

#    def _ledit(self):
#        response.view = 'admin/edit.html'

#        record_id = request.args(1) or None

#        if record_id:
#            record_id = int(record_id)
#            record = db(self._ledit_data.table.id == record_id).select().first()
#        else:
#            record = None

#        form = SQLFORM(self._ledit_data.table, record,
#                       linkto=URL(r=request, args=['list']),
#                       upload=self._ledit_data.upload)

#        if form.accepts(request.vars, session, onvalidation=self._ledit_data.onvalidation):
#            session.flash = "Record has been updated"
#            redirect(URL(r=request, args=['list']))
#        elif form.errors:
#            response.flash = "There were errors processing the request"

#        return dict(form=form, record=record, ledname=self.name)

#    def ldelete(self, description):
#        self._ldelete_data = Storage(description=description)

#    def _ldelete(self):
#        record_id = int(request.args(1)) or redirect(URL(r=request, args='list'))
#        record = db(self._ledit_data.table.id == record_id).select().first()

#        response.view = 'admin/confirmbox.html'

#        def yes():
#            record.delete_record()
#            session.flash = "Record successfully deleted"
#            redirect(URL(r=request, args='list'))
#        def no():
#            session.flash = "The record was not deleted"
#            redirect(URL(r=request, args='list'))

#        confirm = utils.CONFIRM_BOX(request, session,
#            content = DIV(P("Are you sure you want to delete the following record?"),
#                        self._ldelete_data.description(record),
#            ),
#            func_yes = yes, func_no = no,
#        )

#        return dict(confirm_box = confirm)

#@auth.requires_login()
#@expose_to_menu('Configure', index=0, float=True)
#def configure():
#    l = list_edit_delete("Configuration")
#    l.llist(
#        "List Configuration",
#        db.settings.id > 0,
#        db.settings.kkey|db.settings.name,
#        (cache.ram, 5),
#        ['Key', 'Name', ('Value',), 'Description',],
#        [
#            lambda d: A(d.kkey, _href=URL(r=request, args=['edit', d.id])),
#            lambda d: d.name,
#            (lambda d: d.value,),
#            lambda d: d.description,
#        ],
#    )
#    l.ledit(db.settings)
#    l.ldelete(lambda d: DIV(
#                            P(d.kkey, ":", d.name),
#                            P("=>", d.value),
#                            ))

#    return l.act()

#########################################
###    Admin, and web2py stuff.
############
def user(): return dict(form=auth())

@auth.requires_login()
def useradmin(): return dict()

@auth.requires_login()
def download(): return response.download(request,db)

@auth.requires_login()
def call():
    session.forget()
    return service()
    
@auth.requires_login()
@expose_to_active('imex')
def export():
    from gluon.contenttype import contenttype
    response.headers['Content-Type'] = contenttype('.csv')
    response.headers['Content-disposition'] = 'attachment; filename=%s_%s_%s_%s%s_blogitizor.csv' % (
        request.now.year, request.now.month, request.now.day,
        request.now.hour, request.now.minute
    )
    import csv, cStringIO
    s = cStringIO.StringIO()
    db.export_to_csv_file(s, delimiter=',', quotechar='"', quoting=csv.QUOTE_NONNUMERIC)
    return s.getvalue()

@auth.requires_login()
def purgeall():
    response.view = 'admin/confirmbox.html'
    def yes():
        do_purge()
        session.flash = "Data Purged"
        redirect(URL(r=request, f='imex'))
    def no():
        session.flash = "Purge Cancelled"
        redirect(URL(r=request, f='imex'))
        
    confirm = web2py_utils.CONFIRM_BOX(request, session,
                                title="Delete All Records",
                                label="Are you sure you want to delete ALL records? This will also purge all USER accounts.",
                                content="ALL database records will be deleted",
                                func_yes=yes, func_no=no)
    
    return dict(confirm_box=confirm)

@auth.requires_login()
@expose_to_menu('Import?Export')
def imex():
    form = FORM(
        #P(TAG.BUTTON("Migrate", _type="submit", _name="yes", _value="yes")),
        #P(TAG.BUTTON("PurgeAll", _type="submit", _name="ram", _value="ram")),
        P(LABEL("File: "), INPUT(_type="file", _name="data")),
        P(
          TAG.BUTTON("Blogitizor Import", _type="submit", _name="imp", _value="imp"),
          TAG.BUTTON("Wordpress Import", _type="submit", _name="impword", _value="impword")
        ),
        P(TAG.BUTTON("Export", _type="submit", _name="exp", _value="exp")),
        P(TAG.BUTTON("purge", _type="submit", _name="purge", _value="purge")),
    )
    
    if form.accepts(request.vars, session):
        if request.vars.imp:
            db.import_from_csv_file(form.vars.data.file)
            response.flash = "Blogitizor Data Imported"
        elif request.vars.impword:
            #f = open('/tmp/import_%s' % request.now, 'w')
            #f#.write(request.vars.data.file.read())
            #f.close
            do_migrate(request.vars.data.file)#'/tmp/import_%s' % request.now)
            response.flash = "Wordpress Data Imported"
        elif request.vars.exp:
            redirect(URL(r=request, f='export'))
        elif request.vars.purge:
            redirect(URL(r=request, f='purgeall'))
    
    return dict(form=form)

@auth.requires_login()
@expose_to_menu('Configure', float=True)
def configure():
    redirect(URL(r=request, f='index'))
    
#-----------------------------------------------------------------------
#########################################
###    AJAX FUNCTIONS
############
@auth.requires_login()
def add_category():
    form = SQLFORM.factory(
        Field('name', requires=IS_NOT_EMPTY()),
        Field('parent', requires=IS_NULL_OR(dbcategory.requires(False)), widget=dbcategory.select_widget())
        ,_action=URL(r=request, f=request.function+'.json')
    )
    
    if form.accepts(request.vars, session):
        try:
            parent_id = int(request.vars.parent)
        except:
            parent_id = None
        node_id = dbcategory.add_node(request.vars.name.capitalize(), parent_id)
        node_name = request.vars.name
        return dict(node_id=node_id, node_name=node_name)
    else:
        return dict(form=form)
    
#########################################
###    ADMIN FUNCTIONS
############
@auth.requires_login()
@expose_to_menu('FillCache')
def fill():
    from random import randrange
    
    def generator():
        massive_list = []
        
        for i in range(990000):
            massive_list.append(randrange(0, 50000))
            
        return massive_list
    
    ml = cache.disk('massive_list', generator, 1500)
    
    return dict(message="massive")

@auth.requires_login()
@expose_to_menu('Cache', index=0)
def ccache():
    form = FORM(
        P(TAG.BUTTON("Clear CACHE?", _type="submit", _name="yes", _value="yes")),
        P(TAG.BUTTON("Clear RAM", _type="submit", _name="ram", _value="ram")),
        P(TAG.BUTTON("Clear DISK", _type="submit", _name="disk", _value="disk")),
    )
    
    if form.accepts(request.vars, session):
        clear_ram = False
        clear_disk = False
        session.flash = ""
        if request.vars.yes:
            clear_ram = clear_disk = True
        if request.vars.ram:
            clear_ram = True
        if request.vars.disk:
            clear_disk = True
            
        if clear_ram:
            cache.ram.clear()
            session.flash += "Ram Cleared "
        if clear_disk:
            cache.disk.clear()
            session.flash += "Disk Cleared"
            
        redirect(URL(r=request))
    
    from guppy import hpy; hp=hpy()
    import shelve, os, copy, time, math
    from gluon import portalocker
    
    ram = {
        'bytes': 0,
        'objects': 0,
        'hits': 0,
        'misses': 0,
        'ratio': 0,
        'oldest': time.time()
    }
    disk = copy.copy(ram)
    total = copy.copy(ram)
    
    for key, value in cache.ram.storage.items():
        if isinstance(value, dict):
            ram['hits'] = value['hit_total'] - value['misses']
            ram['misses'] = value['misses']
            try:
                ram['ratio'] = ram['hits'] * 100 / value['hit_total']
            except:
                ram['ratio'] = 0
        else:
            ram['bytes'] += hp.iso(value[1]).size
            ram['objects'] += hp.iso(value[1]).count
            if value[0] < ram['oldest']:
                ram['oldest'] = value[0]
    
    locker = open(os.path.join(request.folder,
                                        'cache/cache.lock'), 'a')
    portalocker.lock(locker, portalocker.LOCK_EX)
    disk_storage = shelve.open(
        os.path.join(request.folder,
                'cache/cache.shelve'))
    
    for key, value in disk_storage.items():
        if isinstance(value, dict):
            disk['hits'] = value['hit_total'] - value['misses']
            disk['misses'] = value['misses']
            try:
                disk['ratio'] = disk['hits'] * 100 / value['hit_total']
            except:
                disk['ratio'] = 0
        else:
            disk['bytes'] += hp.iso(value[1]).size
            disk['objects'] += hp.iso(value[1]).count
            if value[0] < disk['oldest']:
                disk['oldest'] = value[0]
        
    portalocker.unlock(locker)
    locker.close()
    disk_storage.close()        
    
    total['bytes'] = ram['bytes'] + disk['bytes']
    total['objects'] = ram['objects'] + disk['objects']
    total['hits'] = ram['hits'] + disk['hits']
    total['misses'] = ram['misses'] + disk['misses']
    total['ratio'] = (ram['ratio'] + disk['ratio']) / 2
    if disk['oldest'] < ram['oldest']:
        total['oldest'] = disk['oldest']
    else:
        total['oldest'] = ram['oldest']
    
    def GetInHMS(seconds):
        hours = math.floor(seconds / 3600)
        seconds -= hours * 3600
        minutes = math.floor(seconds / 60)
        seconds -= minutes * 60
        seconds = math.floor(seconds)
        
        return (hours, minutes, seconds)

    ram['oldest'] = GetInHMS(time.time() - ram['oldest'])
    disk['oldest'] = GetInHMS(time.time() - disk['oldest'])
    total['oldest'] = GetInHMS(time.time() - total['oldest'])
    
    return dict(form=form, total=total,
                ram=ram, disk=disk)

@auth.requires_login()
@expose_to_menu('Main', index=0)
def index():
    latest_comments = db(db.plugin_comments_link.id > 0).select(
        limitby=(0,3), orderby=~db.plugin_comments_link.linked_on)
    
    return dict(latest_comments = latest_comments)

@auth.requires_login()
@expose_to_menu('Pages', index=1)
def list_pages():    
    query = db.page.id > 0
    orderby = ~db.page.posted_on
    pcache = (cache.ram, 5)
    
    paginate = Pagination(db, query, orderby,
                display_count=15,
                cache=pcache, r=request, res=response)
    
    pages = paginate.get_set()  
    
    return dict(pages=pages)
    
@auth.requires_login()
@expose_to_active('list_pages')
def create():
    response.display_sidebar = False
    response.force_narrow = True

    area = request.args(0) or 'post'
    page_slug = request.args(1) or None
    
    file_links = None
    
    #manager.include(URL(r=request, c='static', f='js/ckeditor/ckeditor.js'))
    
    markdown = Storage()
    markdown.permitted_tags = ['b', 'blockquote', 'br/', 'i', 'li', 'ol', 'ul', 'p', 'cite', 'code', 'pre']
    markdown.wmd_loc = URL(r=request, c='static', f='js/wmd/wmd.js')
    markdown.wmd_btn = "heading bold italic | link blockquote code image | ol ul hr"
    markdown.wmd_prv = URL(r=request, c='plugin_comments', f='preview_markdown')    
    
    db.page.type.default = 'post'
    response.title = "Add Post"
    
    if area == "page":
        db.page.type.default = 'page'
        response.title = "Add Page"
    
    elif area == "project":
        db.page.type.default = 'project'
        response.title = "Add Project"
        
    if page_slug:
        page = db(db.page.slug == page_slug).select().first()
    
        record_id = page.id
        response.title = 'Editing %s' % page.title
        
        if not request.vars:
            db.page.title.default = page.title
            db.page.slug.default = page.slug
            db.page.categories.default = page.categories
            db.page.content.default = page.content
            db.page.status.default = page.status
            
        rows_tags = plugin_tagging_get_tags('page', page.id)
        dtags = ''
        for row in rows_tags:
            dtags += row.tag.name + ', '
            
        file_links = db(db.file_links.page == page.id).select()
    else:
        dtags = ''
        record_id = None
        file_links = db(db.file_links.page == -9999).select()
        
    fields = [
        db.page.title,
        db.page.slug,
        db.page.categories, 
        db.page.content,
        db.page.status,
        db.page.posted_on,
        Field('tags', 'text', comment='Seperate tags with a comma', default=dtags),
    ]
        
    form = SQLFORM.factory(
            *fields,
            _name = 'form_page_create',
            record_id = record_id,
            _action="#"
    )
        
    if form.accepts(request.vars, formname='form_page_create', keepvalues=True):
        if page_slug:
            page.update_record(
                title=form.vars.title,
                slug=form.vars.slug,
                categories=form.vars.categories,
                content=form.vars.content,
                status=form.vars.status,
                posted_on=form.vars.posted_on
            )
            tags = filter(lambda a: a != '', form.vars.tags.split(','))
            tags[:] = (tag.strip().lower() for tag in tags)
                
            # Remove Tags...
            for row in rows_tags:
                if row.tag.name not in tags:
                    plugin_tagging_remove_tag('page', page.id, row.tag.name)
                
            # Add Tags...
            for tag in tags:
                if tag not in dtags:
                    plugin_tagging_tag('page', page.id, tag.replace(' ', '_'))
                        
            session.flash = 'Page %s updated' % page.title
            redirect(URL(r=request, f='list_pages'))
        else:
            new_page = db.page.insert(
                title=form.vars.title,
                slug=form.vars.slug,
                categories=form.vars.categories,
                content=form.vars.content,
                status=form.vars.status,
                posted_on=form.vars.posted_on
            )
            tags = filter(lambda a: a != '', form.vars.tags.split(','))
            tags[:] = (tag.strip().lower() for tag in tags)
            
            for tag in tags:
                plugin_tagging_tag('page', new_page.id, tag.replace(' ', '_'))
                
            db(db.file_links.page == -9999).update(page=new_page.id)
                
            session.flash = 'Page %s created' % new_page.title
            redirect(URL(r=request, f='list_pages'))
    elif form.errors:
        response.flash = "There were errors"
    
    return dict(form=form, area=area, markdown=markdown, file_links = file_links)

@auth.requires_login()
def uploaded_files():
    id_page = request.args(0) or -9999
    
    links = db(db.file_links.page == int(id_page))(db.file.id == db.file_links.file).select(db.file.ALL, orderby=~db.file.created_on)
    
    return dict(links=links)
    
@auth.requires_login()
def link_file():
    id_page = request.args(0) or -9999
    
    db.file_links.page.default = int(id_page)
    form = SQLFORM(db.file_links, fields=['file'])
    
    if form.accepts(request.vars, session):
        pass
    
    return dict(form=form)

@auth.requires_login()
def upload_file_iframe():
    id_page = request.args(0) or None
    url = ""
    filename = ""
    
    form = SQLFORM(db.file, showid=False, fields=['title', 'type', 'uploaded_data'],
        _action=URL(r=request, f=request.function, args=request.args))
    
    if form.accepts(request.vars, session):
        f = db(db.file.title == request.vars.title).select(orderby=~db.file.created_on).first()
        url = URL(r=request, c='default', f='download', args=f.uploaded_data)
        filename = request.vars.uploaded_data.filename
        
        try:
            id_page = int(id_page)
        except:
            id_page = -9999
                
        db.file_links.insert(page=id_page, file=form.vars.id)   
        
    elif form.errors:
        url = "ERROR"
        filename = form.errors
        
            
    return dict(form=form)

@auth.requires_login()
@expose_to_menu('Comments', index=2)
def list_comments():
    query = db.plugin_comments_link.id > 0
    orderby = ~db.plugin_comments_link.linked_on
    pcache = (cache.ram, 5)
    
    paginate = Pagination(db, query, orderby,
                display_count=15,
                cache=pcache, r=request, res=response        
        )
    
    latest_comments = paginate.get_set()
    
    return dict(comments = latest_comments)

@auth.requires_login()
@expose_to_active('list_comments')
def edit_comment():
    comment_id = int(request.args(0)) or redirect(URL(r=request, f='list_comments'))
    comment = db(db.plugin_comments_comment.id == comment_id).select().first()
     
    form = SQLFORM(db.plugin_comments_comment, comment)
    
    if form.accepts(request.vars, session):
        session.flash = "Comment updated"
        redirect(URL(r=request, f='list_comments'))
    elif form.errors:
        response.flash = "There were errors"
    
    return dict(form=form, comment=comment)

@auth.requires_login()
@expose_to_active('list_comments')
def delete_comment():
    comment_id = int(request.args(0)) or redirect(URL(r=request, f='list_comments'))
    comment = db(db.plugin_comments_comment.id == comment_id).select().first()
    
    response.view = 'admin/confirmbox.html'
    def yes():
        c_link = db(db.plugin_comments_link.comment == comment_id).delete()
        c = db(db.plugin_comments_comment.id == comment_id).delete()
        
        session.flash = "Comment successfully deleted. %d records were removed" % (c_link + c)
        redirect(URL(r=request, f='list_comments'))
    def no():
        session.flash = "The record was not deleted"
        redirect(URL(r=request, f='list_comments'))
    
    confirm = web2py_utils.CONFIRM_BOX(request, session,
                                content=WIKI(comment.content),
                                func_yes = yes, func_no = no)
    
    return dict(confirm_box = confirm)

@auth.requires_login()
@expose_to_menu('Files', index=3)
def list_files():
    query = db.file.id > 0
    orderby = ~db.file.created_on
    pcache = (cache.ram, 5)
    
    paginate = Pagination(db, query, orderby,
                display_count=35,
                cache=pcache, r=request, res=response        
        )
    
    files = paginate.get_set()
    
    return dict(files = files)

@auth.requires_login()
@expose_to_active('list_files')
def edit_file():
    file_id = request.args(0) or None
    
    if file_id:
        file_id = int(file_id)
        file = db(db.file.id == file_id).select().first()
    else: 
        file = None
    
    form = SQLFORM(db.file, file,
                   linkto=URL(r=request, f='list_files'),
                   upload=URL(r=request, f='download', args=request.args[:1]))
    
    
    if form.accepts(request.vars, session):
        session.flash = "File %s has been updated" % form.vars.title
        redirect(URL(r=request, f='list_files'))
    elif form.errors:
        response.flash = "There were errors processing the request"
    
    return dict(form=form, file=file)

@auth.requires_login()
@expose_to_active('list_files')
def delete_file():
    file_id = int(request.args(0)) or redirect(URL(r=request, f='list_files'))
    file = db(db.file.id == file_id).select().first()
    
    response.view = 'admin/confirmbox.html'
    def yes():
        f_link = db(db.file_link.file == file_id).delete()
        f = db(db.file.id == file_id).delete()
            
        session.flash = "File successfully deleted. %d records were removed" % (c_link + c)
        redirect(URL(r=request, f='list_files'))
    def no():
        session.flash = "The record was not deleted"
        redirect(URL(r=request, f='list_files'))
    
    confirm = web2py_utils.CONFIRM_BOX(request, session,
                                content=DIV(P(A(file.title, _href=URL(r=request, f='download', args=file.uploaded_data))),
                                            P(file.created_on.strftime("%Y-%m-%d %I:%M %p")),
                                            IMG(_width='100%',_src=URL(r=request, f='download', args=file.uploaded_data)) if file.type == "image" else '',
                                            ),
                                func_yes = yes, func_no = no,
    )
    
    return dict(confirm_box=confirm)
