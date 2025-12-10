import os
import xml.etree.ElementTree as ET
import urllib.request

# ŹRÓDŁO — Twój oryginalny XML
SOURCE_URL = os.getenv("SOURCE_URL", "https://kompre.esolu-hub.pl/storage/feeds/kompre.xml")  

# NAZWA WYJŚCIOWEGO PLIKU
OUT_FILE = "ceneo.xml"

KEYWORDS = ["nowy", "fabrycznie nowy"]


def is_new_offer(offer: ET.Element) -> bool:
    texts = []

    # <name>
    name_el = offer.find("name")
    if name_el is not None and name_el.text:
        texts.append(name_el.text.lower())

    # <attrs><a name="Model|Rodzaj|Kondycja">
    attrs_el = offer.find("attrs")
    if attrs_el is not None:
        for a in attrs_el.findall("a"):
            attr_name = (a.get("name") or "").strip().lower()
            if attr_name in ("model", "rodzaj", "kondycja"):
                if a.text:
                    texts.append(a.text.lower())

    joined = " ".join(texts)
    return any(k in joined for k in KEYWORDS)


def main():
    # pobranie XML
    with urllib.request.urlopen(SOURCE_URL) as f:
        tree = ET.parse(f)

    root = tree.getroot()
    offers = list(root.findall("o"))

    kept, removed = 0, 0

    for o in offers:
        if is_new_offer(o):
            kept += 1
        else:
            root.remove(o)
            removed += 1

    print(f"Pozostawiono ofert: {kept}, usunięto: {removed}")

    tree.write(OUT_FILE, encoding="utf-8", xml_declaration=True)


if __name__ == "__main__":
    main()
