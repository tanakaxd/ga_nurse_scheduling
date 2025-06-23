import csv

def transform_schedule(*, input_file):
    # Initialize the output list
    output = []
    
    # Read the CSV file
    with open(input_file, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        headers = reader.fieldnames
        
        # Identify staff columns (excluding meta columns)
        staff_cols = [col for col in headers if col not in ['日付', '曜日', '備考', 'cnt', 'vld', 'メガネ'] and col.strip()]
        
        # Process each row
        for row in reader:
            if not row['曜日'].strip():  # Stop if no date
                break
            day_schedule = []
            for staff in staff_cols:
                value = row[staff].strip()
                # Convert '休' to 'R', 'C/D' to 'C', keep other values as is
                if value == '休':
                    day_schedule.append('R')
                elif value == 'C/D':
                    day_schedule.append('C')
                elif value == '':
                    day_schedule.append('X')
                else:
                    day_schedule.append(value)
            output.append(','.join(day_schedule))
    
    # Return the transformed data as a list of strings
    return output

# Example usage
if __name__ == "__main__":
    input_file = "/home/ttnk0/projects/ga_nurse_scheduling/data/岡田眼科202507シフト表 - fixed_plot.csv"
    output_file = "/home/ttnk0/projects/ga_nurse_scheduling/data/_fixed_plot.csv"
    result = transform_schedule(input_file=input_file)
    
    # Write to CSV file
    with open(output_file, 'w', encoding='utf-8', newline='') as file:
        writer = csv.writer(file)
        # Write each line as a row
        for line in result:
            writer.writerow(line.split(','))
    
    # Print to console
    for line in result:
        print(line)