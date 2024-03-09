import tkinter as tk
from tkinter import ttk
import tkinter.font as tkFont
from main import download_images, clear_wallpapers
import random
import threading
import queue
import os
import sys
import winshell
from ttkthemes import ThemedStyle
from PyQt6 import QtWidgets
from PyQt6.QtGui import QFontDatabase
from PyQt6.QtCore import QDir
import ctypes as ct


def dark_title_bar(window):
    # MORE INFO:
    # https://learn.microsoft.com/en-us/windows/win32/api/dwmapi/ne-dwmapi-dwmwindowattribute
    window.update()
    DWMWA_USE_IMMERSIVE_DARK_MODE = 20
    set_window_attribute = ct.windll.dwmapi.DwmSetWindowAttribute
    get_parent = ct.windll.user32.GetParent
    hwnd = get_parent(window.winfo_id())
    rendering_policy = DWMWA_USE_IMMERSIVE_DARK_MODE
    value = 2
    value = ct.c_int(value)
    set_window_attribute(hwnd, rendering_policy, ct.byref(value),
                         ct.sizeof(value))

class WallpaperGUI:
    def __init__(self, master):
        self.master = master
        self.master.title("Spectro")

        self.script_dir = os.path.dirname(__file__)
        self.data_dir = os.path.join(self.script_dir, "data")
        self.currenttheme = "No current theme"

        # Set theme
        style = ThemedStyle(master)
        # style.set_theme("equilux")
        style.set_theme_advanced(theme_name="blue", brightness=0.2, saturation=2, hue=0.98, preserve_transparency=True)

        self.qtapp = QtWidgets.QApplication(sys.argv)

        font_path = os.path.join(self.data_dir, "fonts")
        families = self.load_fonts_from_dir(font_path)

        if families:
            font_family = families[0]  # Assuming you want to use the first font family found
            self.custom_font = tkFont.Font(family="GeosansLight", size=14)
        
        # title_font_path = os.path.join(self.data_dir, "fonts", "Romanesque Serif.ttf")

        # if os.path.isfile(title_font_path):
        self.title_font = tkFont.Font(family="Disco Diva", size=60)  # Assign to self.title_font here
        
        # Colors
        self.background_color = "#050d14"  # Dark background color
        self.text_color = "#caf1fa"  # White text color
        self.text_color_button = "#caf1fa" #"#00182e"
        self.button_color = "#252b3b"  # Light blue button color
        self.button_hover_color = "#caf1fa"  # Button hover color
        self.checkbutton_hover_color = "black"  # Checkbutton hover color
        self.success_color = "#00ff00"  # Green success message color
        self.spinbox_background_color = "#262625"  # Spinbox background color

        self.progress_queue = queue.Queue()

        # Check if the checkbox is checked in datasave.txt
        self.startup_on_boot = self.check_startup_shortcut()

        # Set window size to Full HD
        self.master.geometry("500x1000")
        self.master.configure(bg=self.background_color)
        self.master.attributes('-alpha', 0.93)

        # Create and place the title label
        self.title_label = ttk.Label(master, text="Spectro", style="Title.TLabel")
        self.title_label.grid(row=0, column=0, columnspan=2, padx=10, pady=20, sticky="s")
        
        self.theme_label = ttk.Label(master, text="Add themes (one per line):", foreground=self.text_color, background=self.background_color, style="Text.TLabel")
        self.theme_label.grid(row=1, column=0, padx=10, pady=1, sticky="w")
        
        # Make text box larger and adapt to window size
        self.theme_text = tk.Text(master, height=30, width=100, bg=self.background_color, fg=self.text_color, insertbackground=self.text_color, font=self.custom_font, relief="sunken", highlightcolor="#caf1fa", highlightthickness=0, borderwidth= 9)
        self.theme_text.grid(row=2, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")
        master.grid_rowconfigure(2, weight=1)  # Make row expandable
        master.grid_columnconfigure(0, weight=1)  # Make column expandable
        
        # Load existing themes from themes.txt
        self.load_existing_themes()
        
        # Add Save button
        self.save_button = ttk.Button(master, text="Save Themes", command=self.save_themes, style="TButton", cursor="hand2")
        self.save_button.grid(row=3, column=0, padx=10, pady=10, sticky="w")
        
        self.num_label = ttk.Label(master, text="Number of wallpapers:", foreground=self.text_color, background=self.background_color, style="Text.TLabel")
        self.num_label.grid(row=4, column=0, padx=10, pady=10, sticky="e")
        
        self.num_var = tk.StringVar()
        self.num_spinbox = ttk.Spinbox(master, from_=1, to=100, textvariable=self.num_var, style="TSpinbox", font=self.custom_font)
        self.num_spinbox.grid(row=4, column=1, padx=10, pady=10, sticky="w")
        # self.num_spinbox.configure({"background": self.spinbox_background_color})  # Change Spinbox background color

        # # Message label for displaying success or error
        # self.empty_label = ttk.Label(master, text=" ", foreground=self.success_color, background=self.background_color, style="Text.TLabel")
        # self.empty_label.grid(row=5, column=0, columnspan=2, padx=10, pady=10)
        
        # Message label for displaying success or error
        self.current_theme_label = ttk.Label(master, text=f"Current theme: {self.currenttheme}", background=self.background_color, style="Text.TLabel")
        self.current_theme_label.grid(row=5, column=0, columnspan=2, padx=10, pady=10)
        
        self.download_button = ttk.Button(master, text="Download Wallpapers", command=self.start_download_async, style="TButton", cursor="hand2")
        self.download_button.grid(row=6, column=0, columnspan=2, padx=10, pady=10)
        
        # Message label for displaying success or error
        self.message_label = ttk.Label(master, text="", foreground=self.success_color, background=self.background_color, style="Text.TLabel")
        self.message_label.grid(row=8, column=0, columnspan=2, padx=10, pady=10)

        self.checkbox_value = tk.BooleanVar(value=self.startup_on_boot)
        self.autostart_checkbox = ttk.Checkbutton(master, text="Start on Boot", variable=self.checkbox_value, command=self.on_checkbox_changed, style="TCheckbutton")
        self.autostart_checkbox.grid(row=3, column=1, padx=10, pady=10, sticky="w")

        self.progress_bar = ttk.Progressbar(master, mode='determinate', style="TProgressbar")
        self.progress_bar.grid(row=7, column=0, columnspan=2, padx=10, pady=10, sticky="we")
        self.progress_bar.grid_forget()

        # Load previous value for number of wallpapers
        self.load_datasave()

        # Configure styles
        self.configure_styles()

        self.update_progress()

    def configure_styles(self):
        # Configure styles for buttons, spinbox, and progressbar
        style = ttk.Style()
        # style.theme_use('winnative')
        style.configure("TButton", font=self.custom_font, foreground=self.text_color_button, background=self.button_color)
        style.map("TButton", background=[("active", self.button_hover_color)])
        style.configure("TSpinbox", foreground=self.text_color_button, fieldbackground=self.button_color, insertcolor=self.text_color, borderwidth=0, font=self.custom_font)
        style.configure("TProgressbar", troughcolor=self.background_color, background=self.button_color)
        style.configure("TCheckbutton", foreground=self.text_color, background=self.background_color, font=self.custom_font)
        style.map("TCheckbutton", background=[("active", self.checkbutton_hover_color)])
        style.configure("Title.TLabel", font=(self.title_font), foreground=self.text_color, background=self.background_color)
        style.configure("Text.TLabel", font=self.custom_font, background=self.background_color, foreground=self.text_color) 


    # Function to load fonts from a directory
    def load_fonts_from_dir(self, directory):
        families = set()
        for fi in QDir(directory).entryInfoList(["*.ttf", "*.woff", "*.woff2"]):
            _id = QFontDatabase.addApplicationFont(fi.absoluteFilePath())
            families |= set(QFontDatabase.applicationFontFamilies(_id))
        return list(families)

    def load_existing_themes(self):
        try:
            with open(os.path.join("data","themes.txt"), 'r') as file:
                existing_themes = file.read()
                self.theme_text.insert("1.0", existing_themes)
        except FileNotFoundError:
            self.message_label.config(text="themes.txt file not found.", foreground="red")
    
    def check_startup_shortcut(self):
        # Check if the shortcut exists in the startup folder
        startup_folder = winshell.startup()
        shortcut_path = os.path.join(startup_folder, "Spectro_Autorun.lnk")
        return os.path.exists(shortcut_path)

    def create_shortcut(self):
        # Get the path to the user's startup folder
        startup_folder = winshell.startup()

        # Path to Spectro_Autorun.exe
        exe_path = os.path.abspath("Spectro_Autorun.exe")
        exe_directory = os.path.dirname(exe_path)

        # Create a shortcut in the startup folder
        shortcut_path = os.path.join(startup_folder, "Spectro_Autorun.lnk")
        with winshell.shortcut(shortcut_path) as shortcut:
            shortcut.path = exe_path
            shortcut.description = "Spectro_Autorun"
            shortcut.working_directory = exe_directory

    def delete_shortcut(self):
        # Delete the startup shortcut
        startup_folder = winshell.startup()
        shortcut_path = os.path.join(startup_folder, "Spectro_Autorun.lnk")
        if os.path.exists(shortcut_path):
            os.remove(shortcut_path)

    # Exemple de fonction pour gérer l'état de la case à cocher
    def on_checkbox_changed(self):
        # Update the startup shortcut based on the checkbox state
        if self.checkbox_value.get():
            self.create_shortcut()
        else:
            self.delete_shortcut()

    def get_themes(self):
        themes = self.theme_text.get("1.0", tk.END).splitlines()
        return [theme.strip() for theme in themes if theme.strip()]
    
    def save_themes(self):
        themes = self.get_themes()
        with open("themes.txt", "w") as file:
            file.write("\n".join(themes))
        self.message_label.config(text="Themes saved successfully!", foreground="green")

    def start_download_async(self):
        threading.Thread(target=self.download_async).start()

    def download_async(self):
        self.download_button.config(state=tk.DISABLED)  # Désactiver le bouton pendant le téléchargement
        self.toggle_progress_bar(True)  # Afficher la barre de progression
        self.progress_bar['mode'] = 'indeterminate'  # Mode indéterminé pour le téléchargement
        self.progress_bar.start(10)  # Commencer la barre de progression
        self.message_label.config(text="Downloading wallpapers...", foreground="white")
        themes = self.get_themes()
        num_wallpapers = int(self.num_var.get())  # Convertir en int
        if themes:
            clear_wallpapers("wallpapers")
            random_theme = random.choice(themes)
            self.progress_queue.put(0)  # Mettre à jour la file d'attente avec l'avancement du téléchargement
            download_images([random_theme], num_wallpapers, self.progress_queue)
            self.message_label.config(text=f"{num_wallpapers} wallpapers successfully downloaded.", foreground="green")
            self.save_datasave(random_theme)  # Sauvegarder le nombre de wallpapers
        else:
            self.message_label.config(text="Please add at least one theme.", foreground="red")
        self.progress_bar.stop()  # Arrêter la barre de progression
        self.toggle_progress_bar(False)  # Cacher la barre de progression
        if not os.listdir("wallpapers"):  # Vérifier si le dossier est vide après le téléchargement
            self.message_label.config(text="No images downloaded. Please try again.", foreground="red")
        self.load_datasave()
        self.download_button.config(state=tk.NORMAL)  # Réactiver le bouton après le téléchargement


    def toggle_progress_bar(self, show):
        if show:
            self.progress_bar.grid(row=7, column=0, columnspan=2, padx=10, pady=10, sticky="we")
        else:
            self.progress_bar.grid_forget()

    def update_progress(self):
        try:
            progress = self.progress_queue.get_nowait()
            self.progress_bar['value'] = progress
            if progress == 100:
                self.progress_bar.stop()  # Arrêter la barre de progression si elle est complète
            self.master.after(100, self.update_progress)  # Mettre à jour la barre de progression toutes les 100 ms
        except queue.Empty:
            self.master.after(100, self.update_progress)  # Mettre à jour la barre de progression toutes les 100 ms


    def load_datasave(self):
        try:
            with open(os.path.join("data", "datasave.txt"), 'r') as file:
                lines = file.readlines()
                for line in lines:
                    if line.startswith("num_wallpapers="):
                        num_wallpapers = line.split("=")[1].strip()
                        self.num_var.set(num_wallpapers)
                    if line.startswith("currenttheme="):
                        self.currenttheme = line.split("=")[1].strip()
                        self.current_theme_label.config(text=f"Current theme: {self.currenttheme}")
        except FileNotFoundError:
            pass
        
    def save_datasave(self, theme):
        num_wallpapers = self.num_var.get()
        with open(os.path.join("data", "datasave.txt"), "w") as file:
            file.write(f"num_wallpapers={num_wallpapers}\n")
            file.write(f"currenttheme={theme}\n")

        
    # def download(self):
    #     themes = self.get_themes()
    #     num_wallpapers = int(self.num_var.get())  # Convert string to int
    #     if themes:
    #         clear_wallpapers("wallpapers")
    #         random_theme = random.choice(themes)
    #         download_images([random_theme], num_wallpapers, self.progress_queue)
    #         self.message_label.config(text=f"Theme '{random_theme}' downloaded and {num_wallpapers} wallpapers downloaded.", foreground="green")
    #         self.save_datasave(random_theme)  # Save number of wallpapers
    #     else:
    #         self.message_label.config(text="Please add at least one theme.", foreground="red")
            
    def on_close(self):
    # Vous pouvez ajouter ici tout ce que vous voulez faire avant la fermeture de l'UI, par exemple, sauvegarder les données
        self.save_datasave(self.currenttheme)
        self.master.destroy()  # Fermer l'UI

def main():
    root = tk.Tk()
    app = WallpaperGUI(root)
    # Chemin vers le fichier .ico dans le dossier data
    script_dir = os.path.dirname(__file__)
    icon_path = os.path.join(script_dir, "data", "LogoSpectro.ico")
    dark_title_bar(root)
    
    # Vérifiez si le fichier .ico existe avant de définir l'icône
    if os.path.exists(icon_path):
        root.iconbitmap(icon_path)  # Définir l'icône de la fenêtre principale
    else:
        print("Le fichier .ico spécifié n'existe pas.")

    root.protocol("WM_DELETE_WINDOW", app.on_close)
    root.mainloop()

if __name__ == "__main__":
    main()
