from django import template
register = template.Library()


@register.filter(name='httpdate')
def httpdate(dt):
    """
    Convert a datetime object into a string in RFC 1123 format.
    """
    return dt.strftime('%a, %d %b %Y %H:%M:%S GMT')