import csv
import os
from readers import EMRDictReader
import random
import string
from simplecrypt import encrypt, decrypt
from getpass import getpass
import pickle
import sys

def deidentify_multiple(emr='accuro', target_fields=None, filenames=None, outputs=None):
    """ Calls deidentify with multiple input and output files. This allows deidentification
        to span multiple files while remaining consistant.
        One deidentificated dict can still be saved for all files
    """
    unique_entries = {}
    for filename, output in zip(filenames, outputs):
        deidentify(emr=emr,
                   target_fields=target_fields,
                   filename=filename,
                   output=output,
                   unique_entries=unique_entries,
                   ask_encrypt=False)

    
    save_encrypted_dict(unique_entries)


def deidentify(emr='accuro', target_fields=None, filename=None, output=None, unique_entries=None, ask_encrypt=True):
    """ Reads one or more CSVs and replaces fields with deidentified data of the same length and type.
        Deidentification preserves repeated groups of fields
        e.g. Rows with same first name, last name, and PHN will be deidentified the same way
        Deidentification will attempt to replace fields with similar types of characters
        i.e. numeric -> numeric, alphanumeric -> alphanumeric etc.

        deidentify(emr='accuro',
                   target_fields=['firstname', 'lastname', 'phn'],
                   filename='tests/identifiable.csv',
                   output='tests/unidentifiable.csv')

        Note: If deidentifying multiple files, the target fields must be the same in all files

        Certain relationships can be maintained (e.g. patient to doctor) by doing two deidentifications
        Each time, specify a different column to be deidentified.
    """
    assert os.path.exists(filename)

    with open(filename) as f:
        reader = EMRDictReader(f, emr=emr)
        # Open a dict reader to the CSV file
        fieldnames = reader.fieldnames

        # Make sure target_fields is a list
        if not isinstance(target_fields, list):
            target_fields = [target_fields]

        # Make sure all fields to deidentify are in the file
        assert set(target_fields).issubset(fieldnames)

        # Open a CSV file to write to, write header
        with open(output, 'w') as out:
            writer = csv.writer(out, lineterminator='\n')
            writer.writerow(fieldnames)

            # When deidentifying multiple files we may be passed a dict of currently
            # deidentified entries that have already been compiled, otherwise initialize one
            if unique_entries is None:
                unique_entries = {
                    'entries': {},
                    'fields': target_fields
                }
            # Loop through the file and write to output in a single pass
            for row in reader:
                new_row = []

                # get the identifiable columns from the row that need to be deidentified
                entry = tuple(row[field] for field in target_fields)

                # if we have already deidentified this row, let's replace those columns
                if entry in unique_entries['entries']:
                    deidentified_entry = unique_entries['entries'][entry]
                else:
                    deidentified_entry = deidentify_row(row, target_fields)
                    unique_entries['entries'][entry] = deidentified_entry

                # fieldnames preserves ordering of fields in the original CSV file
                temp = dict(zip(target_fields, deidentified_entry))
                for field in fieldnames:
                    if field in target_fields:
                        new_row.append(temp[field])
                    else:
                        new_row.append(row[field])

                writer.writerow(new_row)

        print('Finished!')

        if ask_encrypt:
            save_encrypted_dict(unique_entries)


def reidentify(filename=None, output=None):

    assert os.path.exists(filename)

    with open(filename) as f:
        deid_data = load_encrypted_dict()
        target_fields = deid_data['fields']
        reid_rows = {v: k for k,v in deid_data['entries'].items()}

        # Open the encrypted file and make sure the fields in each match
        reader = EMRDictReader(f, emr='accuro')
        if not all(field in reader.fieldnames for field in target_fields):
            sys.exit("Mismatch between fields in encrypted file and fields in deidentified data!")

        with open(output, 'w') as out:
            writer = csv.writer(out, lineterminator='\n')
            writer.writerow(reader.fieldnames)
            for row in reader:
                patient = tuple(row[field] for field in target_fields)
                print(patient)
                try:
                    identifiable_info = reid_rows[patient]

                    for key, value in zip(target_fields, identifiable_info):
                        row[key] = value

                    writer.writerow([row[key] for key in reader.fieldnames])

                except KeyError as err:
                    print("Patient not found in encrypted file!")
                    raise err

    print('Finished reidentification!')


def detect_type(entry):
    """Determines where a field is numeric, alphanumeric, or alphabetical letters only"""
    import re

    if entry.isdigit():
        return 'numeric'
    elif entry.isalpha():
        return 'alpha'
    elif entry.isalnum():
        return 'alnum'
    elif re.match(r'\d{1,2}/\d{1,2}/\d{4}', entry):
        return 'date'
    else:
        return 'alpha'


def transform(value):
    """Returns a random string of the given type and of the same length as the original value"""
    type_ = detect_type(value)

    if type_ == 'numeric':
        chars = string.digits
    elif type_ == 'alpha':
        chars = string.ascii_lowercase
    elif type_ == 'date':
        return dob_to_yob(value)
    else:
        chars = string.digits + string.ascii_lowercase

    return ''.join(random.choice(chars) for _ in range(len(value)))


def deidentify_row(row, fields, method='random'):
    """Deidentifies the specified fields in all rows of a CSV file
        Returns  dict mapping field name -> new deidentified value"""
    deidentified_entry = tuple(transform(row[field]) for field in fields)

    return deidentified_entry


def save_encrypted_dict(unique_entries):
    """ Asks user if they want to save the deidentification table.
        This will write an encrypted txt file to the user-defined location
    """
    ans = input('Would you like to save an encrypted copy of the deidentification table? (Y/N): ')
    if ans != 'Y':
        return
    
    filename = ask_save_filename()

    # Ask if we want to encrypt the deidentifying data
    password = getpass('encryption password: ')

    with open(filename, 'wb') as output:
        json_data = pickle.dumps(unique_entries)
        ciphertext = encrypt(password, json_data)
        output.write(ciphertext)

    print('Finished writing the encrypted deidentification data!') 


def load_encrypted_dict():
    ans = input('Would you like to load an deidentification table for reidentification? (Y/N): ')
    if ans != 'Y':
        return

    filename = ask_load_filename()

    if not filename:
        return
    
    password = getpass('encryption password: ')

    with open(filename, 'rb') as enc_input:
        ciphertext = enc_input.read()
        data = pickle.loads(decrypt(password, ciphertext))
        return data
    

def ask_save_filename():
    # Ask for filename
    filename = input('Enter the full path and filename to save the table (Ctrl-C to cancel): ')
    if os.path.exists(filename):
        ans = input('This file already exists, are you sure you want to overwrite it? (Y/N): ')
        if ans == 'N':
            # Recursion, baby
            filename = ask_save_filename()

    return filename


def ask_load_filename():
    # Ask for filename
    filename = input('Enter the full path and filename to load the table (Ctrl-C to cancel): ')
    if not os.path.exists(filename):
        ans = input('This file doesn\'t exist, do you want to try again? (Y/N): ')
        if ans == 'Y':
            # Recursion, baby
            filename = ask_load_filename()
        else:
            return
        
    return filename


def dob_to_yob(dob):
    import re
    try:
        yob = re.search(r'\d{1,2}/\d{1,2}/(\d{4})', dob).group(1)
    except AttributeError as err:
        print(err)
        assert False

    return yob


if __name__ == '__main__':
    filename = 'C:\\Users\\admin\\Documents\\GitHub\\D2D\\tests\\data\\pss.test.deid.toreid.csv'
    output = 'C:\\Users\\admin\\Documents\\GitHub\\D2D\\tests\\data\\pss.test.reid.csv'
    reidentify(filename=filename, output=output)
