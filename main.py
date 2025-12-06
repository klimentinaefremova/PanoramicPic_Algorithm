import cv2
import argparse
import sys
import os

# Додади патека до src директориумот
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.image_loader import vcitaj_sliki, promeni_golemina_na_slikite  # <-- CHANGED HERE
from src.stitcher import PanoramaStitcher
from src.utils import pokazi_slika, zacuvaj_slika

def glavna_funkcija():
    """
    Главна функција за креирање на панорама
    """
    # Парсирај аргументи од командна линија
    parser = argparse.ArgumentParser(
        description='Креирај панорама од повеќе слики',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument(
        'sliki',
        nargs='+',
        help='Патеки до сликите за спојување'
    )

    parser.add_argument(
        '--izlez',
        default='panorama_rezultat.jpg',
        help='Патека за зачувување на резултатот (default: panorama_rezultat.jpg)'
    )

    parser.add_argument(
        '--pokazi',
        action='store_true',
        help='Прикажи го резултатот во прозорец'
    )

    parser.add_argument(
        '--maks_sirina',
        type=int,
        default=800,
        help='Максимална ширина на сликите за обработка (default: 800)'
    )

    args = parser.parse_args()

    # Провери дали има доволно слики
    if len(args.sliki) < 2:
        print("Грешка: Потребни се најмалку 2 слики!")
        print("Употреба: python main.py слика1.jpg слика2.jpg [дополнителни слики...]")
        return

    # Вчитај ги сликите
    print("Вчитување на сликите...")
    sliki = vcitaj_sliki(args.sliki)  # <-- CHANGED HERE

    if len(sliki) < 2:
        print("Грешка: Неуспешно вчитување на доволно слики!")
        return

    # Промени големина на сликите
    print("Промена на големина на сликите...")
    sliki = promeni_golemina_na_slikite(sliki, args.maks_sirina)

    # Креирај панорама
    print("Креирање на панорама...")
    stitcher = PanoramaStitcher()
    panorama = stitcher.napravi_panorama(sliki)

    if panorama is None:
        print("Неуспех при креирање на панорама!")
        return

    # Зачувај го резултатот
    zacuvaj_slika(panorama, args.izlez)

    # Прикажи го резултатот ако е потребно
    if args.pokazi:
        pokazi_slika(panorama, "Панорама - Резултат")

    print("Процесот е успешно завршен!")

if __name__ == "__main__":
    glavna_funkcija()