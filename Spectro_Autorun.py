from main import download_images, clear_wallpapers, read_themes
import random

def get_num_wallpapers():
    try:
        with open("datasave.txt", 'r') as file:
            lines = file.readlines()
            for line in lines:
                if line.startswith("num_wallpapers="):
                    return int(line.split("=")[1].strip())
    except FileNotFoundError:
        return 10  # Valeur par défaut si le fichier n'existe pas

num_wallpapers = get_num_wallpapers()

# def load_datasave():
#     try:
#         with open("datasave.txt", 'r') as file:
#             lines = file.readlines()
#             for line in lines:
#                 if line.startswith("num_wallpapers="):
#                     num_wallpapers = line.split("=")[1].strip()
#                 if line.startswith("currenttheme="):
#                     currenttheme = line.split("=")[1].strip()
#     except FileNotFoundError:
#         pass
    
def save_datasave(theme):
    with open("datasave.txt", "w") as file:
        file.write(f"num_wallpapers={num_wallpapers}\n")
        file.write(f"currenttheme={theme}\n")

def main():
    themes = read_themes("themes.txt")
    
    if themes:
        clear_wallpapers("wallpapers")
        random_theme = random.choice(themes)
        download_images([random_theme], num_wallpapers, None)
        save_datasave(random_theme)
        print(f"Theme '{random_theme}' downloaded and {num_wallpapers} wallpapers downloaded.")
    else:
        print("Please add at least one theme.")

if __name__ == "__main__":
    main()
