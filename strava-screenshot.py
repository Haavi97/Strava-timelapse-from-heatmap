import time
from datetime import datetime, timedelta
import os
import pyautogui
from mss import mss
import mss.tools
import screeninfo
import pandas as pd
import re

sleep_time = 30
iteration_time = 1

def get_second_monitor_bounds():
    """
    Get the boundaries of the second monitor
    Returns tuple of (left, top, width, height) or None if not found
    """
    try:
        monitors = screeninfo.get_monitors()
        if len(monitors) >= 2:
            # Get the second monitor
            monitor = monitors[1]
            return {
                "top": monitor.y,
                "left": monitor.x,
                "width": monitor.width,
                "height": monitor.height
            }
        else:
            raise Exception("Second monitor not found")
    except Exception as e:
        print(f"Error getting monitor info: {str(e)}")
        return None

def take_strava_screenshot(date_data, monitor_bounds):
    """
    Takes a screenshot of Strava heatmap for a specific date on the specified monitor
    """
        
    date_str = date_data['date']
    # Base URL template
    base_url = "https://www.strava.com/maps/personal-heatmap?sport=Run&style=dark&terrain=false&labels=false&poi=false&cPhotos=false&pColor=orange&pCommutes=false&pHidden=true&pDate=2024-01-01_{0}&pPrivate=true&pPhotos=false&pClusters=false#10.83/59.4333/24.7447"
    
    # Format URL with date
    url = base_url.format(date_str)
    
    try:
        print(f"Processing date {date_str} (Day {date_data['accumulated_days']}, {date_data['accumulated_distance']:.2f} km)...")
        print("Focusing URL bar...")
        # Press Ctrl+L to focus on URL bar
        pyautogui.hotkey('ctrl', 'l')
        time.sleep(1)  # Increased pause after focusing URL bar
        
        print("Clearing current URL...")
        # Clear the current URL (select all and delete)
        pyautogui.hotkey('ctrl', 'a')
        pyautogui.press('delete')
        time.sleep(0.5)
        
        print("Typing URL...")
        pyautogui.write(url)
        
        print("Pressing Enter...")
        pyautogui.press('enter')
        
        print(f"Waiting {sleep_time} seconds for page to load...")
        time.sleep(sleep_time)
        
        # Format filename (YYYYMMDD.png)
        filename = datetime.strptime(date_str, '%Y-%m-%d').strftime('%Y%m%d') + '.png'
        
        # Create 'screenshots' directory if it doesn't exist
        os.makedirs('screenshots', exist_ok=True)
        
        print("Taking screenshot of second monitor...")
        with mss.mss() as sct:
            screenshot = sct.grab(monitor_bounds)
            
            # Save the screenshot
            filepath = os.path.join('screenshots', filename)
            mss.tools.to_png(screenshot.rgb, screenshot.size, output=filepath)
        
        print(f"Screenshot saved: {filepath}")
        
        # Wait between screenshots
        print(f"Waiting {iteration_time} seconds before next iteration...")
        time.sleep(iteration_time)
        
    except Exception as e:
        print(f"Error processing date {date_str}: {str(e)}")

def load_tallinn_streets_data(csv_file="TallinnStreets.csv"):
    """
    Load CSV data and filter for Tallinn Streets activities
    Returns list of activity dates and their distances
    """
    try:
        # First try pandas with different parameters
        df = pd.read_csv(csv_file, engine='python', on_bad_lines='skip', quotechar='"')
        
        print(f"Loaded CSV with {len(df)} total activities")
        print(f"Columns found: {list(df.columns[:5])}...")
        
        if 'Activity Name' in df.columns:
            tallinn_activities = df[df['Activity Name'].str.contains('Tallinn Streets', na=False, case=False)]
            
            if len(tallinn_activities) > 0:
                print(f"Found {len(tallinn_activities)} activities with 'Tallinn Streets' in the name")
                
                # Process pandas results
                activities_data = []
                for _, row in tallinn_activities.iterrows():
                    try:
                        # Parse date
                        date_str = str(row['Activity Date']).strip().strip('"')
                        date_obj = pd.to_datetime(date_str, format='%b %d, %Y, %I:%M:%S %p')
                        formatted_date = date_obj.strftime('%Y-%m-%d')
                        
                        # Parse distance
                        distance = float(row['Distance']) if pd.notna(row['Distance']) else 0
                        
                        activities_data.append({
                            'date': formatted_date,
                            'distance': distance,
                            'name': str(row['Activity Name'])
                        })
                    except Exception as e:
                        print(f"Error processing pandas row: {e}")
                        continue
                
                if activities_data:
                    activities_data.sort(key=lambda x: x['date'])
                    print(f"Processed {len(activities_data)} Tallinn Streets activities:")
                    for activity in activities_data:
                        print(f"  {activity['date']}: {activity['distance']:.2f} km - {activity['name']}")
                    return activities_data
        
        print("Pandas parsing failed or no results, trying manual parsing...")
        
    except Exception as e:
        print(f"Pandas parsing failed: {str(e)}")
        print("Attempting manual CSV parsing...")
    
    # Manual parsing for complex CSV structure
    activities_data = []
    
    with open(csv_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Split by lines but be aware that entries can span multiple lines
    lines = content.split('\n')
    print(f"Processing {len(lines)} lines manually...")
    
    current_entry = ""
    in_entry = False
    
    for i, line in enumerate(lines):
        # Skip empty lines
        if not line.strip():
            continue
            
        # Check if this is the start of a new entry (starts with quote and ID)
        if re.match(r'^"?\d+,', line.strip()):
            # Process previous entry if we were building one
            if current_entry and 'Tallinn Streets' in current_entry:
                activities_data.extend(parse_single_entry(current_entry, i))
            
            # Start new entry
            current_entry = line
            in_entry = True
        else:
            # This is a continuation of the current entry
            if in_entry:
                current_entry += "\n" + line
    
    # Process the last entry
    if current_entry and 'Tallinn Streets' in current_entry:
        activities_data.extend(parse_single_entry(current_entry, len(lines)))
    
    # Sort by date
    activities_data.sort(key=lambda x: x['date'])
    
    print(f"\nManual parsing completed. Found {len(activities_data)} Tallinn Streets activities:")
    for activity in activities_data:
        print(f"  {activity['date']}: {activity['distance']:.2f} km - {activity['name']}")
    
    return activities_data

def parse_single_entry(entry_text, line_num):
    """
    Parse a single CSV entry that may span multiple lines
    """
    try:
        print(f"\nProcessing entry around line {line_num} with Tallinn Streets activity...")
        
        # Extract date - look for the pattern ""Date""
        date_pattern = r'""([^"]+)""'
        date_match = re.search(date_pattern, entry_text)
        
        if not date_match:
            print(f"  Could not extract date from entry")
            return []
        
        date_str = date_match.group(1)
        print(f"  Found date: {date_str}")
        
        # Parse date
        try:
            date_obj = datetime.strptime(date_str, '%b %d, %Y, %I:%M:%S %p')
            formatted_date = date_obj.strftime('%Y-%m-%d')
            print(f"  Parsed date: {formatted_date}")
        except Exception as e:
            print(f"  Could not parse date '{date_str}': {e}")
            return []
        
        # Extract activity name
        name_patterns = [
            r'(Tallinn Streets[^,]*)',
            r'(Survival Morning Run - Tallinn Streets[^,]*)',
            r'([^,]*Tallinn Streets[^,]*)'
        ]
        
        activity_name = "Tallinn Streets Activity"
        for pattern in name_patterns:
            name_match = re.search(pattern, entry_text)
            if name_match:
                activity_name = name_match.group(1).strip()
                break
        
        print(f"  Activity name: {activity_name}")
        
        # Extract distance - look for decimal numbers after the activity name
        # Use a more robust approach: split by commas and look for reasonable distances
        
        # First, let's try to split the entry into fields using CSV parsing
        try:
            import csv
            from io import StringIO
            
            # Clean the entry for CSV parsing
            cleaned_entry = entry_text.replace('\n', ' ').replace('\r', '')
            
            csv_reader = csv.reader(StringIO(cleaned_entry), quotechar='"')
            fields = next(csv_reader)
            
            # Distance is typically in field 6 (0-indexed)
            if len(fields) > 6:
                try:
                    distance = float(fields[6])
                    print(f"  Found distance in field 6: {distance} km")
                    
                    return [{
                        'date': formatted_date,
                        'distance': distance,
                        'name': activity_name
                    }]
                except ValueError:
                    print(f"  Field 6 is not a valid distance: {fields[6]}")
            
        except Exception as e:
            print(f"  CSV parsing failed: {e}")
        
        # Fallback: look for decimal patterns
        decimal_pattern = r'(?:^|,)([0-9]+\.[0-9]+)(?=,|$)'
        decimal_matches = re.findall(decimal_pattern, entry_text.replace('\n', ' '))
        
        if decimal_matches:
            print(f"  Found decimal numbers: {decimal_matches[:5]}")
            
            # Filter for reasonable distance values
            potential_distances = []
            for d in decimal_matches:
                try:
                    val = float(d)
                    if 0.1 <= val <= 100:
                        potential_distances.append(val)
                except ValueError:
                    continue
            
            if potential_distances:
                distance = potential_distances[0]
                print(f"  Selected distance: {distance} km")
            else:
                distance = 0
                print(f"  No reasonable distance found, using 0")
        else:
            distance = 0
            print(f"  No decimal numbers found, using 0")
        
        return [{
            'date': formatted_date,
            'distance': distance,
            'name': activity_name
        }]
        
    except Exception as e:
        print(f"  Error processing entry: {str(e)}")
        return []
    
def parse_csv_manually(csv_file):
    """
    Manual CSV parsing as fallback for complex CSV structure
    """
    activities_data = []
    
    with open(csv_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    lines = content.split('\n')
    print(f"Processing {len(lines)} lines manually...")
    
    i = 0
    while i < len(lines):
        line = lines[i]
        if 'Tallinn Streets' in line and i > 0:  # Skip header
            try:
                print(f"\nProcessing line {i + 1} with Tallinn Streets activity...")
                
                # Extract date - it's between the first set of double quotes after the ID
                # Pattern: "ID,""Date"",Name...
                date_pattern = r'""([^"]+)""'
                date_match = re.search(date_pattern, line)
                
                if not date_match:
                    print(f"  Could not extract date from line {i + 1}")
                    i += 1
                    continue
                
                date_str = date_match.group(1)
                print(f"  Found date: {date_str}")
                
                # Parse date
                try:
                    date_obj = datetime.strptime(date_str, '%b %d, %Y, %I:%M:%S %p')
                    formatted_date = date_obj.strftime('%Y-%m-%d')
                    print(f"  Parsed date: {formatted_date}")
                except Exception as e:
                    print(f"  Could not parse date '{date_str}': {e}")
                    i += 1
                    continue
                
                # Extract activity name - find "Tallinn Streets" and get the full name
                name_patterns = [
                    r'(Tallinn Streets[^,]*)',
                    r'(Survival Morning Run - Tallinn Streets[^,]*)',
                    r'([^,]*Tallinn Streets[^,]*)'
                ]
                
                activity_name = "Tallinn Streets Activity"
                for pattern in name_patterns:
                    name_match = re.search(pattern, line)
                    if name_match:
                        activity_name = name_match.group(1)
                        break
                
                print(f"  Activity name: {activity_name}")
                
                # Extract distance - first check current line
                name_end = line.find(activity_name) + len(activity_name)
                remaining_line = line[name_end:]
                
                # Look for decimal numbers that could be distance
                decimal_pattern = r',([0-9]+\.[0-9]+),'
                decimal_matches = re.findall(decimal_pattern, remaining_line)
                
                # If no distance found on current line, check next line (for split entries)
                if not decimal_matches and i + 1 < len(lines):
                    next_line = lines[i + 1]
                    if not next_line.strip().startswith('"'):  # Not a new entry
                        print(f"  Checking continuation on line {i + 2}...")
                        decimal_matches = re.findall(decimal_pattern, next_line)
                        remaining_line = next_line
                
                if decimal_matches:
                    print(f"  Found decimal numbers: {decimal_matches[:5]}")
                    
                    # Filter for reasonable distance values (0.1 to 100 km)
                    potential_distances = []
                    for d in decimal_matches:
                        val = float(d)
                        if 0.1 <= val <= 100:
                            potential_distances.append(val)
                    
                    if potential_distances:
                        distance = potential_distances[0]  # Take the first reasonable one
                        print(f"  Selected distance: {distance} km")
                    else:
                        distance = 0
                        print(f"  No reasonable distance found, using 0")
                else:
                    distance = 0
                    print(f"  No decimal numbers found, using 0")
                
                activities_data.append({
                    'date': formatted_date,
                    'distance': distance,
                    'name': activity_name
                })
                
                print(f"  Successfully parsed: {formatted_date}, {distance} km, '{activity_name}'")
                
            except Exception as e:
                print(f"  Error processing line {i + 1}: {str(e)}")
        
        i += 1
    
    # Sort by date
    activities_data.sort(key=lambda x: x['date'])
    
    print(f"\nManual parsing completed. Found {len(activities_data)} Tallinn Streets activities:")
    for activity in activities_data:
        print(f"  {activity['date']}: {activity['distance']:.2f} km - {activity['name']}")
    
    return activities_data

def generate_screenshot_dates(activities_data, start_date="2024-01-01"):
    """
    Generate dates from start_date to each activity date
    """
    if not activities_data:
        return []
    
    start_dt = datetime.strptime(start_date, '%Y-%m-%d')
    screenshot_dates = []
    
    for activity in activities_data:
        activity_dt = datetime.strptime(activity['date'], '%Y-%m-%d')
        
        # Generate all dates from start_date to activity_date
        current_dt = start_dt
        while current_dt <= activity_dt:
            date_str = current_dt.strftime('%Y-%m-%d')
            if date_str not in [d['date'] for d in screenshot_dates]:
                # Calculate accumulated distance and days up to this date
                accumulated_distance = sum(
                    act['distance'] for act in activities_data 
                    if datetime.strptime(act['date'], '%Y-%m-%d') <= current_dt
                )
                accumulated_days = len([
                    act for act in activities_data 
                    if datetime.strptime(act['date'], '%Y-%m-%d') <= current_dt
                ])
                
                screenshot_dates.append({
                    'date': date_str,
                    'accumulated_distance': accumulated_distance,
                    'accumulated_days': accumulated_days
                })
            current_dt += timedelta(days=1)
    
    return screenshot_dates

def main():
    # Load Tallinn Streets data from CSV
    activities_data = load_tallinn_streets_data()
    if not activities_data:
        print("No Tallinn Streets activities found or error loading CSV. Exiting.")
        return
    
    # Generate screenshot dates
    screenshot_dates = generate_screenshot_dates(activities_data)
    if not screenshot_dates:
        print("No dates to process. Exiting.")
        return
    
    # Get second monitor bounds
    monitor_bounds = get_second_monitor_bounds()
    if monitor_bounds is None:
        print("Error: Could not detect second monitor. Please ensure it's connected.")
        return

    print(f"Detected second monitor bounds: {monitor_bounds}")
    
    # Save screenshot metadata for video creation
    import json
    metadata = {
        'screenshot_dates': screenshot_dates,
        'activities_data': activities_data
    }
    with open('screenshot_metadata.json', 'w') as f:
        json.dump(metadata, f, indent=2)
    print("Saved screenshot metadata for video creation")
    
    # Add a safety pause before starting
    print(f"\nScript will process {len(screenshot_dates)} screenshots...")
    print("Script will start in 5 seconds. Please make sure your browser is open on the second monitor...")
    print("DO NOT move your mouse or use keyboard during execution!")
    for i in range(5, 0, -1):
        print(f"Starting in {i} seconds...")
        time.sleep(1)
    
    total_dates = len(screenshot_dates)
    for index, date_data in enumerate(screenshot_dates, 1):
        print(f"\nProcessing {index}/{total_dates}")
        take_strava_screenshot(date_data, monitor_bounds)
        print(f"Completed {index}/{total_dates}")

if __name__ == "__main__":
    main()