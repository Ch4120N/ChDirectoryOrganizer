import os
from datetime import datetime
from pathlib import Path

def create_test_file(name: str, year: int, month: int, day: int,
                     hour: int = 0, minute: int = 0, second: int = 0,
                     directory: str = "."):
    """
    Create an empty file and set its modification time to the given date/time.
    """
    if not os.path.exists(directory):
        os.makedirs(directory, exist_ok=True)
    dest = Path(directory) / name
    dest.touch(exist_ok=True)               # create empty file
    
    # Build a datetime object and convert to timestamp
    dt = datetime(year, month, day, hour, minute, second)
    timestamp = dt.timestamp()
    
    os.utime(dest, (timestamp, timestamp))  # set access and modification time
    print(f"[*] Created {dest}  ->  {dt.strftime('%Y-%m-%d %H:%M')}")

# 3 files from 2/23/2026, times 11:00, 11:30, 11:59
create_test_file("doc1.txt", 2026, 2, 23, 11,  0, directory="samples")
create_test_file("doc2.txt", 2026, 2, 23, 11, 30, directory="samples")
create_test_file("doc3.txt", 2026, 2, 23, 11, 59, directory="samples")

# 7 files from 4/23/2026, times ranging from 11:00 to 12:36
create_test_file("report_A.txt", 2026, 4, 23, 11,  40, directory="samples")
create_test_file("report_B.txt", 2026, 4, 23, 11, 45, directory="samples")
create_test_file("report_C.txt", 2026, 4, 23, 12, 10, directory="samples")
create_test_file("report_D.txt", 2026, 4, 23, 12, 20, directory="samples")
create_test_file("report_E.txt", 2026, 4, 23, 12, 30, directory="samples")
create_test_file("report_F.txt", 2026, 4, 23, 12, 35, directory="samples")
create_test_file("report_G.txt", 2026, 4, 23, 12, 36, directory="samples")

# and Other files
create_test_file("doc2_1.txt", 2026, 4, 29, 11,  0, directory="samples")
create_test_file("doc2_2.txt", 2026, 4, 29, 11, 30, directory="samples")
create_test_file("doc2_3.txt", 2026, 4, 29, 2, 32, directory="samples")
create_test_file("doc2_4.txt", 2026, 4, 29, 12, 36, directory="samples")
create_test_file("doc2_5.txt", 2026, 4, 29, 12, 37, directory="samples")

create_test_file("doc3_1.txt", 2025, 4, 29, 11,  0, directory="samples")
create_test_file("doc3_2.txt", 2025, 4, 29, 11, 30, directory="samples")
create_test_file("doc3_3.txt", 2025, 4, 29, 5, 59, directory="samples")
create_test_file("doc3_4.txt", 2025, 4, 29, 12, 36, directory="samples")
create_test_file("doc3_5.txt", 2025, 4, 29, 12, 37, directory="samples")