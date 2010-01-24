if not 'db' in globals():
    raise HTTP(500,"plugin _tagging requires 'db' and 'auth'")

db.define_table('plugin_tagging_tag',
    Field('name'),
    Field('count', 'integer', default=0),
)

db.define_table('plugin_tagging_tag_link',
    Field('table_name'),
    Field('record_id', 'integer'),
    Field('tag', db.plugin_tagging_tag),
)

dbtag = db.plugin_tagging_tag
dbtag_link = db.plugin_tagging_tag_link

dbtag.name.requires = [IS_ALPHANUMERIC(), IS_LOWER(), IS_NOT_IN_DB(db, 'plugin_tagging_tag.name')]
dbtag_link.tag.requires = IS_IN_DB(db, 'plugin_tagging_tag.id')

def plugin_tagging_tag(table_name, record_id, tag_name):
    tag = db(dbtag.name == tag_name).select().first()
    
    if tag:
        link = db(dbtag_link.table_name == table_name
              )(dbtag_link.record_id == record_id
              )(dbtag_link.tag == tag.id).select().first()
        if link:
            #do nothing
            return False
        else:
            dbtag_link.insert(tag=tag, table_name=table_name, record_id=record_id)
            tag.update_record(count=tag.count + 1)
            return True
    else:
        error = True
        for validator in dbtag.name.requires:
            (value, error) = validator(tag_name)
            if error:
                raise ValueError("Invalid %s :: %s" % (value, error))
        
        id_tag = dbtag.insert(name=tag_name, count=1)
        dbtag_link.insert(tag=id_tag, table_name=table_name, record_id=record_id)
        return True

def plugin_tagging_remove_tag(table_name, record_id, tag_name):
    tag = db(dbtag.name == tag_name).select().first()
    
    if tag:
        link = db(dbtag_link.table_name == table_name
              )(dbtag_link.record_id == record_id
              )(dbtag_link.tag == tag.id).select().first()
        if link:
            del dbtag_link[link.id]
            if tag.count - 1 <= 0:
                del dbtag[tag.id]
            else:
                tag.update_record(count=tag.count - 1)
            return True
        else:
            return False
    else:
        return False
        
def plugin_tagging_get_links_id(tag_id):
    links = db(dbtag_link.tag == tag_id).select()
    return links

def plugin_tagging_get_links(tag_name):
    tag = db(dbtag.name == tag_name).select().first()
    
    links = db(dbtag_link.tag == tag.id).select()
    
    return links

def plugin_tagging_get_tags(table_name, record_id):
    return db(dbtag_link.table_name == table_name
            )(dbtag_link.record_id == record_id).select()
