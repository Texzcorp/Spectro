from bing_image_downloader import downloader
from PIL import Image
import os
import shutil
import sys
import random
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox


path = os.path.abspath(os.path.dirname(sys.argv[0]))
wallpaper_path = os.path.join(path, "wallpapers")

# Function to read themes from themes.txt file
def read_themes(file_path):
    with open(file_path, 'r') as file:
        themes = [line.strip() for line in file.readlines() if line.strip()]
    return themes

# Function to download images based on themes and filter full HD images
def download_images(themes, num_wallpapers, progress_queue):
    for theme in themes:
        print(f"Searching images for theme: {theme}")
        large_limit = int(max(num_wallpapers + 20, num_wallpapers * 1.2))
        query = f'{theme} wallpaper 1920x1080 landscape'
        downloader.download(query, limit=large_limit, output_dir=os.path.join("data","temp"), adult_filter_off=False, force_replace=False, timeout=60)
        if progress_queue is not None:  # Vérifier si progress_queue n'est pas None
            progress_queue.put(50)  # Mettre à jour la file d'attente avec l'avancement du téléchargement
    move_full_hd_images(os.path.join("data","temp"), num_wallpapers, progress_queue)  # Appeler la fonction de filtrage des images

# Function to move full HD images from subfolders to the wallpaper folder
def move_full_hd_images(directory, num_wallpapers, progress_queue):
    total_images = sum([len(files) for _, _, files in os.walk(directory)])
    current_image = 0
    for root, dirs, files in os.walk(directory):
        for file in files:
            filepath = os.path.join(root, file)
            if os.path.isfile(filepath):
                try:
                    with Image.open(filepath) as img:
                        if img.width >= 1920 and img.height >= 1080:
                            shutil.move(filepath, os.path.join("wallpapers", file))
                            current_image += 1
                            progress = int((current_image / total_images) * 50) + 50  # Progression après le téléchargement
                            progress_queue.put(progress)  # Mettre à jour la file d'attente avec l'avancement du filtrage
                            print(f"Moved full HD image: {file}")
                        else:
                            os.remove(filepath)
                            print(f"Removed non-full HD image: {file}")
                except Exception as e:
                    # print(f"Error processing {file}: {str(e)}")
                    os.remove(filepath)
    keep_random_images("wallpapers", num_wallpapers)

# Function to keep only 2 random images from the list
def keep_random_images(directory, num_wallpapers):
    image_files = os.listdir(directory)
    random.shuffle(image_files)
    images_to_keep = image_files[:num_wallpapers]  # Choose amout of images to keep
    for filename in image_files:
        if filename not in images_to_keep:
            os.remove(os.path.join(directory, filename))
            print(f"Removed: {filename}")


def clear_wallpapers(directory):
    # Check if the wallpaper folder exists
    if os.path.exists(directory):
        # Remove all files in the directory
        for filename in os.listdir(directory):
            filepath = os.path.join(directory, filename)
            try:
                if os.path.isfile(filepath):
                    os.remove(filepath)
                    print(f"Deleted: {filename}")
            except Exception as e:
                print(f"Error deleting {filename}: {str(e)}")

def set_wallpaper(wallpaper_path):
    # # Check if the wallpaper folder exists
    if os.path.exists(wallpaper_path):
        print("Wallpaper loaded.")

if __name__ == "__main__":
    # Read themes from themes.txt
    num_wallpapers = 10
    themes_file = "themes.txt"
    if not os.path.isfile(themes_file):
        print("themes.txt file not found!")
    # else:
        # themes = read_themes(themes_file)
        # clear_wallpapers("wallpaper")
        # # Choose a random theme
        # random_theme = random.choice(themes)
        # print(f"Selected theme: {random_theme}")
        # download_images([random_theme], num_wallpapers)
