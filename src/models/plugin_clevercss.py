##if request.env.http_host == '10.0.0.100:8000':
##   import os, stat, clevercss, re
##   
##   def save(match):
##      return ''
##        
##   cpat = re.compile(r'[\n\t\r\f\v]|(?s)\s\s')
##   
##   fs = [
##      (('static', 'css', 'admin'), #path to save
##          ('admin',) # clevercss files to include
##      ),
##      (('static', 'css', 'brunstworth'), (
##          'brunstworth', 'comments' ,
##      )),
##      (('static', 'css', 'comments'), (
##          'comments',
##      ))
##     ]
##   
##   for f in fs:
##      odata = ''
##      omdata = ''
##      for clv in f[1]:
##         filename = os.path.join(request.folder, 'private', clv+'.clevercss')
##         
##         def gettime(): return os.stat(filename)[stat.ST_SIZE]
##         
##         if not gettime() == cache.ram(filename, gettime, expire):
##            expire = 0
##            st_size = cache.ram(filename, gettime, expire)
##            
##            input = open(filename, 'r')
##            data = input.read()
##            input.close()
##            
##            data = clevercss.convert(data, dict(
##               DARK_BLUE = '#5E99E7',
##               BLUE = '#8FB6E9',
##               LIGHT_BLUE = '#C3E8FF',
##               LIGHTER_BLUE = '#66A5FB',
##               LIGHT_GREY = '#EFEFEF',
##               PINK = '#FF5C8D',
##               BORDER_GREY = '#DDDDDD',
##               LINE_GREY = '#EEEEEE',
##               RED = '#D0430B',
##            ))
##            
##            min_data = cpat.sub(save, data)
##            
##            odata += data
##            omdata += min_data
##       
##   
##   expire = 10**10 #never
##   filename = os.path.join(request.folder, 'private', 'admin.clevercss')
##
##You can just put your clevercss in
##
##private/style.clevercss
##
##and use a controller like this:
##
##def style():
##   import os, stat, clevercss
##   expire = 10**10 # never
##   filename = os.path.join
##(request.folder,'private','style.clevercss')
##   def gettime(): return os.stat(filename)[stat.ST_SIZE]
##   if not gettime() == cache.ram(filename,gettime,expire): expire = 0
### now
##   return cache.ram(filename+':data',lambda: clevercss.convert(open
##(filename,'rb').read(),{}),expire)
##
##to retrieve it cached and processed.

