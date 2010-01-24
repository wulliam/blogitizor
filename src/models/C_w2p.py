# Mail
###########################################################
mail=Mail()
mail.settings.server = configure.read('blogitizor', 'mail_server')
mail.settings.sender = configure.read('blogitizor', 'mail_sender')
mail.settings.login = configure.read('blogitizor', 'mail_login')
###########################################################


# Auth
###########################################################
auth=Auth(globals(), db)
auth.settings.expiration = 90 * 60
auth.settings.hmac_key = 'sha512:cc6d9b105ff915ce5d923d678b0f915d4a8cd16912117819aa0b0af7¬2004a334b384548d57a1fc86f03f1fa06e36d9fed0ddee6ef7312368¬bac13d437a2deacd '

auth_table = db.define_table('auth_user',
    Field('first_name', length=128, default=''),
    Field('last_name', length=128, default=''),
    Field('username', length=128, default=''),
    Field('email', length=128, default=''),
    Field('site', length=128, default=''),
    Field('password', 'password', length=128, readable=False, label='Password'),
    Field('registration_key', length=256, writable=False, readable=False, default=''),
    migrate=migrate_db
)

auth_table.username.label = "__username"
auth_table.password.label = "__password"
auth_table.first_name.label = "__first_name"
auth_table.last_name.label = "__last_name"
auth_table.email.label = "__email"
auth_table.site.label = "__site"
auth_table.registration_key.label = "__registration_key"

auth.settings.table_user = auth_table
auth_table.first_name.requires = IS_NOT_EMPTY()
auth_table.last_name.requires = IS_NOT_EMPTY()
auth_table.email.requires = [
                    IS_LOWER(), IS_EMAIL(), 
                    IS_NOT_IN_DB(db, db.auth_user.email)
]
auth_table.site.requires = IS_NULL_OR(IS_URL())
auth_table.username.requires = [
            IS_LOWER(), IS_NOT_EMPTY(), 
            IS_NOT_IN_DB(db, db.auth_user.username), 
            IS_EXPR('str(value).lower() != "admin"')
]
auth_table.password.requires = CRYPT()

auth.define_tables(migrate=migrate_db)
#auth.settings.actions_disabled.append('register')
#auth.settings.actions_disabled.append('verify_email')
#auth.settings.actions_disabled.append('retrieve_username')
#auth.settings.actions_disabled.append('retrieve_password')

auth.settings.captcha = Recaptcha(request, 
            configure.read('blogitizor', 'recaptcha_public'),
            configure.read('blogitizor', 'recaptcha_private'))
auth.settings.mailer = mail
auth.settings.registration_requires_verification = True
auth.settings.registration_requires_approval = True

auth.settings.controller = 'admin'

auth.settings.login_url = URL(r=request, c='admin/user', f='login')
auth.settings.logged_url = URL(r=request, c='admin/user', f='profile')
auth.settings.login_next = URL(r=request, c='admin', f='index')
auth.settings.logout_next = URL(r=request, c='admin', f='index')
auth.settings.register_next = URL(r=request, c='admin', f='index')
auth.settings.verify_email_next = URL(r=request, c='admin', f='index')
auth.settings.profile_next = URL(r=request, c='admin', f='index')
auth.settings.retrieve_username_next = URL(r=request, c='admin', f='index')
auth.settings.retrieve_password_next = URL(r=request, c='admin', f='index')
auth.settings.change_password_next = URL(r=request, c='admin', f='index')

auth.messages.email_sent = "Please check your email to verify your account"
auth.messages.email_verified = "Your account has been verified, you may log in now"
auth.messages.logged_in = "Welcome Back"
auth.messages.verify_email = """
    Thank you for joining Blogitizer.
    Click on the following link to verify your email.
    
    http://%(host)s/%(app)s/%(controller)s/user/verify_email/%(key)s
""" % {'host': request.env.http_host, 
       'app': request.application, 
       'controller': auth.settings.controller,
       'key': '%(key)s'}

###########################################################

# CRUD/SERVICES
###########################################################
crud=Crud(globals(), db)
crud.settings.controller = 'weblog'
service=Service(globals())
###########################################################
