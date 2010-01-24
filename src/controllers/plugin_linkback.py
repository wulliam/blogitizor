def call(): return service()

def receive_trackback():
    """
    This function should be exposed with custom so that
    table_name and record_id can be set.
    
    Trackback is a really nasty protocol, and as such, difficult
    to implement. The nice thing about trackback is we can use
    table_name and record_id in the trackback URL and determine
    the record being linked against.... Of course you would then
    need to determine the url of said post so you can verify the linked
    existance of said url
    """
    track = linkback.TrackbackServer()
    
    table_name = request.args(0) or None
    record_id = request.args(1) or None
    
    # Additional checks should be made here.
    if not table_name or record_id:
        status = "Error"
        message = "Trackback target does not exist"
        return dict(status = status, message=message)
        
    # This should be modified
    target_url = URL(r=request, c='default', f='index', args=[table_name, record_id])
    
    db.plugin_linkback_incoming.type.default = 'trackback'
    
    track.verify(request.vars.url, target_url)
    if track.status == linkback.Pingback.PINGBACK_SOURCE_DOES_NOT_LINK:
        return dict(status="Error", message="Souce does not link")
    
    data = track.receive(request.vars)
    
    record_exists = plugin_linkback_incoming_exists(
                             table_name, record_id,
                             data['source_url'])
    
    if record_exists:
        return dict(status="Error", message="Trackback already registered")
    
    
    incoming = db.plugin_linkback_incoming.insert(
        url = data['source_url'],
        target = target_url,
        title = data['title'],
    )
    link = db.plugin_linkback_incoming_link.insert(
        incoming = incoming,
        table_name = table_name,
        record_id = record_id
    )
    
    return dict(status="Success", message="Success")
    
    
@service.xmlrpc
def pingback_ping(source_url, target_url):
    """
    Pingback is nasty in that you have to determine the table_name
    and record_id by looking and parsing the target_url..
    
    This is what ``get_record_identifer`` does.
    """
    ping = linkback.PingbackServer()
    
    data = ping.receive({'source_url': source_url, 
                         'target_url': target_url})
    
    if ping.status == ping.FAILED:
        return ping.message
    
    (table_name, record_id) = plugin_linkback.settings.get_record_identifier(data)
    
    if not table_name or record_id:
        return ping.PINGBACK_TARGET_DOES_NOT_EXIST
    
    record_exists = plugin_linkback_incoming_exists(
                                 table_name, record_id,
                                 source_url)
    
    if record_exists:
        return ping.PINGBACK_ALREADY_REGISTERED
    
    ping.verify(data['source_url'], data['target_url'])
    
    if ping.status == ping.FAILED:
        return ping.message
    
    db.plugin_linkback_incoming.type.default = 'pingback'
    
    incoming = db.plugin_linkback_incoming.insert(
        url = data['source_url'],
        target = data['target_url'],
        title = ping.title,        
    )
    link = db.plugin_linkback_incoming_link.insert(
        incoming = incoming,
        table_name = table_name,
        record_id = record_id
    )
    
    # Everything *should* be ok
    return ping.message
pingback_ping.__name__ = 'pingback.ping'