import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import os
from pathlib import Path

class CropSelector:
    def __init__(self, image_path):
        self.root = tk.Tk()
        self.root.title("Crop Selector")
        
        # Load the image
        self.image = Image.open(image_path)
        # Resize if the image is too large for screen
        screen_width = self.root.winfo_screenwidth() - 100
        screen_height = self.root.winfo_screenheight() - 100
        
        # Calculate scale factor if image needs to be resized
        width_ratio = screen_width / self.image.width
        height_ratio = screen_height / self.image.height
        self.scale = min(width_ratio, height_ratio, 1.0)
        
        if self.scale < 1.0:
            new_width = int(self.image.width * self.scale)
            new_height = int(self.image.height * self.scale)
            self.display_image = self.image.resize((new_width, new_height))
        else:
            self.display_image = self.image.copy()
            
        self.photo = ImageTk.PhotoImage(self.display_image)
        
        # Create canvas
        self.canvas = tk.Canvas(
            self.root,
            width=self.display_image.width,
            height=self.display_image.height
        )
        self.canvas.pack(side=tk.LEFT)
        
        # Display image on canvas
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.photo)
        
        # Variables for crop rectangle
        self.start_x = None
        self.start_y = None
        self.rect = None
        self.crop_coords = None
        
        # Coordinate display labels
        self.coord_frame = ttk.Frame(self.root)
        self.coord_frame.pack(side=tk.RIGHT, padx=10)
        
        ttk.Label(self.coord_frame, text="Coordinates:").pack()
        self.coord_label = ttk.Label(self.coord_frame, text="")
        self.coord_label.pack()
        
        # Instructions
        ttk.Label(self.coord_frame, text="\nInstructions:", font=('Arial', 10, 'bold')).pack()
        ttk.Label(self.coord_frame, text="1. Click and drag to select area").pack()
        ttk.Label(self.coord_frame, text="2. Release to set selection").pack()
        ttk.Label(self.coord_frame, text="3. Press Enter to confirm").pack()
        ttk.Label(self.coord_frame, text="4. Press R to reset").pack()
        
        # Confirm button
        self.confirm_button = ttk.Button(
            self.coord_frame,
            text="Confirm Selection",
            command=self.confirm_selection
        )
        self.confirm_button.pack(pady=10)
        
        # Reset button
        self.reset_button = ttk.Button(
            self.coord_frame,
            text="Reset Selection",
            command=self.reset_selection
        )
        self.reset_button.pack(pady=5)
        
        # Bind mouse events
        self.canvas.bind("<ButtonPress-1>", self.on_press)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_release)
        self.root.bind("<Return>", lambda e: self.confirm_selection())
        self.root.bind("r", lambda e: self.reset_selection())
        
    def on_press(self, event):
        self.start_x = event.x
        self.start_y = event.y
        if self.rect:
            self.canvas.delete(self.rect)
        
    def on_drag(self, event):
        if self.rect:
            self.canvas.delete(self.rect)
        self.rect = self.canvas.create_rectangle(
            self.start_x, self.start_y, event.x, event.y,
            outline='red', width=2
        )
        self.update_coord_label(event.x, event.y)
        
    def on_release(self, event):
        self.update_coord_label(event.x, event.y)
        
    def update_coord_label(self, current_x, current_y):
        # Get coordinates and adjust for scale
        x1 = min(self.start_x, current_x) / self.scale
        y1 = min(self.start_y, current_y) / self.scale
        x2 = max(self.start_x, current_x) / self.scale
        y2 = max(self.start_y, current_y) / self.scale
        
        # Update label with real coordinates
        self.coord_label.config(
            text=f"Left: {int(x1)}\nTop: {int(y1)}\n"
                 f"Right: {int(x2)}\nBottom: {int(y2)}"
        )
        self.crop_coords = (int(x1), int(y1), int(x2), int(y2))
        
    def reset_selection(self):
        if self.rect:
            self.canvas.delete(self.rect)
        self.coord_label.config(text="")
        self.crop_coords = None
        
    def confirm_selection(self):
        if self.crop_coords:
            self.root.quit()
            
    def get_coordinates(self):
        self.root.mainloop()
        self.root.destroy()
        return self.crop_coords

def crop_images(input_folder="screenshots", output_folder="cropped_screenshots"):
    """Process all PNG files in the input folder and save cropped versions"""
    # Create output folder if it doesn't exist
    output_path = Path(output_folder)
    output_path.mkdir(exist_ok=True)
    
    # Get all PNG files
    input_path = Path(input_folder)
    png_files = sorted(list(input_path.glob("*.png")))
    
    if not png_files:
        print(f"No PNG files found in {input_folder}")
        return
    
    print(f"Found {len(png_files)} PNG files to process")
    
    # Get crop coordinates using the first image
    print("\nOpening coordinate selector...")
    selector = CropSelector(png_files[0])
    crop_bounds = selector.get_coordinates()
    
    if not crop_bounds:
        print("No selection made. Exiting.")
        return
        
    print(f"\nUsing crop bounds: {crop_bounds}")
    
    # Process all images with selected bounds
    for png_file in png_files:
        try:
            with Image.open(png_file) as img:
                cropped = img.crop(crop_bounds)
                output_file = output_path / png_file.name
                cropped.save(output_file, "PNG", optimize=True)
                print(f"Processed: {png_file.name}")
        except Exception as e:
            print(f"Error processing {png_file.name}: {e}")

def main():
    print("Starting batch image cropping process...")
    
    if not os.path.exists("screenshots"):
        print("Error: 'screenshots' folder not found!")
        return
    
    crop_images()
    
    print("\nCropping complete!")
    print("Cropped images are saved in the 'cropped_screenshots' folder")

if __name__ == "__main__":
    main()