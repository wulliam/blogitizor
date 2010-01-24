# coding: utf8

response.site = XML('Blogiti<span>zor</span>')
response.site_name = 'Blogitizor'
response.title = 'Blogitizor'
response.subtitle = 'A web2py weblog'
response.meta.author = 'Thadeus Burgess <thadeusb@thadeusb.com>'
response.meta.keywords = 'python, web2py'
response.meta.description = 'A place to blog'
response.meta.copyright = 'Copyright &copy;'

response.force_narrow = False
response.display_sidebar = True
response.sidebar_template = 'sidebar.html'
response.web2py_environment = False

response.pages = []
response.categories = []
response.accessories = []

menu.add_menu_item('main_nav',
                    'main.py',
                    URL(request.application, 'default', 'index'),
                    dict(c='default'))
menu.add_menu_item('main_nav',
                    'data.py',
                    URL(request.application, 'weblog', 'index'),
                    dict(c='weblog'))
