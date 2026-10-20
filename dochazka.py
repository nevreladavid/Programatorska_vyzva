import csv
import json
import sys
import matplotlib.pyplot as plt
from datetime import datetime




def nacti_data(cesta_k_souboru):
    """Načte data z CSV souboru a převede data a časy na datetime objekty."""
    zaznamy = []
    try:
        with open(cesta_k_souboru, mode="r", encoding="utf-8-sig") as soubor:
            c_csv = csv.DictReader(soubor, delimiter=";")
            for radek in c_csv:
                # Ošetření a převod dat
                zaznam = {
                    "cislo_cipu": radek["číslo čipu"],
                    "zamestnanec": radek["zaměstnanec"],
                    "prichod": datetime.strptime(radek["příchod"], "%Y-%m-%d %H:%M"),
                    "odchod": datetime.strptime(radek["odchod"], "%Y-%m-%d %H:%M"),
                }
                # Výpočet délky směny v hodinách
                delka = zaznam["odchod"] - zaznam["prichod"]
                zaznam["hodin"] = round(delka.total_seconds() / 3600, 2)
                zaznamy.append(zaznam)
    except FileNotFoundError:
        print(f"Chyba: Soubor '{cesta_k_souboru}' byl nenalezen.")
        sys.exit(1)
    return zaznamy


def celkovy_prehled(zaznamy):
    """Vypočítá celkově odpracované hodiny a průměrnou směnu pro každého zaměstnance."""
    statistiky = {}
    for z in zaznamy:
        jmeno = z["zamestnanec"]
        if jmeno not in statistiky:
            statistiky[jmeno] = {
                "cip": z["cislo_cipu"],
                "pocet_dni": 0,
                "celkem_hodin": 0,
            }
        statistiky[jmeno]["pocet_dni"] += 1
        statistiky[jmeno]["celkem_hodin"] += z["hodin"]

    print("\n" + "=" * 50)
    print(f"{'Zaměstnanec':<20} | {'Dní':<5} | {'Celkem hodin':<12} | {'Průměr/směna'}")
    print("=" * 50)

    vystupni_data = []
    for jmeno, data in statistiky.items():
        celkem_zaokrouhlene = round(data["celkem_hodin"], 2)
        prumer = round(data["celkem_hodin"] / data["pocet_dni"], 2)
        print(f"{jmeno:<20} | {data['pocet_dni']:<5} | {data['celkem_hodin']:<12.2f} | {prumer} h")

        vystupni_data.append({
            "číslo čipu": data["cip"],
            "zaměstnanec": jmeno,
            "počet_dní": data["pocet_dni"],
            "celkem_hodin": round(data["celkem_hodin"], 2),
            "průměrná_směna": prumer
        })
    print("=" * 50)
    return vystupni_data


def najdi_extremy(zaznamy):
    """Najde nejdelší a nejkratší směnu v datech."""
    if not zaznamy:
        return

    # Tyto řádky byly posunuté moc doleva, teď už jsou správně uvnitř funkce:
    najdelsi = max(zaznamy, key=lambda x: x["hodin"])
    nejkratsi = min(zaznamy, key=lambda x: x["hodin"])

    print("\n--- EXTRÉMY SMĚN ---")
    print(
        f"Nejdelší směna: {najdelsi['zamestnanec']} ({najdelsi['hodin']} h dne {najdelsi['prichod'].strftime('%Y-%m-%d')})")
    print(
        f"Nejkratší směna: {nejkratsi['zamestnanec']} ({nejkratsi['hodin']} h dne {nejkratsi['prichod'].strftime('%Y-%m-%d')})")


def vyhledat_zamestnance(zaznamy):
    """Umožní vyhledat záznamy konkrétního zaměstnance."""
    jmeno_hledane = input("Zadejte jméno nebo část jména zaměstnance: ").strip().lower()
    nalezeno = [z for z in zaznamy if jmeno_hledane in z["zamestnanec"].lower()]

    if not nalezeno:
        print("Žádní zaměstnanci nebyli nalezeni.")
        return

    print(f"\n--- ZÁZNAMY PRO: {jmeno_hledane.upper()} ---")
    for z in nalezeno:
        print(
            f"Datum: {z['prichod'].strftime('%Y-%m-%d')} | Příchod: {z['prichod'].strftime('%H:%M')} | Odchod: {z['odchod'].strftime('%H:%M')} | Odpracováno: {z['hodin']} h")


def uloz_do_json(data, vystupni_soubor="vysledek.json"):
    """Uloží zpracovaná data do JSON souboru."""
    try:
        with open(vystupni_soubor, mode="w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        print(f"\n[OK] Data byla úspěšně uložena do souboru '{vystupni_soubor}'.")
    except Exception as e:
        print(f"Chyba při ukládání souboru: {e}")


def graf_funkce():
    # Data pro osu X (např. dny v týdnu nebo dny v měsíci)
    dny = ["Po", "Út", "St", "Čt", "Pá"]

    # Data pro osu Y (např. odpracované hodiny)
    hodiny = [8.0, 8.5, 7.5, 9.0, 8.2]

    plt.plot(dny, hodiny, marker='o', ms=8, mec='black', mfc='cyan', linestyle='-', linewidth=2)

    # Přidání popisků a nadpisu
    plt.title("Přehled odpracovaných hodin za týden")
    plt.xlabel("Dny")
    plt.ylabel("Hodiny")

    # Zapnutí mřížky pro lepší čitelnost
    plt.grid(True)

    # Zobrazení grafu okna
    plt.show()

def main():
    if len(sys.argv) < 2:
        print("Použití: python dochazka.py <cesta_k_csv>")
        sys.exit(1)

    cesta = sys.argv[1]
    zaznamy = nacti_data(cesta)
    posledni_statistiky = None

    while True:
        print("\n========================================")
        print("          ANALÝZA DOCHÁZKY")
        print("========================================")
        print("1 - Zobrazit celkový přehled zaměstnanců")
        print("2 - Vyhledat extrémní směny (nejdelší/nejkratší)")
        print("3 - Vyhledat záznamy zaměstnance")
        print("4 - Uložit přehled do JSON")
        print("5 - Vypsání grafu")
        print("0 - Konec")

        volba = input("\nVyberte možnost (0-5): ").strip()

        if volba == "1":
            posledni_statistiky = celkovy_prehled(zaznamy)
        elif volba == "2":
            najdi_extremy(zaznamy)
        elif volba == "3":
            vyhledat_zamestnance(zaznamy)
        elif volba == "4":
            if posledni_statistiky is None:
                # Pokud ještě nebyl zobrazen přehled, spočítáme ho
                posledni_statistiky = []
                # Rychlý výpočet pro JSON
                temp = {}
                for z in zaznamy:
                    j = z["zamestnanec"]
                    if j not in temp:
                        temp[j] = {"cip": z["cislo_cipu"], "dni": 0, "hodiny": 0}
                    temp[j]["dni"] += 1
                    temp[j]["hodiny"] += z["hodin"]
                for j, d in temp.items():
                    posledni_statistiky.append({
                        "číslo čipu": d["cip"],
                        "zamestnanec": j,
                        "počet_dní": d["dni"],
                        "celkem_hodin": round(d["hodiny"], 2),
                        "průměrná_směna": round(d["hodiny"] / d["dni"], 2)
                    })
            uloz_do_json(posledni_statistiky)
        elif volba == "5":
            graf_funkce()
        elif volba == "0":
            print("Ukončuji program. Na shledanou!")
            break
        else:
            print("Neplatná volba, zadejte číslo od 0 do 5.")


if __name__ == "__main__":
    main()