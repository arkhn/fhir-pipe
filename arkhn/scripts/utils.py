
def is_empty(value):
    return value is None \
           or value == 'NaN' \
           or value == '' \
           or value in '                        '
