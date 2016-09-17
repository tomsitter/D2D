#! python3

from csv import DictReader
from collections import defaultdict
import os
from reader import open_csv

def calc_score(emr=None, filename=None, field=None, target_field=None):
    """Reads a CSV and categorizes and counts rows based on a unique entries in field
    emr can either be "pss" or "accuro"

    If you would like a list of items instead of the count provide target_field
    e.g. calc_score(emr='accuro',
                    filename='smoking_denom.csv',
                    field='Enrolled Provider Last Name',
                    target_field='PHN')
    This will return a dictionary with each key being a unique provider and each value being a last of health numbers
    Leaving out target_field will just return the total count of patients for each provider
    """
    reader = open_csv(emr=emr, filename=filename)
    
    assert field in reader.fieldnames
    if target_field:
        assert target_field in reader.fieldnames
    
    for row in reader:
        if target_field:
            result[row[field].lower()].append(row[target_field])
        else:
            result[row[field].lower()] += 1
            
    return result

def print_summary(numer={}, denom={}):
    """ Takes two dicts with identical keys, calculates the ratio between them and prints it
        If dict values are lists it will take the length, otherwise it will assume they are integer counts
    """
    for key, d in denom.items():
        n = numer[key]
        if type(d) is list:
            d = len(d)
        if type(n) is list:
            n = len(n)

        print(key, ":", n , "/", d, "=", n/d)

        
