# Strava Heatmap Timelapse Generator

This project contains a set of Python scripts to automatically create a timelapse video from Strava heatmaps based on activities from a CSV export. The process involves three main steps:
1. Reading Strava activities from CSV and capturing screenshots for relevant dates
2. Cropping the screenshots to focus on the map
3. Creating a timelapse video with date overlays and accumulated statistics

## Prerequisites

- Python 3.6 or higher
- Web browser
- Active Strava account (must be logged in before running the scripts)
- Multiple monitors setup (script uses second monitor for captures)
- Strava data export CSV file named `TallinnStreets.csv`

## CSV File Requirements

The script expects a CSV file named `TallinnStreets.csv` with your Strava activity data. The script will:
- Filter activities containing "Tallinn Streets" in the Activity Name
- Use these activities to determine screenshot dates
- Calculate accumulated distance and days for video overlays

Required CSV columns: `Activity Date`, `Activity Name`, `Distance`

## Installation

1. Clone this repository or download the script files:
```bash
git clone [your-repository-url]
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

4. Place your `TallinnStreets.csv` file in the project directory

## Project Structure

```
strava-heatmap-timelapse/
├── TallinnStreets.csv (your CSV file)
├── strava_screenshot.py
├── image_cropper.py
├── create_video.py
├── requirements.txt
├── README.md
├── screenshot_metadata.json (generated)
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

This script reads your CSV file and captures screenshots from 2024-01-01 to each activity date:

```bash
python strava-screenshot.py
```

Features:
- Reads `TallinnStreets.csv` and filters for activities containing "Tallinn Streets"
- Generates screenshots from start date to each activity date
- Captures screenshots from second monitor
- Saves dated screenshots and metadata for video creation
- Shows progress with accumulated distance and days

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

### 3. Create Timelapse (create_video.py)

This script combines the cropped images into a video with multiple overlays:

```bash
python create_video.py
```

Features:
- Creates MP4 video from screenshots
- Date overlay (bottom right)
- Accumulated distance overlay (bottom left)
- Accumulated days overlay (above distance)
- Semi-transparent backgrounds for all overlays
- Uses metadata from screenshot capture process
## Customization

### Screenshot Script
- CSV file location: Change the filename in `load_tallinn_streets_data()`
- Activity filter: Modify the string filter in the CSV processing
- Start date: Change the default start date in `generate_screenshot_dates()`
- URL parameters: Adjust map style, zoom level in the base URL

### Cropping Script
- Window size handling: Adjust scaling factors
- Selection tool colors: Modify rectangle outline color
- Output folder: Change the output directory name

### Video Creation
- FPS: Adjust video speed (default: 2)
- Date format: Change date display format
- Overlay positions: Modify text positioning
- Font settings: Adjust size, thickness, color
- Background opacity: Change transparency level

## Data Flow

1. **CSV Processing**: Script reads `TallinnStreets.csv` and filters activities
2. **Date Generation**: Creates screenshot dates from start date to each activity
3. **Metadata Creation**: Saves `screenshot_metadata.json` with accumulated stats
4. **Screenshot Capture**: Takes screenshots for each date
5. **Image Cropping**: Processes all screenshots with consistent crop
6. **Video Creation**: Combines images with overlays using metadata

## Troubleshooting

1. **CSV Issues**:
   - Ensure file is named exactly `TallinnStreets.csv`
   - Check that Activity Name column contains "Tallinn Streets" entries
   - Verify Date and Distance columns are properly formatted

2. **Screenshot Issues**:
   - Ensure second monitor is properly detected
   - Check if browser is active window on second monitor
   - Verify Strava login status
   - Try increasing sleep times if pages load slowly

3. **Video Creation Issues**:
   - Ensure `screenshot_metadata.json` exists (created by screenshot script)
   - Check if cropped_screenshots folder exists and contains images
   - Verify all images are properly named (YYYYMMDD.png format)

## Output Information

The final video will display:
- **Bottom Right**: Date of the screenshot
- **Bottom Left**: Accumulated kilometers from all "Tallinn Streets" activities up to that date
- **Above Distance**: Day number (number of activities completed)

## Example Workflow

1. Export your Strava data and save as `TallinnStreets.csv`
2. Run screenshot script: captures all relevant dates
3. Run cropping script: select map area once, applies to all
4. Run video script: creates timelapse with statistics

## Dependencies

Main dependencies (see requirements.txt for versions):
- pandas: CSV data processing
- pyautogui: Screen control and automation
- Pillow: Image processing
- mss: Multi-monitor screen capture
- opencv-python: Video creation and overlay rendering
- screeninfo: Monitor detection
- numpy: Numerical operations

## Contributing

Feel free to open issues or submit pull requests if you have suggestions for improvements.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Notes

- The scripts assume your activities contain "Tallinn Streets" in the name
- Screenshots are taken from the second monitor
- Files are processed in chronological order
- Metadata is preserved between scripts for accurate statistics
- Original files are preserved at each step