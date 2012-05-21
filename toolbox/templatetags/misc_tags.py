from django import template
from django.utils.safestring import mark_safe, SafeData
from django.template.defaultfilters import stringfilter

register = template.Library()

def datejs(dt):
    """
    Reformats a datetime object as a JavaScript Date() object.
    """
    if hasattr(dt, 'hour') and hasattr(dt, 'minute') and hasattr(dt, 'second'):
        js = 'Date(%s, %s, %s, %s, %s, %s)' % (
            dt.year, dt.month-1, dt.day,
            dt.hour, dt.minute, dt.second,
        )
    else:
        js = 'Date(%s, %s, %s)' % (dt.year, dt.month-1, dt.day)
    return mark_safe(js)
datejs.is_safe = True
register.filter(datejs)


_base_js_escapes = (
    ('\\', r'\u005C'),
    ('\'', r'\u0027'),
    ('"', r'\u0022'),
    ('>', r'\u003E'),
    ('<', r'\u003C'),
    ('&', r'\u0026'),
    ('=', r'\u003D'),
    ('-', r'\u002D'),
    (';', r'\u003B'),
    (u'\u2013', r'\u2013'),
    (u'\u2014', r'\u2014'),
    (u'\u2019', r'\u2019'),
    (u'\u201c', r'\u201c'),
    (u'\u201d', r'\u201d'),
    (u'\u2028', r'\u2028'),
    (u'\u2029', r'\u2029'),
    (u'\xbd', r'\xbd')
)

# Escape every ASCII character with a value less than 32.
_js_escapes = (_base_js_escapes +
               tuple([('%c' % z, '\\u%04X' % z) for z in range(32)]))

def escapejs(value):
    """
    Replaces Django's built-in escaping function with one that actually works.

    Take from "Changeset 12781":http://code.djangoproject.com/changeset/12781
    """
    for bad, good in _js_escapes:
        value = value.replace(bad, good)
    return value
escapejs = stringfilter(escapejs)
register.filter(escapejs)
