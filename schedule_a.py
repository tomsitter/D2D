import csv
import os
from datetime import datetime
from collections import defaultdict, namedtuple
from operator import attrgetter
import pdb

__author__ = 'Tom Sitter'

Event = namedtuple('Event', ['date', 'value'])

date_format = '%m/%d/%Y'


filepath = r'C:\Users\admin\Documents\East GTA\Schedule A'


def weight_mgmt():

    billing_file = 'WM_Weight_20160401-20160930.csv'

    weights = build_dict(filename=os.path.join(filepath, billing_file),
                         key=('First Name', 'Last Name'),
                         event_fields=Event(date='Collection Date', value='Value'))

    for patient, events in weights.items():
        sorted_dates = sorted([event.date for event in events])

        if len(sorted_dates) > 1:
            start_date, end_date = sorted_dates[0], sorted_dates[-1]
            start = float([event.value for event in events if event.date == start_date][0])
            end = float([event.value for event in events if event.date == end_date][0])

            print(patient, ":", round((end-start)/start*100, 2), "%")
        else:
            print(patient, ": Only 1 weight")



def mental_health():

    init_code = 'MHINI'
    followup_code = 'MHFU'

    summary = {
        'no fu': [],
        'no init': [],
        'fu': []
    }



    billing_file = 'MH_Billing_20160401-20160930.csv'
    phq9_file = 'MH_PHQ9_20160401-20160930.csv'
    gad7_file = 'MH_GAD7_20160401-20160930.csv'

    bills = build_dict(filename=os.path.join(filepath, billing_file),
                       key='PHN',
                       event_fields=Event(date='Bill Date', value='PCode'))

    phq9s = build_dict(filename=os.path.join(filepath, phq9_file),
                       key='PHN',
                       event_fields=Event(date='Observation Date', value='Value'))

    gad7s = build_dict(filename=os.path.join(filepath, gad7_file),
                       key='PHN',
                       event_fields=Event(date='Observation Date', value='Value'))

    for patient, events in bills.items():
        init_date, filtered_events = filter_events_by_code(events, init_code=init_code)

        if not init_date:
            # print('Patient: ', patient, 'Status: N/A -- No Init Date')
            # summary['no init'].append(patient)
            continue

        filtered_phq9_events = filter_events_by_date(phq9s[patient],
                                                     init_date=init_date)
        filtered_gad7_events = filter_events_by_date(gad7s[patient],
                                                     init_date=init_date)

        if len(filtered_phq9_events) >= 2:
            init_phq9, final_phq9 = filtered_phq9_events[0], filtered_phq9_events[-1]
            print('Patient: ', patient, 'PHQ9 Status: ', get_patient_status(int(init_phq9.value),
                                                                            int(final_phq9.value)))

        if len(filtered_gad7_events) >= 2:
            init_gad7, final_gad7 = filtered_gad7_events[0], filtered_gad7_events[-1]
            print('Patient: ', patient, 'GAD7 Status: ', get_patient_status(int(init_gad7.value),
                                                                            int(final_gad7.value)))


def build_dict(filename=None, key=None, event_fields=None):
    """Given a filename to a CSV file, and which key and values we want to extract, build a dict"""
    events = defaultdict(list)

    with open(filename) as f:
        reader = csv.DictReader(f)

        for row in reader:
            if isinstance(key, tuple):
                patient_key = ' '.join([row[e] for e in key]).title()
            else:
                patient_key = row[key]

            event = Event(date=datetime.strptime(row[event_fields.date], date_format).date(),
                          value=row[event_fields.value])
            events[patient_key].append(event)

    return events


def filter_events_by_code(events, init_code=None):
    """Given a list of events and an initial billing code,
    Return a sorted list of all billing events that occurred from the
    date of the most recent initial billing onward"""

    # Sort events by date and get the most recent initial visit date
    sorted_event_dates = sorted([event.date for event in events if event.value == init_code])

    if not sorted_event_dates:
        return None, []
    else:
        init_date = sorted_event_dates[-1]

    # Make sure patient has had a initial visit billed
    if not init_date:
        return None, []

    # Now go through all events and pull values for any dates occurring on or after the initial visit date
    return (init_date, [event
                        for event in sorted(events, key=attrgetter('date'))
                        if event.date >= init_date]
            )


def filter_events_by_date(events, init_date=None):
    return [event
            for event in sorted(events, key=attrgetter('date'))
            if event.date >= init_date]


def get_patient_status(start, end):
    if not isinstance(end, int) or not isinstance(start, int):
        return 'NA'
    elif end < start:
        return 'Improved'
    elif end == start:
        return 'Same'
    elif end > start:
        return 'Worsened'
