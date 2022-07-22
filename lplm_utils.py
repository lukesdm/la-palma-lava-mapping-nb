import numpy

def format_date(date: numpy.datetime64) -> str:
    """Formats date as 'YYY-MM-DD', e.g., '2021-09-16.'"""
    # Used for both presentation and filename based ops - careful!
    return str(date)[:10]