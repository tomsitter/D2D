from collections import defaultdict
from csv import DictReader
import os
from reader import open_csv
import random
import string

def deidentify(emr=None, target_fields=None, filename=None, output=None):
    """Reads a CSV and replaces fields with deidentified data of the same length and type.
       Deidentification preserves repeated groups of fields
       e.g. Rows with same firstname, lastname, and PHN
       Deidentification will attempt to replace fields with similar types of characters
       i.e. numeric -> numeric, alphanumeric -> alphanumeric etc.
    """
    # Open a dict reader to the CSV file
    reader = open_csv(emr=emr, filename=filename)

    # Make sure all fields to deidentify are in the file
    assert set(target_fields).issubset(reader.fieldnames)

    deidentified_file = []

    # Have to build up list of unique tuples from the fieldnames
    unique_entries = {}
    for row in reader:
        entry = []
        new_row = []
        # Loop through fields twice:
        # 1. Get all entries that need to be deidentified, see if they have already (if not, do it)
        # 2. Add all the fields to the new list using the deidentified data
        for field in row.fieldnames:
            if field in target_fields:
                entry.append(row[field])
            else:
                new_row.append(row[field])

        # Convert to tuple to use as dict key
        key = tuple(entry)
        if key in unique_entries.keys():
            # Only want to add a key once
        else:
            unique_entries[tuple(entry)] = ()
    
    # I now have a dict with the key being the values to be deidentified


def detect_type(entry):
    """Determines where a field is numeric, alphanumeric, or alphebetical letters only"""
    if entry.isdigit():
        return 'numeric'
    elif entry.isalpha():
        return 'alpha'
    elif entry.isalnum():
        return 'alnum'
    else:
        return 'alpha'

def replace_entry(type_, value):
    if type_ == 'numeric':
        chars = string.digits
    elif type_ == 'alpha':
        chars = string.ascii_lowercase
    elif type_ == 'alnum':
        chars = string.digits + string.ascii_lowercase

    return ''.join(random.choice(chars) for _ in value)

def randomize_data(types, values):
    """Given a tuple of field types, returns a randomized tuple of values"""
    deidentified_data = []
    for type_, value in zip(types, values):
        deidentified_data.append(replace_entry(type_, value))

    return deidentified_data
        

def deindentify_row(rows, fields):
    """Deidentifies the specified fields in all rows of a CSV file"""
