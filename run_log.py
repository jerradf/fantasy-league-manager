import os
from datetime import datetime
from pathlib import Path

def write_run_log(lines, base_dir="logs/2026/sleeper"):
    # Build the filename from the current local time formatted %Y-%m-%d_%H%M plus .md
    timestamp = datetime.now().strftime("%Y-%m-%d_%H%M")
    filename = f"{timestamp}.md"
    
    # Create base_dir with os.makedirs(..., exist_ok=True)
    full_path = Path(base_dir) / filename
    os.makedirs(full_path.parent, exist_ok=True)
    
    # Write a Markdown file whose first line is "# Run log" followed by the time, then each string in lines on its own line
    with open(full_path, 'w') as file:
        file.write("# Run log\n")
        file.write(f"{datetime.now()}\n")
        for line in lines:
            file.write(f"{line}\n")
    
    # Return the full path as a pathlib.Path
    return full_path
