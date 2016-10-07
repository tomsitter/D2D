from csv import DictReader


class EMRDictReader(DictReader):
    """Reads a CSV file from an EMR export. Accepts "pss" and "accuro"
    """
    def __init__(self, f, emr=None, *args, **kwargs):
        # PSS puts a newline at the start of the file
        if emr.lower() == 'pss':
            next(f)

        super().__init__(f)
