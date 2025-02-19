import csv
import io
import json


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


def json_to_csv(json_file, csv_file):
    with open(json_file, "r", encoding="utf-8") as file:
        timetable = json.load(file)

    time_slots = set()
    for day in timetable.values():
        for entry in day:
            time_slots.add(entry["time_slot"])
    time_slots = sorted(time_slots)

    header = ["DAY \\ TIME"] + time_slots
    rows = []

    for day, slots in timetable.items():
        subjects_row = [day] + [""] * len(time_slots)
        teachers_row = [""] + [""] * len(time_slots)

        for entry in slots:
            index = time_slots.index(entry["time_slot"]) + 1
            subjects_row[index] = entry["subject_id"]
            teachers_row[index] = entry["teacher_id"]

        rows.append(subjects_row)
        rows.append(teachers_row)

    with open(csv_file, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(header)
        writer.writerows(rows)
