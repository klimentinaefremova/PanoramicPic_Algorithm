import cv2
import numpy as np

def pokazi_slika(slika, naslov="Слика", ceka_klik=True):
    """
    Прикажи слика во прозорец

    Args:
        slika: Слика за прикажување
        naslov (str): Наслов на прозорецот
        ceka_klik (bool): Дали да чека клик за затворање
    """
    cv2.imshow(naslov, slika)
    if ceka_klik:
        cv2.waitKey(0)
        cv2.destroyAllWindows()

def zacuvaj_slika(slika, patistina_izlez="panorama_rezultat.jpg"):
    """
    Зачувај ја сликата

    Args:
        slika: Слика за зачувување
        patistina_izlez (str): Патека за зачувување
    """
    cv2.imwrite(patistina_izlez, slika)
    print(f"Сликата е зачувана како: {patistina_izlez}")

def pretvori_vo_sivo(sliki):
    """
    Претвори ги сликите во сиво

    Args:
        sliki (list): Листа на бои слики

    Returns:
        list: Листа на сиви слики
    """
    sliki_sivi = []

    for slika in sliki:
        siva_slika = cv2.cvtColor(slika, cv2.COLOR_BGR2GRAY)
        sliki_sivi.append(siva_slika)

    return sliki_sivi