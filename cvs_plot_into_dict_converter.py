import csv

def csv_to_dict(filename):
    result = {}
    with open(filename, 'r') as file:
        reader = csv.reader(file)
        for i, row in enumerate(reader):
            date = i+1
            for j, cell in enumerate(row):
                if cell not in ["X"]:
                    if date not in result:
                        result[date] = {}
                    result[date][j] = cell
    return result
