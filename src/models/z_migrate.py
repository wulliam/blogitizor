DOHTML = False

def do_purge():
    db(db.plugin_comments_link.id > 0).delete()
    db(db.plugin_comments_comment.id > 0).delete()
    db(db.plugin_tagging_tag_link.id > 0).delete()
    db(db.plugin_tagging_tag.id > 0).delete()
    db(db.plugin_category.id > 0).delete()
    db(db.file_links.id > 0).delete()
    db(db.file.id > 0).delete()
    db(db.page.id > 0).delete()

def do_migrate(f):
    """
    f -- open readable file-like object
    """
    
    from BeautifulSoup import BeautifulSoup
    w2py = local_import('plugin_wordpress2py')
    h2t = local_import('html2text')
    
    data = w2py.word2py(f)
    
    ids = dict(
        category = {},
        post = {},
        tag = {},
        comment = {},
    )
    
    for c in data['categories']:
        ids['category'][c['slug']] = dbcategory.add_node(c['name'], c['parent'])
        
    ids['category']['uncategorized'] = dbcategory.add_node('uncategorized')
        
    for p in data['posts'][13:]:
        if p['type'] == 'post' or p['type'] == 'page':
            post = dict(
                title = p['title'],
                slug = p['slug'].replace('-', '_'),
                type = p['type'],
                posted_on = p['post_date'],
                status = p['status'],
                author = 1
            )
            if DOHTML:
                content = p['content'].replace('\n', '<br />')
                content = content.replace('\t', '')
            else:
                content = p['content']
                
            #content = content.replace('&gt;', '>')
            #content = content.replace('&lt;', '<')
            
            #content = h2t.html2text(content)
            
            def setcontents(tag, val):
                for c in tag.contents:
                    c.extract()
                tag.insert(0, val)
            
            if DOHTML:
                soup = BeautifulSoup(str(content))
            else:
                soup = BeautifulSoup(content)
    
            for tag in soup.findAll('pre'):
                ts = tag.renderContents()
                ts = ts.replace('<br />', '\n    ')
                setcontents(tag, tag.renderContents().replace('<br />', '\n    '))
                
            content = unicode(soup)
            
            content = WIKI("%s" % soup, safe_mode=False).xml()
            
            content = h2t.html2text(content.decode('utf-8'))
                        
            post['content'] = content
            
            cat_ids = []
            for c in p['categories']:
                cat_ids.append(ids['category'][c])
            post['categories'] = '|' + '|'.join(str(c.id) for c in cat_ids) + '|'
            
            id_page = db.page.insert(**post)
            
            for t in p['tags']:
                plugin_tagging_tag('page', id_page.id, t.replace('-', '_'))
                
            for c in p['comments']:
                if c['approved'] != 'spam':
                    id_comment = db.plugin_comments_comment.insert(
                        r_name = c['author'],
                        r_email = c['author_email'],
                        r_site = c['author_url'],
                        content = c['content'],
                        posted_on = c['date']
                    )
                    
                    id_link = db.plugin_comments_link.insert(
                        comment = id_comment,
                        table_name = 'page',
                        record_id = id_page,
                        linked_on = c['date']
                    )
            

