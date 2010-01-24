# coding: utf8

response.title = "Search"
response.display_sidebar = False

display_count = 20

import re

# Stop Words courtesy of http://www.dcs.gla.ac.uk/idom/ir_resources/linguistic_utils/stop_words
STOP_WORDS = r"""\b(a|about|above|across|after|afterwards|again|against|all|almost|alone|along|already|also|
although|always|am|among|amongst|amoungst|amount|an|and|another|any|anyhow|anyone|anything|anyway|anywhere|are|
around|as|at|back|be|became|because|become|becomes|becoming|been|before|beforehand|behind|being|below|beside|
besides|between|beyond|bill|both|bottom|but|by|call|can|cannot|cant|co|computer|con|could|couldnt|cry|de|describe|
detail|do|done|down|due|during|each|eg|eight|either|eleven|else|elsewhere|empty|enough|etc|even|ever|every|everyone|
everything|everywhere|except|few|fifteen|fify|fill|find|fire|first|five|for|former|formerly|forty|found|four|from|
front|full|further|get|give|go|had|has|hasnt|have|he|hence|her|here|hereafter|hereby|herein|hereupon|hers|herself|
him|himself|his|how|however|hundred|i|ie|if|in|inc|indeed|interest|into|is|it|its|itself|keep|last|latter|latterly|
least|less|ltd|made|many|may|me|meanwhile|might|mill|mine|more|moreover|most|mostly|move|much|must|my|myself|name|
namely|neither|never|nevertheless|next|nine|no|nobody|none|noone|nor|not|nothing|now|nowhere|of|off|often|on|once|
one|only|onto|or|other|others|otherwise|our|ours|ourselves|out|over|own|part|per|perhaps|please|put|rather|re|same|
see|seem|seemed|seeming|seems|serious|several|she|should|show|side|since|sincere|six|sixty|so|some|somehow|someone|
something|sometime|sometimes|somewhere|still|such|system|take|ten|than|that|the|their|them|themselves|then|thence|
there|thereafter|thereby|therefore|therein|thereupon|these|they|thick|thin|third|this|those|though|three|through|
throughout|thru|thus|to|together|too|top|toward|towards|twelve|twenty|two|un|under|until|up|upon|us|very|via|was|
we|well|were|what|whatever|when|whence|whenever|where|whereafter|whereas|whereby|wherein|whereupon|wherever|whether|
which|while|whither|who|whoever|whole|whom|whose|why|will|with|within|without|would|yet|you|your|yours|yourself|
yourselves)\b"""

stop_words_list = re.compile(STOP_WORDS, re.IGNORECASE)

w = utils.w
ws = utils.ws

def index():
    if request.vars.q:
        q = stop_words_list.sub('', request.vars.q)
        
        query = (
              db.page.title.lower().like(w(q)) 
            | db.page.content.lower().like(ws(q))
        )
        
        for qs in filter(lambda a: a != '', q.split(' ')):
            query = query | db.page.content.lower().like(w(qs.strip()))
        
        paginate = utils.Pagination(db, query, 
                                    ~db.page.posted_on,
                                   display_count = 25,
                                   cache=(cache.ram, 5),
                                   r=request, res=response)
        
        pages = paginate.get_set()
                
        results = {'pages': pages}
        response.title += ': ' + q
    else:
        query = None
        results = None
        
    return dict(results=results, query=request.vars.q)
