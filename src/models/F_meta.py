# coding: utf8

configure.verify('site-meta', {
    'title': {
        'value': fixtures.get('site-meta', {}).get('title', "Blogitizor"),
        'description': 'Title of the web site',
    },
    'subtitle': {
        'value': fixtures.get('site-meta', {}).get('subtitle', "Blogitizing the world!"),
        'description': 'Site subtitle or slogan',
    },
    'author': {
        'value': fixtures.get('site-meta', {}).get('author', "Authortizor"),
        'description': 'Author of the site content',
    },
    'keywords': {
        'value': fixtures.get('site-meta', {}).get('keywords', "blogitizor, blogs"),
        'description': 'Keywords for the site',
    },
    'description': {
        'value': fixtures.get('site-meta', {}).get('description', "Blogitizor comes from a blog"),
        'description': 'Short description of the site. < 255 characters',
    },
    'copyright': {
        'value': fixtures.get('site-meta', {}).get('copyright', "Blogitizor likes pie license"),
        'description': 'Copyright of the web2py content.'
    }
})

response.title                      = request.function
response.meta.title                 = configure.read('site-meta', 'title')
response.meta.subtitle              = configure.read('site-meta', 'subtitle')
response.meta.author                = configure.read('site-meta', 'author')
response.meta.keywords              = configure.read('site-meta', 'keywords')
response.meta.description           = configure.read('site-meta', 'description')
response.meta.copyright             = configure.read('site-meta', 'copyright')

response.pages = []
response.categories = []
response.accessories = []
