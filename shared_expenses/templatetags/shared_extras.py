from django import template

register = template.Library()


@register.filter
def get_item(querydict_or_dict, key):
    """
    Get share_<key> from a QueryDict (request.POST) or plain dict.
    Usage: {{ request.POST|get_item:u.pk }}
    Returns the value of POST['share_<u.pk>'] if present, else ''.
    """
    if querydict_or_dict is None:
        return ''
    lookup_key = f'share_{key}'
    if hasattr(querydict_or_dict, 'get'):
        return querydict_or_dict.get(lookup_key, '')
    return ''
