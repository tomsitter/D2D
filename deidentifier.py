import csv
from readers import open_csv
import random
import string


def deidentify(emr='accuro', target_fields=None, filename=None, output=None):
    """Reads a CSV and replaces fields with deidentified data of the same length and type.
       Deidentification preserves repeated groups of fields
       e.g. Rows with same first name, last name, and PHN will be deidentified the same way
       Deidentification will attempt to replace fields with similar types of characters
       i.e. numeric -> numeric, alphanumeric -> alphanumeric etc.

       deidentify(emr='accuro',
                  target_fields=['firstname', 'lastname', 'phn'],
                  filename='tests/identifiable.csv',
                  output='tests/unidentifiable.csv')
    """
    # Open a dict reader to the CSV file
    reader = open_csv(emr=emr, filename=filename)
    fieldnames = reader.fieldnames

    # Open a CSV file to write to
    out = open(output, 'w')
    writer = csv.writer(out, lineterminator='\n')

    # Make sure target_fields is a list
    if not isinstance(target_fields, list):
        target_fields = list(target_fields)

    # Make sure all fields to deidentify are in the file
    assert set(target_fields).issubset(fieldnames)

    # Have to build up list of unique tuples from the fieldnames
    unique_entries = {}

    # Loop through the file and write to output in a single pass
    for row in reader:
        new_row = []

        # get the identifiable columns from the row that need to be deidentified
        entry = tuple(row[field] for field in target_fields)

        # if we have already deidentified this row, let's replace those columns
        if entry in unique_entries:
            deidentified_entry = unique_entries[entry]
        else:
            deidentified_entry = deidentify_row(row, target_fields)
            unique_entries[entry] = deidentified_entry

        # fieldnames preserves ordering of fields in the original CSV file
        for field in fieldnames:
            if field in deidentified_entry.keys():
                new_row.append(deidentified_entry[field])
            else:
                new_row.append(row[field])

        writer.writerow(new_row)

    # close the output file
    out.close()

    print('Finished!')


def detect_type(entry):
    """Determines where a field is numeric, alphanumeric, or alphabetical letters only"""
    if entry.isdigit():
        return 'numeric'
    elif entry.isalpha():
        return 'alpha'
    elif entry.isalnum():
        return 'alnum'
    else:
        return 'alpha'


def replace_entry(value):
    """Returns a random string of the given type and of the same length as the original value"""
    type_ = detect_type(value)

    if type_ == 'numeric':
        chars = string.digits
    elif type_ == 'alpha':
        chars = string.ascii_lowercase
    else:
        chars = string.digits + string.ascii_lowercase

    return ''.join(random.choice(chars) for _ in range(len(value)))


def deidentify_row(row, fields):
    """Deidentifies the specified fields in all rows of a CSV file
        Returns  dict mapping field name -> new deidentified value"""

    deidentified_entry = {}

    for field in fields:
        deidentified_entry[field] = replace_entry(row[field])

    return deidentified_entry
