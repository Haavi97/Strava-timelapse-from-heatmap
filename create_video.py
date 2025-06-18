import cv2
import numpy as np
from pathlib import Path
import re
from datetime import datetime
import json

def filter_unique_activities(screenshot_metadata):
    """
    Filter screenshots to only include those where the day number increases
    (i.e., where a new Tallinn Streets activity was completed)
    """
    if not screenshot_metadata:
        return []
    
    # Sort by date to ensure proper order
    screenshot_metadata.sort(key=lambda x: x['date'])
    
    filtered_screenshots = []
    last_day_count = 0
    
    for screenshot in screenshot_metadata:
        current_day_count = screenshot['accumulated_days']
        
        # Only include if this represents a new activity (day count increased)
        if current_day_count > last_day_count:
            filtered_screenshots.append(screenshot)
            last_day_count = current_day_count
            print(f"  Including: {screenshot['date']} - Day {current_day_count}, {screenshot['accumulated_distance']:.2f} km")
        else:
            print(f"  Skipping: {screenshot['date']} - Day {current_day_count}, {screenshot['accumulated_distance']:.2f} km (no new activity)")
    
    print(f"\nFiltered from {len(screenshot_metadata)} to {len(filtered_screenshots)} screenshots")
    return filtered_screenshots

def load_screenshot_metadata():
    """
    Load metadata about screenshots for Tallinn Streets activities only
    """
    try:
        with open('screenshot_metadata.json', 'r') as f:
            metadata = json.load(f)
        
        # Get the screenshot dates
        screenshot_dates = metadata.get('screenshot_dates', [])
        
        print(f"Loaded metadata for {len(screenshot_dates)} total screenshots")
        
        # Filter to only include screenshots where day count increases
        print("Filtering for unique activities only...")
        filtered_dates = filter_unique_activities(screenshot_dates)
        
        return filtered_dates
        
    except Exception as e:
        print(f"Warning: Could not load screenshot metadata: {e}")
        return None

def create_video_from_images(
    input_folder="cropped_screenshots",
    output_filename="timelapse.mp4",
    fps=2,
    date_format="%Y-%m-%d"
):
    """
    Create a video from PNG images with date overlay and accumulated stats
    Only processes screenshots for dates where new activities occurred
    
    Args:
    input_folder: Folder containing the cropped screenshots
    output_filename: Name of the output video file
    fps: Frames per second for the video
    date_format: Format to display the date
    """
    # Load metadata for accumulated stats (filtered for unique activities only)
    screenshot_metadata = load_screenshot_metadata()
    
    if not screenshot_metadata:
        print("No screenshot metadata available. Processing all images without overlays.")
        screenshot_metadata = []
    
    # Get list of PNG files that correspond to our filtered metadata
    input_path = Path(input_folder)
    
    # Create a set of dates we want to process
    target_dates = set()
    metadata_lookup = {}
    
    for meta in screenshot_metadata:
        # Convert date to filename format (YYYYMMDD)
        date_obj = datetime.strptime(meta['date'], '%Y-%m-%d')
        filename_date = date_obj.strftime('%Y%m%d')
        target_dates.add(filename_date + '.png')
        metadata_lookup[filename_date + '.png'] = meta
    
    # Get all PNG files and filter for only the ones we want
    all_png_files = list(input_path.glob("*.png"))
    png_files = [f for f in all_png_files if f.name in target_dates]
    png_files = sorted(png_files)  # Sort by filename (which is date-based)
    
    if not png_files:
        print(f"No PNG files found in {input_folder} for the filtered dates")
        print(f"Looking for files: {sorted(target_dates)}")
        print(f"Available files: {sorted([f.name for f in all_png_files])}")
        return
    
    print(f"Processing {len(png_files)} images (filtered from {len(all_png_files)} total)")
    for png_file in png_files:
        meta = metadata_lookup.get(png_file.name, {})
        print(f"  Will process: {png_file.name} - Day {meta.get('accumulated_days', '?')}, {meta.get('accumulated_distance', 0):.2f} km")
    
    # Read first image to get dimensions
    first_image = cv2.imread(str(png_files[0]))
    height, width = first_image.shape[:2]
    
    # Initialize video writer
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    video_writer = cv2.VideoWriter(
        output_filename,
        fourcc,
        fps,
        (width, height)
    )
    
    # Font settings for overlays
    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = height / 1000  # Scale font based on image height
    font_thickness = max(1, int(height / 500))
    font_color = (255, 255, 255)  # White color
    
    days = 0
    # Process each image
    for i, image_path in enumerate(png_files, 1):
        print(f"Processing image {i}/{len(png_files)}: {image_path.name}")
        
        # Read image
        image = cv2.imread(str(image_path))
        
        # Get metadata for this image
        meta = metadata_lookup.get(image_path.name, {})
        
        # Extract date from filename (expecting YYYYMMDD format)
        date_match = re.search(r'(\d{8})', image_path.stem)
        if date_match:
            date_str = date_match.group(1)
            # Convert to desired display format
            date_obj = datetime.strptime(date_str, '%Y%m%d')
            display_date = date_obj.strftime(date_format)
            
            # Get accumulated stats from metadata
            accumulated_distance = meta.get('accumulated_distance', 0)
            accumulated_days = meta.get('accumulated_days', 0)
            days += 1
            
            # Prepare overlay texts
            date_text = display_date
            distance_text = f"{accumulated_distance:.1f} km"
            days_text = f"Day {days}" if days > 0 else "Day 0"
            
            # Calculate positions and sizes for all texts
            
            # Date overlay (bottom right)
            date_size = cv2.getTextSize(date_text, font, font_scale, font_thickness)[0]
            date_padding = 20
            date_x = width - date_size[0] - date_padding
            date_y = height - date_padding
            
            # Distance overlay (bottom left)
            distance_size = cv2.getTextSize(distance_text, font, font_scale, font_thickness)[0]
            distance_x = date_padding
            distance_y = height - date_padding
            
            # Days overlay (above distance, bottom left)
            days_size = cv2.getTextSize(days_text, font, font_scale, font_thickness)[0]
            days_x = date_padding
            days_y = height - date_padding - distance_size[1] - 10  # 10px gap between texts
            
            # Create overlay with semi-transparent backgrounds
            overlay = image.copy()
            alpha = 0.6
            rect_pad = 5
            
            # Background for date (bottom right)
            date_rect_start = (date_x - rect_pad, date_y + rect_pad)
            date_rect_end = (date_x + date_size[0] + rect_pad, date_y - date_size[1] - rect_pad)
            cv2.rectangle(overlay, date_rect_start, date_rect_end, (0, 0, 0), -1)
            
            # Background for distance (bottom left)
            distance_rect_start = (distance_x - rect_pad, distance_y + rect_pad)
            distance_rect_end = (distance_x + distance_size[0] + rect_pad, distance_y - distance_size[1] - rect_pad)
            cv2.rectangle(overlay, distance_rect_start, distance_rect_end, (0, 0, 0), -1)
            
            # Background for days (above distance)
            days_rect_start = (days_x - rect_pad, days_y + rect_pad)
            days_rect_end = (days_x + days_size[0] + rect_pad, days_y - days_size[1] - rect_pad)
            cv2.rectangle(overlay, days_rect_start, days_rect_end, (0, 0, 0), -1)
            
            # Apply the overlay with transparency
            image = cv2.addWeighted(overlay, alpha, image, 1 - alpha, 0)
            
            # Add all text overlays
            cv2.putText(image, date_text, (date_x, date_y), font, font_scale, font_color, font_thickness, cv2.LINE_AA)
            cv2.putText(image, distance_text, (distance_x, distance_y), font, font_scale, font_color, font_thickness, cv2.LINE_AA)
            cv2.putText(image, days_text, (days_x, days_y), font, font_scale, font_color, font_thickness, cv2.LINE_AA)
        
        # Write frame to video
        video_writer.write(image)
    
    # Release video writer
    video_writer.release()
    print(f"\nVideo created successfully: {output_filename}")
    print(f"Video contains {len(png_files)} frames showing progression through Tallinn Streets activities")

def main():
    print("Starting video creation process...")
    
    # Verify input folder exists
    if not os.path.exists("cropped_screenshots"):
        print("Error: 'cropped_screenshots' folder not found!")
        return
    
    # Create video with default settings
    create_video_from_images(
        fps=3,  # 2 frames per second
        date_format="%B %d, %Y"  # e.g., "January 01, 2024"
    )
    
if __name__ == "__main__":
    import os
    main()