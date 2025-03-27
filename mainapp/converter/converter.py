import csv
import io
import json
import os
from datetime import datetime

def csv_to_json(file):
    file.seek(0)  # Ensure the file pointer is at the beginning
    reader = list(csv.reader(io.StringIO(file.read().decode("utf-8"))))

    # Identify the starting row for timetable data
    start_index = None
    for i, row in enumerate(reader):
        if row and "DAY" in row[0].upper():
            start_index = i
            break

    if start_index is None:
        return json.dumps({"error": "No valid timetable structure found"}, indent=2)

    reader = reader[start_index:]  # Skip metadata rows
    time_slots = [slot.strip() for slot in reader[0][1:] if slot.strip()]
    timetable = {}

    weekdays = {
        "MONDAY",
        "TUESDAY",
        "WEDNESDAY",
        "THURSDAY",
        "FRIDAY",
    }

    for i in range(
        1, len(reader), 2
    ):  # Iterate two rows at a time (subjects and teachers)
        if i + 1 < len(reader):  # Ensure the next row exists
            day = reader[i][0].strip().upper()
            if day not in weekdays:
                continue  # Skip rows that are not part of the main weekday schedule

            timetable[day] = []  # Initialize list for day's classes
            subjects = [
                cell.split("(")[0].strip()
                for cell in reader[i][1 : len(time_slots) + 1]
            ]  # Remove extra mapping info
            teachers = reader[i + 1][1 : len(time_slots) + 1]

            for j, subject in enumerate(subjects):
                subject = subject.strip()
                if subject and subject not in ["BREAK", "LUNCH", ""]:
                    timetable[day].append(
                        {
                            "teacher_id": (
                                teachers[j].strip()
                                if j < len(teachers) and teachers[j]
                                else "Unknown"
                            ),
                            "subject_id": subject,
                            "time_slot": time_slots[j],
                        }
                    )

    return json.dumps(timetable, indent=2)


def extract_time_slots_for_teacher(timetable, time_slot_order):
    """Extract and sort time slots dynamically based on backend input."""
    unique_slots = {entry["time_slot"] for day_data in timetable.values() for slots in day_data.values() for entry in slots}
    sorted_slots = sorted(unique_slots, key=lambda slot: time_slot_order.get(slot, float('inf')))
    return [("CLASS", slot) for slot in sorted_slots]

def teacher_json_to_csv(teacher_timetable, output_folder, time_slots):
    """Convert teacher timetable dictionary to CSV with dynamic time slots."""
    os.makedirs(output_folder, exist_ok=True)
    time_slot_order = {v: k for k, v in time_slots.items()}
    days_of_week_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday","Saturday"]

    for teacher_id, schedule in teacher_timetable.items():
        final_slots = extract_time_slots_for_teacher(schedule, time_slot_order)
        csv_file = os.path.join(output_folder, f"{teacher_id}.csv")
        header = ["DAY"] + [slot[1] for slot in final_slots]
        rows = []

        sorted_days = sorted(schedule.items(), key=lambda x: days_of_week_order.index(x[0]))

        for day, day_data in sorted_days:
            row = [day] + ["" for _ in final_slots]
            
            for section, classes in day_data.items():
                for entry in classes:
                    for i, slot in enumerate(final_slots):
                        if entry["time_slot"] == slot[1]:
                            row[i + 1] = f"{entry['subject_id']} ({section}, {entry['classroom_id']})"
            
            rows.append(row)

        with open(csv_file, mode="w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(header)
            writer.writerows(rows)

if __name__ == "__main__":
    # Load teacher timetable from samples/teacher.json
    json_file = os.path.join(os.path.dirname(__file__), "samples", "teacher.json")  # Fixed path

    if not os.path.exists(json_file):
        print(f"Error: {json_file} not found!")
    else:
        with open(json_file, "r", encoding="utf-8") as file:
            teacher_tt = json.load(file)

        # Define time slots mapping
        time_slots = {
            1: "08:00 - 09:00",
            2: "09:00 - 10:00",
            3: "11:00 - 12:00",
            4: "12:00 - 13:00",
            5: "16:50 - 17:50",
        }

        # Convert JSON timetable to CSVs inside samples/tt_csvs
        output_folder = os.path.join(os.path.dirname(__file__), "samples", "teacher_tt_csvs")
        os.makedirs(output_folder, exist_ok=True)  # Ensure folder exists

        teacher_json_to_csv(teacher_tt, output_folder, time_slots)
        print(f"Teacher CSV files have been saved in '{output_folder}'.")


def extract_time_slots_for_classroom(timetable, time_slot_order):
    """Extract and sort time slots from the timetable based on a predefined order."""
    unique_slots = set()
  
    # Collect all unique time slots
    for day_data in timetable.values():
        for slots in day_data.values():
            for entry in slots:
                if isinstance(entry, dict) and "time_slot" in entry:
                    unique_slots.add(entry["time_slot"])
                else:
                    print(f"⚠️ ERROR: Unexpected entry format -> {entry}")

    sorted_slots = sorted(unique_slots, key=lambda slot: time_slot_order.get(slot, float('inf')))
    
    return [("CLASS", slot) for slot in sorted_slots]

def classroom_json_to_csv(classroom_timetable, output_folder, time_slots):
    """Convert classroom timetable JSON to CSV."""
    os.makedirs(output_folder, exist_ok=True)  # Ensure output folder exists
    time_slot_order = {v: k for k, v in time_slots.items()}
    days_of_week_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]

    for classroom_id, schedule in classroom_timetable.items():
        final_slots = extract_time_slots_for_classroom(schedule, time_slot_order)
        csv_file = os.path.join(output_folder, f"{classroom_id}.csv")
        header = ["DAY"] + [slot[1] for slot in final_slots]
        rows = []

        # Sort days correctly
        sorted_days = sorted(schedule.items(), key=lambda x: days_of_week_order.index(x[0]) if x[0] in days_of_week_order else float('inf'))

        for day, day_data in sorted_days:
            row = [day] + ["" for _ in final_slots]  # Empty slots initially
            
            for section, classes in day_data.items():
                for entry in classes:
                    for i, slot in enumerate(final_slots):
                        if entry["time_slot"] == slot[1]:
                            row[i + 1] = f"{entry['subject_id']} ({section}, {entry['teacher_id']})"
            
            rows.append(row)

        # Write to CSV
        with open(csv_file, mode="w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(header)
            writer.writerows(rows)  

# if __name__ == "__main__":
    
#     """Main function to load timetable and generate CSVs."""
#     json_file = os.path.join(os.path.dirname(__file__), "samples", "class.json")  # ✅ Fixed path

#     if not os.path.exists(json_file):
#         print(f"❌ Error: {json_file} not found!")

#     with open(json_file, "r", encoding="utf-8") as file:
#         classroom_tt = json.load(file)

#     # Define time slots mapping (Modify as needed)
#     time_slots = {
#         1: "08:00 - 09:00",
#         2: "09:00 - 10:00",
#         3: "11:00 - 12:00",
#         4: "12:00 - 13:00",
#         5: "16:50 - 17:50",
#     }

#     # Output folder for CSV files
#     output_folder = os.path.join(os.path.dirname(__file__), "samples", "class_csvs")
#     os.makedirs(output_folder, exist_ok=True)  # Ensure folder exists

#     # Convert JSON timetable to CSV
#     classroom_json_to_csv(classroom_tt, output_folder, time_slots)

#     print(f"✅ Classroom CSV files have been saved in '{output_folder}'.")
    
# Predefined time slots mapping

def parse_time(time_slot):
    """Extract start and end times from a time slot string."""
    start_time_str, end_time_str = time_slot.split(" - ")
    start_time = datetime.strptime(start_time_str.strip(), "%I:%M").time()
    end_time = datetime.strptime(end_time_str.strip(), "%I:%M").time()
    return start_time, end_time

def extract_time_slots(timetable,time_slot_order):
    """Extract, sort time slots, and insert BREAK/LUNCH where needed."""
    unique_slots = set()

    # Collect all unique time slots from timetable
    for day_data in timetable.values():
        for slots in day_data.values():
            for entry in slots:
                unique_slots.add(entry["time_slot"])

    # Sort slots based on predefined order
    sorted_slots = sorted(unique_slots, key=lambda slot: time_slot_order[slot])

    # Insert BREAK and LUNCH dynamically based on gaps
    final_slots = []
    last_end_time = None
    break_lunch_counter = 0

    for slot in sorted_slots:
        start_time, end_time = parse_time(slot)

        if last_end_time:
            gap = (datetime.combine(datetime.today(), start_time) - datetime.combine(datetime.today(), last_end_time)).seconds / 60

            if gap > 5:  # If there's a gap greater than 5 minutes
                break_time = f"{last_end_time.strftime('%I:%M')} - {start_time.strftime('%I:%M')}"
                if break_lunch_counter == 0:
                    final_slots.append(("BREAK", break_time))
                elif break_lunch_counter == 1:
                    final_slots.append(("LUNCH", break_time))
                else:
                    final_slots.append(("BREAK", break_time))

                break_lunch_counter += 1  # Increment counter

        final_slots.append(("CLASS", slot))
        last_end_time = end_time  # Update last_end_time

    return final_slots

def json_to_csv(input_folder, json_filename, output_folder,time_slots):
    """Convert JSON timetable to CSV with breaks and lunches inserted."""
    # Reverse lookup to get slot number from time string
    time_slot_order = {v: k for k, v in time_slots.items()}

# List of days in the order we want them to appear
    days_of_week_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
    json_file = os.path.join(input_folder, json_filename)

    with open(json_file, "r", encoding="utf-8") as file:
        timetable = json.load(file)

    sections = set()
    final_slots = extract_time_slots(timetable,time_slot_order)

    os.makedirs(output_folder, exist_ok=True)

    # Identify all sections
    for day_data in timetable.values():
        for section in day_data.keys():
            sections.add(section)

    # Sort days in the correct order
    sorted_days = sorted(timetable.items(), key=lambda x: days_of_week_order.index(x[0]))

    for section in sections:
        csv_file = os.path.join(output_folder, f"{section}.csv")
        header = ["DAY"] + [slot[1] for slot in final_slots]  # Extract only time for header
        rows = []

        # Iterate over sorted days in the correct order
        for day, day_data in sorted_days:  # Sorted days based on days_of_week_order
            # Initialize row with blank spaces
            row = [day] + [""] * len(final_slots)  # Initially empty for each time slot

            if section in day_data:
                for entry in day_data[section]:
                    for i, slot in enumerate(final_slots):
                        # Compare and add the class schedule, BREAK, or LUNCH
                        if entry["time_slot"] == slot[1] and slot[0] == "CLASS":
                            row[i + 1] = f"{entry['subject_id']} ({entry['teacher_id']}, {entry['classroom_id']})"
                        elif slot[0] == "BREAK" or slot[0] == "LUNCH":
                            # Add BREAK and LUNCH to appropriate slots
                            row[i + 1] = slot[0]

            rows.append(row)

        # Write the row into CSV
        with open(csv_file, mode="w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(header)
            writer.writerows(rows)

        print(f"CSV file '{csv_file}' has been created successfully!")

# if __name__ == "__main__":
#     input_folder = os.path.join(os.path.dirname(__file__), "samples")  # ✅ Fixed path
#     json_filename = "tt.json"
#     json_file = os.path.join(input_folder, json_filename)

#     if not os.path.exists(json_file):
#         print(f"❌ Error: {json_file} not found!")
#     else:
#         with open(json_file, "r", encoding="utf-8") as file:
#             tt = json.load(file)

#         output_folder = os.path.join(os.path.dirname(__file__), "samples", "timetable_csvs")
#         os.makedirs(output_folder, exist_ok=True)  # Ensure folder exists

#         time_slots = {
#             1: "9:00 - 9:55",
#             2: "9:55 - 10:50",  # Fixed spacing
#             3: "11:10 - 12:05",  # Fixed spacing
#             4: "12:05 - 1:00",  # Fixed spacing
#             5: "1:20 - 2:15",  # Fixed spacing
#             6: "2:15 - 3:10",  # Fixed spacing
#             7: "3:30 - 4:25"  # Fixed spacing
#         }

#         json_to_csv(input_folder, json_filename, output_folder, time_slots)
        
        
        
