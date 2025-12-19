import cv2
import argparse
import sys
import os
import glob
from pathlib import Path

# Додади патека до src директориумот
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.image_loader import vcitaj_sliki, promeni_golemina_na_slikite
from src.stitcher import PanoramaStitcher
from src.utils import pokazi_slika, zacuvaj_slika

def najdi_sliki_vo_folder(folder_patistina):
    """
    Најди ги сите panorama part слики во папка

    Args:
        folder_patistina (str): Патека до папката

    Returns:
        list: Сортирана листа на патеки до сликите
    """
    # Најди ги сите слики што завршуваат на _Part*.jpg
    pattern = os.path.join(folder_patistina, "*_panorama_Part*.jpg")
    sliki_patisti = glob.glob(pattern)

    # Ако не најде со голема P, пробај со мала p
    if not sliki_patisti:
        pattern = os.path.join(folder_patistina, "*_Panorama_Part*.jpg")
        sliki_patisti = glob.glob(pattern)

    # Сортирај ги по бројот (Part1, Part2, Part3...)
    def sortiraj_po_broj(patistina):
        # Извлечи го бројот од името
        ime = os.path.basename(patistina)
        # Најди го бројот по "Part"
        import re
        match = re.search(r'Part(\d+)', ime)
        if match:
            return int(match.group(1))
        return 0

    sliki_patisti.sort(key=sortiraj_po_broj)

    return sliki_patisti

def generiraj_unikatno_ime_za_slika(bazno_ime):
    """
    Генерирај уникатно име за слика што не постои

    Args:
        bazno_ime (str): Основно име на сликата (на пр. 'panorama_rezultat.jpg')

    Returns:
        str: Уникатно име за сликата
    """
    # Ако фајлот не постои, врати го оригиналното име
    if not os.path.exists(bazno_ime):
        return bazno_ime

    # Извлечи име и екстензија
    ime_bez_ekstenzija, ekstenzija = os.path.splitext(bazno_ime)

    # Додај броеви додека не најдеме слободно име
    brojach = 1
    while True:
        novo_ime = f"{ime_bez_ekstenzija}_{brojach}{ekstenzija}"
        if not os.path.exists(novo_ime):
            return novo_ime
        brojach += 1

def obraboti_panorama_folder(folder_patistina, pokazi_rezultat=False,
                             maks_sirina=1200, smer='auto'):
    """
    Обработи една panorama папка

    Args:
        folder_patistina (str): Патека до папката со слики
        pokazi_rezultat (bool): Дали да се прикаже резултатот
        maks_sirina (int): Максимална ширина на сликите
        smer (str): 'auto' за автоматска детекција, 'horizontal' за хоризонтална панорама, 'vertical' за вертикална
    Returns:
        bool: Дали беше успешно
    """
    print(f"\n{'='*60}")
    print(f"Обработка на папка: {folder_patistina}")
    if smer == 'auto':
        print(f"Насока: автоматско детектирање")
    else:
        print(f"Насока: {smer}")
    print(f"{'='*60}")

    # Провери дали папката постои
    if not os.path.exists(folder_patistina):
        print(f"Грешка: Папката {folder_patistina} не постои!")
        return False

    # Најди ги сликите
    sliki_patisti = najdi_sliki_vo_folder(folder_patistina)

    if not sliki_patisti:
        print(f"Грешка: Не се пронајдени panorama part слики во {folder_patistina}")
        print(f" Очекувани имиња: *_panorama_Part*.jpg или *_Panorama_Part*.jpg")
        return False

    print(f"Пронајдени {len(sliki_patisti)} слики:")
    for patistina in sliki_patisti:
        print(f" • {os.path.basename(patistina)}")

    # Вчитај ги сликите
    print("\nВчитување на сликите...")
    sliki = vcitaj_sliki(sliki_patisti)

    if len(sliki) < 2:
        print("Грешка: Неуспешно вчитување на доволно слики!")
        return False

    # Промени големина на сликите
    print("Промена на големина на сликите...")
    sliki = promeni_golemina_na_slikite(sliki, maks_sirina)

    # Креирај панорама
    if smer == 'auto':
        print("Креирање на панорама (автоматска детекција на насока)...")
    else:
        print(f"Креирање на {smer} панорама...")
    stitcher = PanoramaStitcher(smer=smer)
    panorama = stitcher.napravi_panorama(sliki)

    if panorama is None:
        print("Неуспех при креирање на панорама!")
        return False

    # Генерирај име за резултатот
    folder_ime = os.path.basename(folder_patistina)

    # Извлечи го основното име (без _Panorama ако постои)
    if folder_ime.endswith("_Panorama"):
        osnovno_ime = folder_ime
    else:
        osnovno_ime = folder_ime

    # Додади насока во името на резултатот
    if smer == 'auto':
        # За автоматско детектирање, нема да додадеме насока во името
        ime_na_rezultat = f"{osnovno_ime}_Result.jpg"
    else:
        ime_na_rezultat = f"{osnovno_ime}_Result_{smer}.jpg"

    patistina_na_rezultat = os.path.join(folder_patistina, ime_na_rezultat)

    # Генерирај уникатно име ако фајлот веќе постои
    patistina_na_rezultat = generiraj_unikatno_ime_za_slika(patistina_na_rezultat)

    # Зачувај го резултатот
    zacuvaj_slika(panorama, patistina_na_rezultat)

    # Прикажи го резултатот ако е потребно
    if pokazi_rezultat:
        if smer == 'auto':
            pokazi_slika(panorama, f"Резултат: {osnovno_ime}")
        else:
            pokazi_slika(panorama, f"Резултат: {osnovno_ime} ({smer})")

    print(f"✅ Успешно креирана панорама: {os.path.basename(patistina_na_rezultat)}")
    return True

def glavna_funkcija():
    """
    Главна функција за креирање на панорама
    """
    # Парсирај аргументи од командна линија
    parser = argparse.ArgumentParser(
        description='Креирај панорама од повеќе слики или цели папки',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument(
        'vlez',
        nargs='+',
        help='Патеки до сликите ИЛИ папки за спојување'
    )

    parser.add_argument(
        '--izlez',
        default='panorama_rezultat.jpg',
        help='Патека за зачувување на резултатот (default: panorama_rezultat.jpg). Ако фајлот веќе постои, ќе се додаде број.'
    )

    parser.add_argument(
        '--pokazi',
        action='store_true',
        help='Прикажи го резултатот во прозорец'
    )

    parser.add_argument(
        '--maks_sirina',
        type=int,
        default=1200,
        help='Максимална ширина на сликите за обработка (default: 1200)'
    )

    parser.add_argument(
        '--folder',
        action='store_true',
        help='Обработи цели папки наместо поединечни слики'
    )

    parser.add_argument(
        '--smer',
        choices=['auto', 'horizontal', 'vertical'],
        default='auto',
        help='Насока на спојување: auto за автоматска детекција (default), horizontal за хоризонтална панорама, vertical за вертикална панорама'
    )

    args = parser.parse_args()

    # Провери дали обработуваме папки или поединечни слики
    if args.folder:
        # Обработка на папки
        uspeshni = 0
        vkupno = len(args.vlez)

        for folder_patistina in args.vlez:
            if obraboti_panorama_folder(folder_patistina, args.pokazi, args.maks_sirina, args.smer):
                uspeshni += 1

        print(f"\n{'='*60}")
        print(f"РЕЗИМЕ: Успешно обработени {uspeshni} од {vkupno} папки")
        if args.smer == 'auto':
            print(f"Насока на панорами: автоматско детектирање")
        else:
            print(f"Насока на паноами: {args.smer}")
        print(f"{'='*60}")

    else:
        # Стариот начин: обработка на поединечни слики
        if len(args.vlez) < 2:
            print("Грешка: Потребни се најмалку 2 слики!")
            print("Употреба за слики: python main.py слика1.jpg слика2.jpg [дополнителни слики...]")
            print("Употреба за папки: python main.py папка1 папка2 --folder")
            print("Насока: python main.py слика1.jpg слика2.jpg --smer vertical")
            return

        if args.smer == 'auto':
            print("Креирање на панорама (автоматска детекција на насока)...")
        else:
            print(f"Креирање на {args.smer} панорама...")
        print("Вчитување на сликите...")
        sliki = vcitaj_sliki(args.vlez)

        if len(sliki) < 2:
            print("Грешка: Неуспешно вчитување на доволно слики!")
            return

        print("Промена на големина на сликите...")
        sliki = promeni_golemina_na_slikite(sliki, args.maks_sirina)

        if args.smer == 'auto':
            print("Креирање на панорама (автоматска детекција на насока)...")
        else:
            print(f"Креирање на {args.smer} панорама...")
        stitcher = PanoramaStitcher(smer=args.smer)
        panorama = stitcher.napravi_panorama(sliki)

        if panorama is None:
            print("Неуспех при креирање на панорама!")
            return

        # Генерирај уникатно име за излезната слика
        izlez_patistina = generiraj_unikatno_ime_za_slika(args.izlez)

        zacuvaj_slika(panorama, izlez_patistina)

        if args.pokazi:
            if args.smer == 'auto':
                pokazi_slika(panorama, f"Панорама - Резултат ({os.path.basename(izlez_patistina)})")
            else:
                pokazi_slika(panorama, f"Панорама - Резултат ({args.smer}) ({os.path.basename(izlez_patistina)})")

        print(f"✅ Панорамата е успешно зачувана како: {izlez_patistina}")

if __name__ == "__main__":
    glavna_funkcija()