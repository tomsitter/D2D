from csv import DictReader
import os
from collections import defaultdict, OrderedDict
import pdb

filepath = r'C:\Users\SAFHT_AdminTom\Documents\PHI\Chiropody'

initial = open(os.path.join(filepath, r'Chiropody - Initial.csv'))
latest = open(os.path.join(filepath, r'Chiropody_20160901_20161220.csv'))

init_dict = defaultdict(dict)
diff_dict = defaultdict(dict)
sex = defaultdict(int)
physician = defaultdict(int)
age = []
dm_foot_risk = defaultdict(int)
total_dm_foot_risk = 0
total_visits = 0
total_reasons = 0

visit_type = [
    "ChiropodyInitialConsult",
    "ChiropodyF/UConsult"
]

visit_reason = [
    "IngrownToeNailSurgery",
    "DMFootCare",
    "RoutineFootCare",
    "DMWoundCare",
    "DMFootAssessment",
    "PlantarWarts",
]

measures = visit_type + visit_reason

for row in DictReader(initial):
    pat = row["Patient #"]
    for measure in measures:
        init_dict[pat][measure] = int(row[measure])

for row in DictReader(latest):
    pat = row["Patient #"]
    for measure in measures:
        if pat in init_dict:
            diff_dict[pat][measure] = int(row[measure]) - init_dict[pat][measure]
        else:
            diff_dict[pat][measure] = int(row[measure])

        if measure in visit_type:
            total_visits += diff_dict[pat][measure]
        else:
            total_reasons += diff_dict[pat][measure]

    sex[row["Sex"]] += 1
    physician[row["patRef.fullName"].title()] += 1
    age.append(int(row["Age"]))
    if row["DMFootRisk:"].endswith(','):
        risk = row["DMFootRisk:"][:-1]
    else:
        risk = row["DMFootRisk:"]
    if risk != 'never done':
        total_dm_foot_risk += 1
    dm_foot_risk[risk] += 1


# Analysis

def count_all(d, measure):
    return sum(v[measure] for v in d.values())

def categorize_ages(ages):
    categories = OrderedDict([
        ("<30",   0), ("30-64", 0), ("65-74", 0),
        ("75-84", 0), ("85-94", 0), ("95+",   0) 
    ])

    for age in ages:
        if age > 94:
            categories["95+"] += 1
        elif age > 84:
            categories["85-94"] += 1
        elif age > 74:
            categories["75-84"] += 1
        elif age > 64:
            categories["65-74"] += 1
        elif age > 29:
            categories["30-64"] += 1
        else:
            categories["<30"] += 1

    return categories

def percent(value, total):
    return round(value/total*100, 1)

# Number of Patients
print("Number of patients: {}".format(len(diff_dict)))

# Count of each visit type
print("\nVisits:")
for visit_type in visit_types:
    print("{}: {} ({}%)".format(diff_dict[visit_type], 
                                count_all(diff_dict, visit_type),
                                percent(count_all(diff_dict, visit_type), total_visits)))
print("Total: ", total_visits)

# Count of each visit reason
print("\nReason For Visit:")
for visit_reason in visit_reasons:
    print("{}: {} ({}%)".format(diff_dict[visit_reason], 
                                count_all(diff_dict, visit_reason),
                                percent(count_all(diff_dict, visit_reason), total_reasons)))
print("Total: ", total_reasons)

print('\nDM Foot Risk')
for risk, count in sorted(dm_foot_risk.items()):
    print("{}: {} ({}%)".format(risk, count, percent(count, total_dm_foot_risk)))

# Gender
print("\nGender:")
for gender, count in sex.items():
    print("{}: {} ({}%)".format(gender, count, 
                                percent(count, len(diff_dict))))

# Age
print("\nAges:")
for age_group, count in categorize_ages(age).items():
    print("{}: {} ({}%)".format(age_group, count, percent(count, len(age))))
print("Age Range: ", min(age), "-", max(age))
    
# Physician
print("\nReferring Physician:")
for phys, count in sorted(physician.items()):
    if phys == "":
        phys = "Unknown"
    print("{}: {}".format(phys, count))