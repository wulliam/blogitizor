# Statistics
###########################################################
db.define_table('guppy_heapy',
    Field('text', 'text'),
    Field('objects', 'integer'),
    Field('bytes', 'integer'),
    Field('measured_on', 'datetime', default=request.now),
)
def guppy_heapy():
    from guppy import hpy; hp=hpy()
    heap = hp.heap()

    objects = heap.count
    size = heap.size
    text = "%s" % heap
    text = text.replace("\n", "\n\n")
    
    row = db.guppy_heapy.insert(
        text=text,
        objects=objects,
        bytes=size,
    )
    return {
        'objects': objects,
        'bytes': size,
        'text': text,
        'measured_on': row.measured_on
    }
def guppy_heapy_avg():
    average_guppy_heapy = db(db.guppy_heapy.id > 0).select(
            db.guppy_heapy.objects.sum(),
            db.guppy_heapy.objects.count(),
            db.guppy_heapy.bytes.sum(),
            db.guppy_heapy.bytes.count(),
            cache=(cache.disk, 1800),
    ).first()
    return {
        'objects': average_guppy_heapy._extra[db.guppy_heapy.objects.sum()] / average_guppy_heapy._extra[db.guppy_heapy.objects.count()],
        'bytes': average_guppy_heapy._extra[db.guppy_heapy.bytes.sum()] / average_guppy_heapy._extra[db.guppy_heapy.bytes.count()],
    }
latest_guppy_heapy = lambda: cache.ram('guppy_heapy', 
    lambda: cache.disk('guppy_heapy', guppy_heapy, 1800), 600)
average_guppy_heapy = lambda: cache.ram('guppy_heapy_average',
    lambda: cache.disk('guppy_heapy_average', guppy_heapy_avg, 1800), 600)
###########################################################
