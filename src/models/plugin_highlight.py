def html_entity_decode(text):
    """
    Removes HTML or XML character references and entities from a text string.
    
    @param text The HTML (or XML) source text.
    @return The plain text, as a Unicode string, if necessary.
    """
    import re, htmlentitydefs
    def fixup(m):
        text = m.group(0)
        if text[:2] == "&#":
            # character reference
            try:
                if text[:3] == "&#x":
                    return unichr(int(text[3:-1], 16))
                else:
                    return unichr(int(text[2:-1]))
            except ValueError:
                pass
        else:
            # named entity
            try:
                text = unichr(htmlentitydefs.name2codepoint[text[1:-1]])
            except KeyError:
                pass
        return text # leave as is
    return re.sub("&#?\w+;", fixup, text)

def __highlight__(content, dom_element='pre', linenos=True, noclasses=True):
    """
    Performs syntax highlighting on text inside of dom_element
    Uses BeautifulSoup for processing and pygments for highlighting
    
    @param content The HTML (or XML) content to parse
    @param dom_element The dom tag to search and replace with highlighted
    @return The content with highlighted code withing dom_element
    
    """
    from pygments import highlight
    from pygments.lexers import get_lexer_by_name
    from pygments.formatters import HtmlFormatter
    from BeautifulSoup import BeautifulSoup, BeautifulStoneSoup
    
    decodedString=unicode(BeautifulStoneSoup(content,convertEntities=BeautifulStoneSoup.HTML_ENTITIES ))
    #decodedString=html_entity_decode(content.encode('utf-8'))
    soup = BeautifulSoup(content)
    
    formatter = HtmlFormatter(linenos=linenos, noclasses=noclasses)
    
    for tag in soup.findAll(dom_element):
        language = tag.get('lang') or 'text'
        try:
            lexer = get_lexer_by_name(language, encoding='UTF-8')
        except:
            lexer = get_lexer_by_name('text', encoding='UTF-8')
        tag.replaceWith(highlight(tag.renderContents(), lexer, formatter))
        pass
    return unicode(str(soup), 'utf-8', errors='ignore')
    
