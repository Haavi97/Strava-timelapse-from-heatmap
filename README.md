# Strava Heatmap Timelapse Generator

This project contains a set of Python scripts to automatically create a timelapse video from Strava heatmaps. The process involves three main steps:
1. Capturing screenshots from Strava
2. Cropping the screenshots to focus on the map
3. Creating a timelapse video with date overlays

## Prerequisites

- Python 3.6 or higher
- Web browser
- Active Strava account (must be logged in before running the scripts)
- Multiple monitors setup (script uses second monitor for captures)

## Installation

1. Clone this repository or download the script files:
```bash
git clone [url]
cd strava-heatmap-timelapse
```

2. Create a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows, use: venv\Scripts\activate
```

3. Install required packages:
```bash
pip install -r requirements.txt
```

## Project Structure

```
strava-heatmap-timelapse/
├── strava_screenshot.py
├── image_cropper.py
├── create_video.py
├── requirements.txt
├── README.md
├── screenshots/
│   ├── YYYYMMDD.png
│   └── ...
├── cropped_screenshots/
│   ├── YYYYMMDD.png
│   └── ...
└── timelapse.mp4
```

## Usage

### 1. Capture Screenshots (strava_screenshot.py)

This script automates the process of capturing Strava heatmap screenshots:

```bash
python strava_screenshot.py
```

Features:
- Automatically navigates to Strava heatmap URLs
- Captures screenshots from second monitor
- Saves dated screenshots (YYYYMMDD.png format)
- Handles multiple dates automatically

Safety Notes:
- Don't move mouse or use keyboard while script is running
- Keep browser window active on second monitor
- Ensure you're logged into Strava before starting

### 2. Crop Screenshots (image_cropper.py)

This script provides a GUI to select crop area and applies it to all screenshots:

```bash
python image_cropper.py
```

Features:
- Visual selection interface
- Real-time coordinate display
- Batch processing of all screenshots
- Preserves original files

Usage:
1. Click and drag to select crop area
2. Use buttons or keyboard shortcuts:
   - Enter: Confirm selection
   - R: Reset selection
3. Original images are preserved, cropped versions saved to new folder

### 3. Create Timelapse (create_video.py)

This script combines the cropped images into a video with date overlays:

```bash
python create_video.py
```

Features:
- Creates MP4 video from screenshots
- Adds date overlay to bottom right
- Semi-transparent background for date
- Configurable FPS and date format

## Customization

### Screenshot Script
- Modify `start_date` and `end_date` in main()
- Adjust sleep times if needed
- Change URL parameters for different map styles

### Cropping Script
- Adjust window size handling
- Modify selection tool colors
- Change output folder name

### Video Creation
- Adjust FPS (default: 3)
- Change date format
- Modify text position and style
- Adjust background opacity

## Troubleshooting

1. Screenshot Issues:
   - Ensure second monitor is properly detected
   - Check if browser is active window
   - Verify Strava login status
   - Try increasing sleep times

2. Cropping Issues:
   - Make sure screenshots folder exists
   - Check if images are readable
   - Verify sufficient disk space

3. Video Creation Issues:
   - Verify cropped_screenshots folder exists
   - Check if all images are properly named
   - Ensure sufficient memory for video creation

## Contributing

Feel free to open issues or submit pull requests if you have suggestions for improvements.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Notes

- The scripts assume a consistent monitor setup
- Screenshots are taken from the second monitor
- Files are processed in alphabetical order
- Dates are extracted from filenames
- Original files are preserved at each step

## Dependencies

Main dependencies (see requirements.txt for versions):
- pyautogui: For screen control
- Pillow: Image processing
- mss: Screen capture
- opencv-python: Video creation
- screeninfo: Monitor detection
- numpy: Image processing