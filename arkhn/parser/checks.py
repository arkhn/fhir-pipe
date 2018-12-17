import re


def _is_empty(value):
    return value is None or value == 'NaN' or value == ''


def assert_has_sql_type(name_type, value):
    """
    State if value is of type name_type
    """
    if name_type in [None, '', 'uri', 'string']:
        if not isinstance(value, str):
            raise TypeError('{} <{}> should be a str.'.format(value, type(value)))
    elif name_type.startswith('code'):
        if '=' in name_type:
            options = name_type.split('=')[1].split('|')
            if not _is_empty(value) and not value in options:
                raise TypeError('{} <{}> should be in .'.format(value, type(value)), options)
    elif name_type in ('dateTime', 'date'):
        pat = re.compile(r'^\d{4}-\d{2}-\d{2}[T]\d{2}:\d{2}:\d{2}')
        if len(pat.findall(value)) == 0 and value != '':
            # raise TypeError('{} should be a ISO date (ex: 1998-02-17T00:00:00) .'.format(value))
            pass
    elif name_type == 'boolean':
        if not isinstance(value, bool) and value is not None:
            raise TypeError('{} <{}> should be a boolean.'.format(value, type(value)))
    else:
        raise TypeError('Type {} <{}> is not known.'.format(name_type, type(name_type)))
