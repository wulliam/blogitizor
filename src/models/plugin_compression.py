import re

def save_pre(match):
    s = match.group()
    if s.startswith('<pre') \
       or s.startswith('<textarea') \
       or s.startswith('<blockquote'):
        pass
    else:
        s = ''
    return s

def compress_response(d):
    if callable(d):
        d = d()
    if isinstance(d, dict):
        cpat = re.compile(r'[\n\t\r\f\v]|(?s)\s\s\s|(?s)<pre(.*?)</pre>|(?s)<blockquote(.*?)</blockquote>|(?s)<textarea(.*?)</textarea>')
        d = cpat.sub(save_pre, response.render(d))
        lgh = latest_guppy_heapy()
    return d

if not request.env.http_host.endswith("8000"):
    response._caller = compress_response