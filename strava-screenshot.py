import time
from datetime import datetime, timedelta
import os
import pyautogui
from mss import mss
import mss.tools
import screeninfo

sleep_time = 15

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
            # Get the first monitor
            monitor = monitors[0]
            return {
                "top": monitor.y,
                "left": monitor.x,
                "width": monitor.width,
                "height": monitor.height
            }
    except Exception as e:
        print(f"Error getting monitor info: {str(e)}")
        return None

def take_strava_screenshot(date_str, monitor_bounds):
    """
    Takes a screenshot of Strava heatmap for a specific date on the specified monitor
    """
    base_url = "https://www.strava.com/maps/personal-heatmap?sport=Run&style=dark&terrain=false&labels=true&poi=false&cPhotos=false&pColor=orange&pCommutes=false&pHidden=true&pDate=2024-01-01_{0}&pPrivate=true&pPhotos=false&pClusters=false#11/59.4254/24.7382"
    
    url = base_url.format(date_str)
    
    try:
        print(f"Processing date {date_str}...")
        print("Focusing URL bar...")
        pyautogui.hotkey('ctrl', 'l')
        
        print("Clearing current URL...")
        pyautogui.hotkey('ctrl', 'a')
        pyautogui.press('delete')
        
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
            # Get the screenshot
            screenshot = sct.grab(monitor_bounds)
            
            filepath = os.path.join('screenshots', filename)
            mss.tools.to_png(screenshot.rgb, screenshot.size, output=filepath)
        
        print(f"Screenshot saved: {filepath}")

        
    except Exception as e:
        print(f"Error processing date {date_str}: {str(e)}")

def generate_date_range(start_date_str, end_date_str):
    """
    Generate a list of dates between start_date and end_date
    """
    start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
    end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
    
    date_list = []
    current_date = start_date
    
    while current_date <= end_date:
        date_list.append(current_date.strftime('%Y-%m-%d'))
        current_date += timedelta(days=1)
    
    return date_list

def main():
    monitor_bounds = get_second_monitor_bounds()
    if monitor_bounds is None:
        print("Error: Could not detect second monitor. Please ensure it's connected.")
        return

    print(f"Detected second monitor bounds: {monitor_bounds}")
    
    print("Script will start in 5 seconds. Please make sure your browser is open on the second monitor...")
    print("DO NOT move your mouse or use keyboard during execution!")
    for i in range(5, 0, -1):
        print(f"Starting in {i} seconds...")
        time.sleep(1)
    
    # Example usage for a date range
    start_date = "2023-01-01"
    end_date = "2023-01-03"  # Change this to your desired end date
    
    dates = generate_date_range(start_date, end_date)
    
    total_dates = len(dates)
    print(f"Estimated time to process each date: {sleep_time + 1} seconds")
    print(f"Total estimated time: {(sleep_time+1)*total_dates} seconds")
    starting_time = datetime.now()
    for index, date in enumerate(dates, 1):
        print(f"\nProcessing {index}/{total_dates}: {date}")
        take_strava_screenshot(date, monitor_bounds)
        print(f"Completed {index}/{total_dates}")
    finishing_time = datetime.now()
    print(f"\nAll dates processed in {finishing_time - starting_time}")

if __name__ == "__main__":
    main()