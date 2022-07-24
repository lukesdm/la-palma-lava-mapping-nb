import numpy
import pandas

def format_date(date: numpy.datetime64) -> str:
    """Formats date as 'YYY-MM-DD', e.g., '2021-09-16.'"""
    # Used in a variety of places - take care when changing this!
    # See: https://stackoverflow.com/questions/19502506/convert-numpy-datetime64-to-string-object-in-python
    return str(date)[:10]

def to_date(text: str) -> numpy.datetime64:
    return pandas.to_datetime(text)