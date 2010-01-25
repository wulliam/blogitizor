import xml
from gluon.html import A, URL, H2, DIV, FORM, LABEL, P, XML, OL, LI, UL
from gluon.cache import Cache
from gluon.tools import Storage
from gluon.sql import Field

class BUTTON(DIV):
    tag = 'button'
    
def CONFIRM_BOX(request, session,
                title="Delete Record",
                label="Are you sure you want to delete this record?", 
                content="", func_yes=lambda v:v, func_no=lambda v:v):
    form = FORM(
        DIV(
            P(LABEL(label), _class="centered"),
            P(BUTTON("Yes", _type="submit", _name="yes", _value="yes"), _class="centered"), 
            P(BUTTON("No", _type="submit", _name="no", _value="no"), _class="centered"),
        )
    )
    
    html = DIV(
        H2(title),
        DIV(
            DIV(
                form,
                P(content),
            _id="padding"),
        _id="user_action"),
    )
    
    if form.accepts(request.vars, session):
        if request.vars.yes == "yes":
            func_yes()
        else:
            func_no()
    elif form.errors:
        response.flash = "There were errors with the form"
        
    return html
    
    
def w(q):
    return "%" + q.lower() + "%"

def ws(q):
    ws = '%'.join(qs.lower() for qs in q.split(' '))
    return w(ws)
 
class Pagination():
    def __init__(self, db, query, 
                 orderby, current=None, 
                 display_count=4, cache=None,
                 r=None, res=None):
        self.db = db
        self.query = query
        self.orderby = orderby
        if not current:
            if not r.vars.p:
                current = 0
            else:
                current = int(r.vars.p)
        elif not isinstance(current, int):
            current = int(current)
        self.current = current
        self.display_count = display_count
        self.r = r
        self.res = res
        if not cache:
            self.cache = (Cache(r).ram, 1500)
        else:
            self.cache = cache
        
    def get_set(self, set_links = True):
        self.set = self.db(self.query).select(
            orderby=self.orderby, limitby=(
                self.current, self.current+self.display_count
                ), cache=self.cache
            )
        self.num_results = len(self.set)
        self.total_results = self.db(self.query).count()
        if set_links:
            self.res.paginate_links = self.generate_links()
            
        return self.set
    
    def generate_links(self):
        self.backward = A('<< previous()', _href=URL(r=self.r, vars={'p': self.current - self.display_count})) if self.current else '<< previous(False)'
        self.forward = A('next() >>', _href=URL(r=self.r, vars={'p': self.current + self.display_count})) if self.total_results > self.current + self.display_count else 'next(False) >>'
        self.location = 'Showing %d to %d out of %d records' % (min(self.current + 1, self.num_results), self.current + self.num_results, self.total_results)
        return (self.backward, self.forward, self.location)

class Configure():
    """
    This class implements a configurable set of options
    for use in anything that needs settings that
    are to be stored in the database.
    """
    def __init__(self, database,
                    auto_define=True,
                    migrate=True,
                    cache=None):
        """
        Initialize configure class.

        Keyword arugments:
        database -- web2py DAL instance
        auto_define -- auto define database tables (default: True)
        migrate -- migrate the database tables (default: True)
        cache -- cache object to use for pulling database settings,
                this is a tuple object consisting of cache object
                and cache timeout. Default No Cache!
                (Cache(r).ram, 1500)
        """
        self.db = database
        self.cache = cache
        if auto_define:
            self.define_tables(migrate=migrate)
            self._get_settings()

    def define_tables(self, migrate=True):
        """
        Defines the database tables needed to function
        """
        self.db.define_table('settings',
            Field('key'),
            Field('name'),
            Field('value', 'text'),
            Field('description', 'text'),
            migrate=migrate
            #Field('created_on', 'datetime'),
           # Field('modified_on', 'datetime'),
        )

        #self.db.settings.created_on.default = request.now
        #self.db.settings.modified_on.update = request.now

       # self.db.settings.created_on.writable = False
       # self.db.settings.created_on.readable = False
       # self.db.settings.modified_on.writable = False
       # self.db.settings.modified_on.readable = False

    def _get_settings(self):
        """
        Retreives the settings from the database and
        stores them in a storage dictionary
        """
        settings = Storage()

        rows = self.db(self.db.settings.id > 0).select(cache=self.cache)

        for row in rows:
            if not settings.has_key(row.key):
                settings[row.key] = Storage()
            settings[row.key][row.name] = row

        self.settings = settings

    def verify(self, key, settings):
        """
        Adds the configuration to memory, and assures that the
        configuration exists in the database (DAL for web2py).

        If there are no database entries, it will create the table,
        and fill in the default values, otherwise it will poll
        the database for the information.

        Keyword arguments:
        key -- unique name for a set of configuration options
                examples include, 'blog', 'cache', 'rss'
        items -- dictionary of configs to store into the database.
                in the format of
                {'key_name': { 'value': default, 'description': 'a desc' }}

                Example:
                    {'display_count': {
                        'value': 4,
                        'description': "Number of posts to display per-page",},}
        """
        for name, info in settings.iteritems():
            row = self.db(
                  (self.db.settings.key == key)
                & (self.db.settings.name == name)
            ).select().first()

            if not row:
                record = self.db.settings.insert(
                 key=key,
                 name=name,
                 value=info.get('value', None),
                 description=info.get('description', None)
                )
                if not self.settings.has_key(key):
                    self.settings[key] = Storage()
                self.settings[key][name] = record

    def read(self, key, name):
        """
        Returns the value of a settings object

        Keyword arguments:
        key -- keyname
        name -- setting name
        """
        return self.settings[key][name].value

    def write(self, key, name, value):
        """
        Writes a setting to the database

        Keyword arguments:
        key -- keyname
        name -- setting name
        value -- value for the setting
        """
        self.settings[key][name].value = value
        self.settings[key][name].update_record()

class MenuManager():
    """
    Manages menu's for blogitizor.

    Example usage

    menu = MenuManager()
    main_menu = MenuItem(
        title, url
        activewhen(
            controller ==
            application ==
            action ==
        )
    """
    TITLE_INDEX = 0
    URL_INDEX = 1
    ACTIVE_INDEX = 2

    def __init__(self, request):
        self.menus = {}
        self.request = request

    def add_menu_item(self, menu, title, url, activewhen=dict(c=None,f=None,a=None)):
        if not self.menus.has_key(menu):
            self.menus[menu] = []
        self.menus[menu].append(
            [title, url, self.iam(activewhen)]
        )

    def render_menu(self, menu, type='ol'):
        if type == 'ol':
            xml == OL()
        else:
            xml = UL()
        for item in self.menus[menu]:
            if item[MenuManager.ACTIVE_INDEX]:
                c = "active"
            else:
                c = None
            xml.append(
                LI(
                    A(item[MenuManager.TITLE_INDEX], _href=item[MenuManager.URL_INDEX])
                , _class=c)
            )
        return xml
    
    def is_active_menu(self, when):
        c = when.get('c', None)
        f = when.get('f', None)
        a = when.get('a', None)
        i = False

        if c:
            if c == self.request.controller:
                i = True
            else:
                i = False

        if f:
            fs = f.split('/')
            onehit = False
            for fps in fs:
                if fps == self.request.function:
                    onehit = True
            i = onehit and i

        if a:
            if a == self.request.args:
                i = True and i
            else:
                i = False

        return i
    iam = is_active_menu
