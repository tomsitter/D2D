from csv import DictReader
import os


def open_csv(emr=None, filename=None):
    """Reads a CSV file from an EMR export. Accepts "pss" and "accuro"
    """
    assert emr.lower() in ('accuro', 'pss')
    assert os.path.exists(filename)

    f = open(filename)
    # PSS puts a newline at the start of the file
    if emr.lower() == 'pss':
        next(f)

    reader = DictReader(f)

    return reader
