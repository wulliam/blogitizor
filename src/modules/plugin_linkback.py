"""
This module implements linkback specifications for python.

The current implementations include Pingback and Trackback.

The pingback specification can be located at
http://www.hixie.ch/specs/pingback/pingback

The trackback specification can be located at
http://www.sixapart.com/pronet/docs/trackback_spec

Common Variables:
source - URL of the article located on YOUR site. LOCAL
target - URL of the article that is being linked to. EXTERNAL
server_url - URL of the linkback server to notify
data - Dictionary of information to send server

"""

__author__ = "Thadeus Burgess <thadeusb@thadeusb.com>"

import re
import xmlrpclib
import urllib, urllib2

#-----------------------------------------------------------------------
class LinkbackDataError(Exception): pass

class Linkback():
    """
    Abstract class that all linkback classes inherit from.
    
    Includes variables common to both client and server, and across
    multiple instances of linkback specifications.
    """
    
    NOT_YET = 'Not_Yet'
    NO_LINK = 'No_Link'
    SUCCESS = 'Success'
    FAILED = 'Failed'
    DONT = 'Dont'
    
    STATUS_MESSAGES = {
        NOT_YET: 'Not attempted',
        NO_LINK: 'No server URL found',
        SUCCESS: 'Success',
        FAILED: 'Failed',
        DONT: 'Do not attempt',
    }
    
    aRe = re.compile(r'''<a [^>]*?>''', re.IGNORECASE)
    hrefRe = re.compile(r'''href=['"](.*?)['"]''')
    titleRe = re.compile(r'<title>(.*)</title>')
    
    def __init__(self):
        pass
    
#-----------------------------------------------------------------------
class Pingback(Linkback):
    """
    Abstract class that all pingback classes inherit from.
    
    Includes variables common to both client and server pingback
    specifications.
    """
    
    PINGBACK_SOURCE_DOES_NOT_EXIST = 0x0010
    PINGBACK_SOURCE_DOES_NOT_LINK  = 0x0011
    PINGBACK_TARGET_DOES_NOT_EXIST = 0x0020
    PINGBACK_TARGET_CANNOT_BE_USED = 0x0021
    PINGBACK_ALREADY_REGISTERED    = 0x0030
    PINGBACK_ACCESS_DENIED         = 0x0031
    PINGBACK_UPSTREAM_ERROR        = 0x0032
    PINGBACK_OK                    = 'OK'
    
    pass
    
#-----------------------------------------------------------------------
class Trackback(Linkback):
    """
    Abstract class that all trackback classes inherit from.
    
    Includes variables common to both client and server trackback
    specifications.
    """
    pass
    
#-----------------------------------------------------------------------
class LinkbackClient():
    """
    Base class that should be inherited by a given linkback
    specification. This class implements basic client operations
    for linkback.
    
    Client operations:
    - Determining the server_url from a given target_url by using
    autodiscovery methods.
    - Sending relative data to the linkback server.
    
    
    """
    
    #-----------------------------------------------------------------------
    def __init__(self, source_url, target_url, fail_silently=True):
        """
        Default constructor.
        
        Keyword arguments:
        source_url -- URL of the article located on YOUR site. LOCAL
        target_url -- URL of the article being referenced. EXTERNAL
        fail_silently -- if True (default), will not raise an exception on error
                         if False, will raise exception on error
        
        """
        isinstance(source_url, (str, unicode))
        isinstance(target_url, (str, unicode))
        isinstance(fail_silently, bool)
        
        self.source_url = source_url
        self.target_url = target_url
        self.fail_silently = fail_silently
        
        self.status = Linkback.NOT_YET
        self.message = Linkback.STATUS_MESSAGES[self.status]
        
        self.__discovered = False
        self.server_url = None
    
    #-----------------------------------------------------------------------
    def send(self, data=None):
        """
        This method will contact the remote target and send
        the linkback information over. This method MUST be
        overridden by the child class
        
        Keyword arguments:
        data -- Dictionary of values to send to server
        
        """
        pass
    
    #-----------------------------------------------------------------------
    def discover(self):
        """
        Try to find the given URL by using autodiscovery
        
        This MUST be overridden by the child class
        """
        pass
    
#-----------------------------------------------------------------------
class LinkbackServer():
    """
    Base class that should be inherited by a given linkback
    specification. This class implements basic server operations
    for linkback.
    
    Server operations:
    - Parsing incoming data to determine if it is valid
    - Verify that the source_url includes a link to our target_url
    - Responding with the status and message.
    
    """
    
    #-----------------------------------------------------------------------
    def __init__(self, trim=255, fail_silently=True):
        """
        Base class for linkback servers.
        
        Class args:
        verified -- has the source been verified to have a link to target?
        
        Keyword arguments:
        trim -- index to trim incoming data (default 255)
        fail_silently -- if True (default), will not raise an exception on error
                         if False, will raise exception on error

        """
        self.trim = trim
        self.verified = False
        self.fail_silently = fail_silently
        
        self.status = Linkback.NOT_YET
        self.message = Linkback.STATUS_MESSAGES[self.status]
    
    #-----------------------------------------------------------------------
    def receive(self, data):
        """
        Handles incoming data
        
        Keyword arguments:
        data -- Dictionary of incoming data
             -> pass
        """
        pass
    
    #-----------------------------------------------------------------------
    def verify(self, source_url, target_url):
        """
        Verify that ``target_url`` exists in ``source_url``
        Also pulls the ``title`` of the ``source_url``.
        
        Keyword arguments:
        source_url -- Website that is linking to article. REMOTE
        target_url -- URL of the page being linked. LOCAL
        """
        try:
            remote = urllib2.urlopen(source_url)
            html = res.read()
            remote.close()
            
            m = Pingback.titleRe.search(html)
            
            if m:
                self.title = m.group(1)
            else:
                self.title = None
                
            self.target_exists = False
            
            for link in Pingback.hrefRe.findall(html):
                if link == target_url:
                    self.target_exists = True
        except Exception, e:
            self.status = self.FAILED
            self.message = "Exception was raised while verifying link, %s" % e
            
            if self.fail_silently:
                return
            else:
                raise e
            
        return self.target_exists
        

#-----------------------------------------------------------------------
class PingbackClient(Pingback, LinkbackClient):
    """
    Implements necessary functions for discovering and
    sending data to a server using the pingback specification.
    
    Pingback spec:
    http://www.hixie.ch/specs/pingback/pingback
    
    Autodiscovers server url by looking at the X-Pingback header
    or alternatively parsing the <link rel="pingback"... html.
    
    Uses XML-RPC to notify the server.
    pingback.ping('url that pings', 'url that is pinged')
    
    Static Attributes:
    pingbackRe -- regex to find pingback link in html
    
    """
    pingbackRe = re.compile('<link rel="pingback" href="([^"]+)" ?/?>')
    
    #-----------------------------------------------------------------------
    def send(self, data):
        """
        Send a XML-RPC pingback to ``target_url`` via the ``server_url``
        PingbackClient.discover() must be called beforehand.
        
        Keyword arguments:
        data -- UNUSED. Defined for compatibility with LinkbackClient.
        
        """
        isinstance(data, dict)
        
        if not self.__discovered:
            self.discover()
            
        
        if self.server_url:
            try:
                proxy = xmlrpclib.ServerProxy(self.source_url, self.target_url)
                response = proxy.pingback.ping(source, target)
                
                if reponse == self.PINGBACK_OK:
                    self.status = self.SUCCESS
                else:
                    self.status = self.FAILED
                    
                self.message = response
                
            except Exception, e:
                self.status = self.FAILED
                self.message = "Exception was raised, %s" % e
                
                if self.fail_silently:
                    return
                else:
                    raise e
        else:
            pass
                
        return self.status
    
    #-----------------------------------------------------------------------
    def discover(self):
        """
        Loads remote document from ``target_url`` and retrieves the
        url of the pingback server.
        
        Autodiscovers server url by looking at the X-Pingback header
        or alternatively parsing the <link rel="pingback"... html.
        
        """
        self.__discovered = True
        
        try:
            remote = urllib2.urlopen(self.target_url)
            self.server_url = remote.info().getheader('X-Pingback')
            
            if not self.server_url:
                m = PingbackClient.pingbackRe.findall(remote.read())
                # Make sure it exists
                if len(m) > 0:
                    self.server_url = m[0]
                
            # Either the URL or None            
            if not self.server_url:
                self.status = self.NO_LINK
                self.message = self.STATUS_MESSAGES[self.status]
                
        except Exception, e:
            self.status = self.FAILED
            self.message = "Exception was raised, %s" % e
            
            if self.fail_silently:
                return
            else:
                raise e
 
#-----------------------------------------------------------------------
class PingbackServer(Pingback, LinkbackServer):
    """
    Linkback server implementation.
    """
    
    #-----------------------------------------------------------------------
    def receive(self, data):
        """
        Receives and handles incoming pingback data.
        """
        if not data['source_url']:
            self.status = Pingback.FAILED
            self.message = Pingback.PINGBACK_SOURCE_DOES_NOT_EXIST
            
        if not data['target_url']:
            self.status = Pingback.FAILED
            self.message = Pingback.PINGBACK_TARGET_DOES_NOT_EXIST
            
        self.data = {
            'source_url': data['source_url'],
            'target_url': data['target_url'],
        }
        
        return self.data
            
    #-----------------------------------------------------------------------
    def verify(self, source_url, target_url):
        status = LinkbackServer.verify(self, source_url, target_url)
        
        if not status:
            self.status = Pingback.FAILED
            self.message = Pingback.PINGBACK_SOURCE_DOES_NOT_LINK
        else:
            self.status = Pingback.SUCCESS
            self.message = Pingback.PINGBACK_OK
#-----------------------------------------------------------------------
class TrackbackClient(Trackback, LinkbackClient):
    """
    Implements necessary functions for discovering and
    sending data to a server using the trackback specification.
    
    Trackback spec:
    http://www.sixapart.com/pronet/docs/trackback_spec
    
    Autodiscovers server url by looking at the html RDF attributes
    or alternatively parsing the <link rel="trackback"...
    
    Uses HTML POST to notify the server.
    url -- source_url
    title -- title of source article
    excerpt -- excerpt from target article
    site_name -- name of source site
    
    Static Attributes:
    rdfRe -- regex to find pingback link in html
    rdfIdRe -- regex to find rdf identifier element
    rdfTbRe -- regex to find rdf ping url
    linkTbRe -- scans link and a elements and extracts href.
    
    """
    rdfRe = re.compile(r'<rdf:Description.*?/>', re.DOTALL)
    rdfIdRe = re.compile(r'''dc:identifier=['"](.*?)['"]''')
    rdfTbRe = re.compile(r'''trackback:ping=['"](.*?)['"]''')
    linkTbRe = re.compile(r'''<(link|a) [^>]*rel=['"]trackback['"].*?>''', re.IGNORECASE)
    
    errorRe = re.compile(r'<error>(\d+)</error>')
    messageRe = re.compile(r'<message>(.*)</message>')
    
    #-----------------------------------------------------------------------
    def send(self, data):
        """
        Send a HTML POST to ``target_url`` via the ``server_url``
        TrackbackClient.discover() must be called beforehand
        
        Keyword arguments:
        data -- Dictionary of arguments to pass along to server
             -> 'title' -- title of source article
             -> 'excerpt' -- excerpt from target article
             -> 'site_name' -- name of source site
        
        """
        isinstance(data, dict)
        isinstance(data['title'], (str, unicode))
        isinstance(data['excerpt'], (str, unicode))
        isinstance(data['site_name'], (str, unicode))
        
        if not self.__discovered:
            self.discover()
            
        if self.server_url:
            try:
                mapping = {'url': self.source_url}
                if data['title']:
                    mapping['title'] = data['title']
                if data['excerpt']:
                    mapping['excerpt'] = data['excerpt']
                if data['site_name']:
                    mapping['blog_name'] = data['site_name']
                    
                params = urllib.urlencode(mapping)
                
                request = urllib2.Request(self.server_url)
                request.add_header('Content-type',
                    'application/x-www-form-urlencode; charset=utf-8')
                
                remote = urllib2.urlopen(request)
                html = remote.read()
                remote.close()
                
                m = self.errorRe.search(html)
                
                if m:
                    # get error message
                    code = int(m.group(1))
                    if code == 0:
                        self.status = self.SUCCESS
                        self.message = self.STATUS_MESSAGES[self.status]
                    else:
                        self.status = self.FAILED
                        m = self.messageRe.search(html)
                        if m:
                            self.message = "Error %s: %s" % (code, m.group(1))
                        else:
                            self.message = "Server did not respond with error"
                else:
                    self.status = self.FAILED
                    self.message = "Unknown server response"
                
            
            except Exception, e:
                self.status = self.FAILED
                self.message = "Exception was raised, %s" % e
                
                if self.fail_silently:
                    return
                else:
                    raise e
        else:
            pass
        
        return self.status
    
    #-----------------------------------------------------------------------
    def discover(self):
        """
        Loads remote document from ``target_url`` and retrieves the
        url of the pingback server.
        
        Autodiscovers server url by looking at the html RDF attributes
        or alternatively parsing the <link rel="trackback"...
        
        """
        self.__discovered = True
        
        try:
            remote = urllib2.urlopen(self.target_url)
            html = remote.read()
            remote.close()
            
            # Try RDF autodiscovery
            # A page can have multiple RDF blocks;
            # search for the one containing url
            for rdf in self.rdfRe.findall(html):
                # Check the identifier
                m = self.rdfIdRe.search(rdf)
                if not m: continue
                if m.group(1) != self.target_url:
                    continue
                
                # Find the trackback
                m = self.rdfTbRe.search(rdf)
                if not m:
                    continue
                self.server_url = m.group(1)
                
            if not self.server_url:
                # Look for a <link> or <a> with rel="trackback" and extract the href
                links = set()
                for linkMatch in self.linkTbRe.finditer(html):
                    link = linkMatch.group(0)
                    m = self.hrefRe.search(link)
                    if m:
                        links.add(m.group(1))
                        
                if len(links) == 1:
                    self.server_url = links.pop()
                    
            if not self.server_url:
                self.status = self.NO_LINK
                self.message = self.STATUS_MESSAGES[self.status]
                
        except Exception, e:
            self.status = self.FAILED
            self.message = "Exception was raised, %s" % e
            
            if self.fail_silently:
                return
            else:
                raise e
        
#-----------------------------------------------------------------------
class TrackbackServer(Trackback, LinkbackServer):
    """
    Trackback server implementation.
    """
    #-----------------------------------------------------------------------
    def receive(self, data):
        """
        Receives and handles incoming trackback data.
        """
        if not data['url']:
            self.status = "Error"
            self.message = "There is no url."
            return
            
        self.data = {'source_url': data['url']}
        
        if data['title']:
            self.data['title'] = data['title'][:self.trim]
        elif self.title:
            self.data['title'] = self.title[:self.trim]
        
        if data['blog_name']:
            self.data['site_name'] = data['blog_name'][:self.trim]
        if data['excerpt']:
            self.data['excerpt'] = data['excerpt'][:self.trim]
        
            self.status = "OK"
            
        return self.data

