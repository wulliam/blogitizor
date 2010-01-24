def plugin_linkback_rdf(permalink, title, ping_url):
    return XML(
        response.render('plugin_linkback/rdf.xml',
        dict(
            permalink = permalink,
            title = title,
            ping_url = ping_url,
        ))
    )

