import cv2
import numpy as np
from pathlib import Path
import re
from datetime import datetime

def create_video_from_images(
    input_folder="cropped_screenshots",
    output_filename="timelapse.mp4",
    fps=3,
    date_format="%Y-%m-%d"
):
    """
    Create a video from PNG images with date overlay
    
    Args:
    input_folder: Folder containing the cropped screenshots
    output_filename: Name of the output video file
    fps: Frames per second for the video
    date_format: Format to display the date
    """
    input_path = Path(input_folder)
    png_files = sorted(list(input_path.glob("*.png")))
    
    if not png_files:
        print(f"No PNG files found in {input_folder}")
        return
    
    print(f"Found {len(png_files)} images")
    
    # Read first image to get dimensions
    first_image = cv2.imread(str(png_files[0]))
    height, width = first_image.shape[:2]
    
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    video_writer = cv2.VideoWriter(
        output_filename,
        fourcc,
        fps,
        (width, height)
    )
    
    # Font settings for date overlay
    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = height / 1000  # Scale font based on image height
    font_thickness = max(1, int(height / 500))
    font_color = (255, 255, 255)  
    
    for i, image_path in enumerate(png_files, 1):
        print(f"Processing image {i}/{len(png_files)}: {image_path.name}")
        
        image = cv2.imread(str(image_path))
        
        # Extract date from filename (expecting YYYYMMDD format)
        date_str = re.search(r'(\d{8})', image_path.stem)
        if date_str:
            date_obj = datetime.strptime(date_str.group(1), '%Y%m%d')
            display_date = date_obj.strftime(date_format)
            
            text_size = cv2.getTextSize(
                display_date,
                font,
                font_scale,
                font_thickness
            )[0]
            
            padding = 20
            text_x = width - text_size[0] - padding
            text_y = height - padding
            
            # Add dark background for better readability
            # Create a rectangle behind the text
            rect_pad = 5
            rect_start = (
                text_x - rect_pad,
                text_y + rect_pad
            )
            rect_end = (
                text_x + text_size[0] + rect_pad,
                text_y - text_size[1] - rect_pad
            )
            
            # Draw semi-transparent background
            overlay = image.copy()
            cv2.rectangle(
                overlay,
                rect_start,
                rect_end,
                (0, 0, 0),
                -1
            )
            # Apply the overlay with transparency
            alpha = 0.6
            image = cv2.addWeighted(overlay, alpha, image, 1 - alpha, 0)
            
            # Add text
            cv2.putText(
                image,
                display_date,
                (text_x, text_y),
                font,
                font_scale,
                font_color,
                font_thickness,
                cv2.LINE_AA
            )
        
        # Write frame to video
        video_writer.write(image)
    
    # Release video writer
    video_writer.release()
    print(f"\nVideo created successfully: {output_filename}")

def main():
    print("Starting video creation process...")
    
    # Verify input folder exists
    if not os.path.exists("cropped_screenshots"):
        print("Error: 'cropped_screenshots' folder not found!")
        return
    
    # Create video with default settings
    create_video_from_images(
        fps=3,  
        date_format="%B %d, %Y"  # e.g., "January 01, 2024"
    )
    
if __name__ == "__main__":
    import os
    main()
