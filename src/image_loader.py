import cv2
import os

def vcitaj_sliki(patistina_sliki):  # <-- CHANGED HERE
    """
    Чита повеќе слики од дадена патека

    Args:
        patistina_sliki (list): Листа на патеки до сликите

    Returns:
        list: Листа на прочитани слики
    """
    sliki = []

    for patistina in patistina_sliki:
        if not os.path.exists(patistina):
            print(f"Предупредување: Сликата {patistina} не постои!")
            continue

        slika = cv2.imread(patistina)
        if slika is not None:
            sliki.append(slika)
            print(f"Успешно вчитана слика: {patistina}")
        else:
            print(f"Грешка при вчитување на сликата: {patistina}")

    return sliki

def promeni_golemina_na_slikite(sliki, maksimalna_sirina=800):
    """
    Промени големина на сликите за поеднаква обработка

    Args:
        sliki (list): Листа на слики
        maksimalna_sirina (int): Максимална ширина на сликата

    Returns:
        list: Листа на променети слики
    """
    sliki_promeneti = []

    for slika in sliki:
        visina, sirina = slika.shape[:2]

        if sirina > maksimalna_sirina:
            razmer = maksimalna_sirina / sirina
            nova_sirina = maksimalna_sirina
            nova_visina = int(visina * razmer)
            slika = cv2.resize(slika, (nova_sirina, nova_visina))

        sliki_promeneti.append(slika)

    return sliki_promeneti