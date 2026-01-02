import os
import re
import xml.etree.ElementTree as ET
import urllib.request

# Źródłowy XML
SOURCE_URL = os.getenv("SOURCE_URL", "https://kompre.esolu-hub.pl/storage/feeds/kompre.xml")

# Plik wyjściowy
OUT_FILE = "ceneo.xml"

# Frazy, które oznaczają faktycznie NOWY produkt
GOOD_PATTERNS = [
    r"\bnowy\b",
    r"\bfabrycznie nowy\b",
    r"\bnowy zamiennik\b",
    r"\bzupelnie nowy\b",
]

# Frazy, które ZAWSZE blokują
BAD_PATTERNS = [
    r"powystawowy",
    r"magazynowy",
    r"leżak",
    r"lezak",
    r"używany",
    r"uzywany",
    r"regenerowany",
    r"odnowiony",
    r"refurbished",
]


def is_new_offer(offer: ET.Element) -> bool:
    """Zwraca True tylko jeśli produkt jest faktycznie NOWY na podstawie name + attrs."""
    texts = []

    # <name>
    name_el = offer.find("name")
    if name_el is not None and name_el.text:
        texts.append(name_el.text.lower())

    # <attrs><a ...>
    attrs_el = offer.find("attrs")
    if attrs_el is not None:
        for a in attrs_el.findall("a"):
            attr_name = (a.get("name") or "").strip().lower()
            if attr_name in ("model", "rodzaj", "kondycja"):
                if a.text:
                    texts.append(a.text.lower())

    text = " ".join(texts)

    # Jeśli zła fraza → odrzuć
    for bad in BAD_PATTERNS:
        if re.search(bad, text):
            return False

    # Jeśli dobra fraza → akceptuj
    for good in GOOD_PATTERNS:
        if re.search(good, text):
            return True

    return False


def main():
    # Pobranie XML
    with urllib.request.urlopen(SOURCE_URL) as f:
        tree = ET.parse(f)

    root = tree.getroot()
    offers = list(root.findall("o"))

    kept = 0
    removed = 0

    for o in offers:
        # ---- filtr dostępności ----
        stock_raw = o.get("stock")
        avail_raw = o.get("avail")

        try:
            stock_val = int(stock_raw) if stock_raw is not None else 0
        except ValueError:
            stock_val = 0

        is_available = (stock_val > 0) and (avail_raw == "1")
        # ----------------------------

        # Zostają tylko NOWE + dostępne
        if is_available and is_new_offer(o):
            kept += 1
        else:
            root.remove(o)
            removed += 1

    print(f"Pozostawiono ofert: {kept}, usunięto: {removed}")

    # Zapis pliku
    tree.write(OUT_FILE, encoding="utf-8", xml_declaration=True)


if __name__ == "__main__":
    main()
