import json
from datetime import datetime

def lade_katzen():
    with open("cats.json", "r") as f:
        return json.load(f)

def speichere_katzen(katzen):
    with open("cats.json", "w") as f:
        json.dump(katzen, f, indent=4)

def katze_hinzufuegen(name, ration_total):
    katzen = lade_katzen()

    if name in katzen:
        print("Katze existiert bereits.")
    else:
        katzen[name] = {
            "ration_total": ration_total,
            "ration_left": ration_total,
            "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        speichere_katzen(katzen)
        print(f"{name} wurde mit {ration_total}g Tagesration hinzugefügt.")


katze_hinzufuegen("Bruno", 200)
katze_hinzufuegen("Flaekli", 180)