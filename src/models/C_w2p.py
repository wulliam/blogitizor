# Mail
###########################################################
mail=Mail()
mail.settings.server = configure.read('site-settings', 'mail_server')
mail.settings.sender = configure.read('site-settings', 'mail_sender')
mail.settings.login = configure.read('site-settings', 'mail_login')
###########################################################


# Auth
###########################################################
configure.verify('auth', {
    'actions_disabled': {
        'value': '',
        'description': """
            List of auth actions to disable. (separated by a space)

            * register
            * verify_email
            * retrieve_username
            * retrieve_password
        """,
    },
    'recaptcha_login': {
        'value': True,
        'description': 'Use recaptcha to log in?',
    },
    'msg_verify_email': {
        'value': fixtures.get('auth', {}).get('msg_verify_email', '{{=link}}'),
        'description': 'Email sent confirm email and account registration.'
    },
})


auth=Auth(globals(), db)
auth.settings.expiration = 90 * 60
auth.settings.hmac_key = hmac_key

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
auth_table.password.requires = CRYPT(key=auth.settings.hmac_key, digest_alg="SHA512")

auth.define_tables(migrate=migrate_db)

for action in configure.read('auth', 'actions_disabled').split(' '):
    auth.settings.actions_disabled.append(action)

if configure.read('auth', 'recaptcha_login'):
    auth.settings.captcha = Recaptcha(request,
                configure.read('site-settings', 'recaptcha_public'),
                configure.read('site-settings', 'recaptcha_private'))
                
auth.settings.mailer = mail
auth.settings.registration_requires_verification = True
auth.settings.registration_requires_approval = True

auth_patches.set_controller(auth, 'admin')

auth.messages.email_sent        = "Please check your email to verify your account"
auth.messages.email_verified    = "Your account has been verified, you may log in now"
auth.messages.logged_in         = "Welcome Back"

auth.messages.verify_email = configure.read('auth', 'msg_verify_email').replace(
    '{{=link}}',
    "http://%(host)s/%(controller)s/user/verify_email/%(key)s" % {
            'host': request.env.http_host,
            'app': request.application,
            'controller': auth.settings.controller,
            'key': '%(key)s'})

###########################################################

# CRUD/SERVICES
###########################################################
service=Service(globals())
###########################################################
