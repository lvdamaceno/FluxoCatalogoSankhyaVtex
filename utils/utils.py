def fill_with_zeros(number=None):
    if number is None:
        return '000'
    return str(number).zfill(3)