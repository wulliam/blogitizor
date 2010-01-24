db.define_table('plugin_linkback_incoming',    
    Field('type'),
    Field('url'),
    Field('title', length=255),
    Field('site_name', length=255),
    Field('excerpt', 'text', length=500),
    
    Field('target'),
    
    Field('remote_ip', default=request.env.remote_addr),
    Field('receive_date', 'datetime', default=request.now)
)

db.plugin_linkback_incoming.type.requires = IS_IN_SET(('pingback', 'trackback'))
db.plugin_linkback_incoming.url.requires = IS_URL()
db.plugin_linkback_incoming.target.requires = IS_NULL_OR(IS_URL())

db.define_table('plugin_linkback_outgoing',
    Field('type'),
    Field('url'),
    Field('service_callback'),
    
    Field('status'),
    Field('message'),
    Field('attempts', 'integer', default=0),
    
    Field('last_attempted', 'datetime', default=request.now, update=request.now)
)

db.plugin_linkback_outgoing.type.requires = IS_IN_SET(('pingback', 'trackback'))
db.plugin_linkback_outgoing.url.requires = IS_URL()
db.plugin_linkback_outgoing.service_callback.requires = IS_URL()
db.plugin_linkback_outgoing.status.requires = IS_IN_SET(
    linkback.Linkback.STATUS_MESSAGES.keys(),
    linkback.Linkback.STATUS_MESSAGES.values(),
)

db.define_table('plugin_linkback_incoming_link',
    Field('pingback_incoming', db.plugin_linkback_incoming),
    Field('table_name'),
    Field('record_id', 'integer'),
)

db.plugin_linkback_incoming_link.pingback_incoming.requires = IS_IN_DB(db, 'plugin_linkback_incoming.id')

db.define_table('plugin_linkback_outgoing_link',
    Field('pingback_outgoing', db.plugin_linkback_outgoing),
    Field('table_name'),
    Field('record_id', 'integer')
)

db.plugin_linkback_outgoing_link.pingback_outgoing.requires = IS_IN_DB(db, 'plugin_linkback_outgoing.id')

def plugin_linkback_incoming_exists(table_name, record_id, url):
    return db((db.plugin_pingback_incoming_link.table_name == table_name)
         &(db.plugin_pingback_incoming_link.record_id == record_id)
         &(db.plugin_pingback_incoming.url == url)
         &(db.plugin_pingback_incoming.id == db.plugin_pingback_incoming_link.pingback_incoming)
        ).count() > 0