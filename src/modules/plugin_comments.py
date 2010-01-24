# 
# Copyright (C) 2009 Thadeus Burgess
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>

__author__ = "Thadeus Burgess <thadeusb@thadeusb.com>"
__copyright__ = "Copyright 2009-2010 Thadeus Burgess. GNU GPL v3."
__title__ = "Commentizor"
__description__ = """
Commenting plugin, trying a rewrite into an Auth like approach instead of
the unorganized approach
"""
__version__ = "2.0"
###########################################################

"""
## Todo List ##
-------
make __getitem__ able to return comments_for()
"""

from gluon.sql import *
from gluon.sqlhtml import *
from gluon.html import *
from gluon.validators import *
from gluon.tools import Recaptcha

class T():
    pass

class CommentPlugin():
    
    def __init__(self, environment, db, tablename="plugin_comment", **kw):
        """
        Define a comment framework
        
        Keyword arguments:
        recaptcha -- Enable recaptcha to post comments
        no_recaptcha_for_users -- Should users that are logged into auth get captcha?
        auto_fill_users -- If a user is logged in, should it prefill their name/email/website information?
        
        markdown -- format ('text', 'wiki', or 'xml')
        markdown_permitted_tags -- (xml format only)
        markdown_wmd_loc -- WMD, javascript markdown WYSIWYM textarea editor (wiki only), path to js file.
        markdown_wmd_btn -- WMD Buttons
        markdown_wmd_prv -- Location to WIKI preview (ajax based)
        markdown_wmd_ajax -- If false, will use wmd builtin preview functionality ## NOT IMPLEMENTED ##
        """
        self._db = db
        self._tablename = tablename
        self._environment = Storage(environment)
        self._request = self._environment.request
        self._session = self._environment.session
        self._auth = self._environment.auth
        self._response = self._environment.reponse
        T = self._environment.T
        self.settings = Storage()
        self.messages = Storage()
        
        def s(name, default):
            """
            set setting
            
            Keyword arguments:
            name -- setting variable name
            default -- default value for variable
            """
            self.settings[name] = kw.get(name, default)
            
# SETTINGS
###########################################################
        s('recaptcha', True)
        s('no_recaptcha_for_users', True)
        s('auto_fill_users', True)
        
        if self.settings.auto_fill_users and self._auth.is_logged_in():
            s('auth_name', "%(first_name)s %(last_name)s" % self._auth.user)
            s('auth_email', "%(email)s" % self._auth.user)
            s('auth_site', "%(site)s" % self._auth.user)
            
# MARKDOWN SETTINGS
###########################################################
# Formats available
# 'text' - text/plain
# 'wiki' - markdown
# 'xml' - permitted tags
        
        s('markdown', 'wiki')
        s('markdown_permitted_tags', 
          ['b', 'blockquote', 'br/', 'i', 'li', 
           'ol', 'ul', 'p', 'cite', 'code', 'pre']
        )
        s('markdown_wmd_loc', 
          URL(r=self._request, c='static', f='js/wmd/wmd.js')
        )
        s('markdown_wmd_btn',
          'heading bold italic | link blockquote code image | ol ul hr'
        )
        s('markdown_wmd_prv',
          URL(r=self._request, c='plugin_comments', f='expose/preview_markdown')
        )
        s('markdown_wmd_ajax', True)
        
        if self.settings.recaptcha:
            s('captcha', 
              lambda f,v: Recaptcha(self._request, 
                        kw.get('recaptcha_public'), 
                        kw.get('recaptcha_private'))
            )
# MESSAGES
###########################################################

        if self.settings.markdown == 'wiki':
            from gluon.contrib.markdown import WIKI
            self.messages.content_comment = """
<b><a href="http://daringfireball.net/projects/markdown/syntax">Markdown</a> syntax is supported for comments.</b>
            """
        elif self.settings.markdown == 'xml':
            self.messages.content_comment = """
<b>HTML formatting is supported. Permitted tags: ['b','blockquote','br/','i','li','ol','ul','p','cite','code','pre']</b>
            """
        else:
            self.messages.content_comment = """
<b>Comments are in text/plain format.</b>
            """
            
        self.messages.content_comment = kw.get('content_comment', T(self.messages.content_comment))
            
        self.messages.name_label = kw.get('name_label', T("Name"))
        self.messages.email_label = kw.get('email_label', T("Email Address (required)"))
        self.messages.email_comment = kw.get('email_comment', T("Will not be published"))
        self.messages.site_label = kw.get('site_label', T("Website"))
        self.messages.content_label = kw.get('content_label', T("Your Message"))
        
    def __getitem__(self, key):
        if isinstance(key, int):
            return self._db[self._tablename][key]
        else:
            raise TypeError("Key must be of type int")
       

# DATABASE DEFINITIONS
###########################################################

    def define_tables(self, fk="no_table", migrate_db=True):
        if isinstance(fk, Table):
            fk_name = fk._tablename
            fk_field = Field('record', fk)
        else:
            fk_name = fk
            fk_field = Field('record')
            
        self.tablename_comment = self._tablename + 'comment'
        self.tablename_comment_link = self._tablename + 'link_' + fk_name
        
        self.dbcomment = self._db.define_table(
            self.tablename_comment,
            Field('name'),
            Field('email', requires=IS_EMAIL()),
            Field('site', requires=IS_NULL_OR(IS_URL())),
            Field('content', 'text', requires=IS_NOT_EMPTY()),
            Field('posted_on', 'datetime', default=self._request.now,
                  writable=False, readable=False)
        )
        
        self.dbcomment_link = self._db.define_table(
            self.tablename_comment_link,
            Field('comment', self.dbcomment),
            fk_field,
            Field('linked_on', 'datetime', default=self._request.now,
                  writable=False, readable=False)
        )
        
        self.dbcomment_link.comment.requires = IS_IN_DB(self._db, name_comment + '.id')
        
        self.settings.orderby = self.dbcomment_link.linked_on

# LABELS AND DEFAULTS
###########################################################        

        self.dbcomment.name.label = self.messages.name_label
        self.dbcomment.email.label = self.messages.email_label
        self.dbcomment.email.comment = self.messages.email_comment
        self.dbcomment.site.label = self.messages.site_label
        self.dbcomment.content.label = self.messages.content_label
        self.dbcomment.content.comment = XML(self.messages.content_comment)
                
        if self.settings.auto_fill_users and self._auth.is_logged_in():
            self.dbcomment.name.default = self.settings.auth_name
            self.dbcomment.email.default = self.settings.auth_email
            self.dbcomment.site.default = self.settings.auth_site
            
            self.dbcomment.name.writable = False
            self.dbcomment.email.writable = False
            self.dbcomment.site.writable = False

# QUERIES AND FUNCTIONS
###########################################################        

    def comments_for(self, record_id):
        """
        Get comments for ``record_id``
        Returns a web2py query object, you will need to perform your own
        .select() to get the results.
        
        Keyword arguments:
        record_id -- ID of the record in foriegn key table.
        
        Returns:
        query object.
        """
        return self._db(self.dbcomment_link.record == record_id)
    
    def load(self, record_id):
        """
        Returns web2py's LoadFactory for ``record_id``
        Calls the plugin's comment action.
        """
        return LOAD('plugin_comments', 'expose/comment', args=record_id)
    
    @classmethod
    def gravatar_url(email="", default="", size=40):
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
    
# VIEWS
###########################################################        

    def __call__(self):
        """
        View dispatcher
        """
        req = self._request
        if req.args(0) == 'preview_markdown':
            if req.vars.no_table_content:
                return self.preview_markdown(req.vars.no_table_content)
            if req.vars[self.tablename_comment]:
                return self.preview_markdown(req.vars[self.tablename_comment])
        elif req.args(0) == 'comment':
            return self.comment(req.args(1), req)
    
    def preview_markdown(self, content):
        """
        Returns a preview of the content using web2py WIKI markdown syntax
        """
        return WIKI(content).xml()
    
    def comment(self, record_id, request):
        """
        Gathers a list of comments, and generates a comment form.
        """
        def captcha_form(private=True):
            """
            Returns an SQLFORM with a recaptcha field
            """
            return SQLFORM.factory(
                        self.dbcomment.name,
                        self.dbcomment.email,
                        self.dbcomment.site,
                        self.dbcomment.content,
                        Field('anti_spam', widget=self.settings.captcha, default=''),
                    )
        def regular_form(private=True):
            """
            Returns an SQLFORM of just a comment.
            """
            return SQLFORM(self.dbcomment)   
        
        if request.get_vars.content:
            self.dbcomment.content.default = request.get_vars.content
        if request.get_vars.content and request.post_vars.content:
            request.vars.content = request.post_vars.content
            
        if self.settings.recaptcha:
            if self.settings.no_captcha_for_user and self._auth.is_logged_in():
                form = regular_form()
            else:
                form = captcha_form()
        else:
            form = regular_form()
        
        if form.accepts(request.vars, self._session, keepvalues=False):
            if 'anti_spam' in form.fields:
                c = self.dbcomment.insert(
                    name = request.vars.name,
                    email = request.vars.email,
                    site = request.vars.site,
                    content = request.vars.content
                )
            else:
                c = form.vars.id
                
            link = self.dbcomment_link.insert(
                comment = c,
                record = record_id
            )
        
        rows = self.comments_for(record_id).select(orderby=self.settings.orderby)
    
        return dict(form=form, rows=rows, settings=settings)    