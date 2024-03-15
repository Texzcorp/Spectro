import random
import os
from main import download_images, clear_wallpapers, read_themes

def get_savedata():
    savedata = {}
    try:
        with open(os.path.join("data", "datasave.txt"), 'r') as file:
            lines = file.readlines()
            for line in lines:
                key, value = line.strip().split("=")
                savedata[key] = value
    except FileNotFoundError:
        pass
    return savedata

def save_savedata(savedata):
    with open(os.path.join("data", "datasave.txt"), "w") as file:
        for key, value in savedata.items():
            file.write(f"{key}={value}\n")

def main():
    savedata = get_savedata()
    num_wallpapers = int(savedata.get("num_wallpapers", 10))  # Valeur par défaut si non trouvée
    current_theme = savedata.get("currenttheme", "")

    themes = read_themes(os.path.join("data", "themes.txt"))
    
    if themes:
        clear_wallpapers("wallpapers")
        random_theme = random.choice(themes)
        suffix = savedata.get("themesuffix", "")  # Récupérer le suffixe du savedata
        isSFW = savedata.get("adult_filter", "")  # Récupérer le suffixe du savedata
        if suffix:
            random_theme += f" {suffix}"  # Appliquer le suffixe au thème
        download_images([random_theme], num_wallpapers, None, isSFW)
        savedata["currenttheme"] = random_theme  # Mettre à jour le thème actuel dans le savedata
        print(f"Theme '{random_theme}' downloaded and {num_wallpapers} wallpapers downloaded.")
    else:
        print("Please add at least one theme.")

    save_savedata(savedata)  # Sauvegarder le savedata mis à jour

if __name__ == "__main__":
    main()
