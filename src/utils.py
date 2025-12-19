import cv2
import numpy as np
import os

def pokazi_slika(slika, naslov='Слика'):
    """
    Прикажи слика во прозорец
    """
    cv2.imshow(naslov, slika)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

def zacuvaj_slika(slika, patistina):
    """
    Зачувај слика на дадена патека
    """
    try:
        cv2.imwrite(patistina, slika)
        print(f"✅ Сликата е зачувана како: {patistina}")
        return True
    except Exception as e:
        print(f"❌ Грешка при зачувување на сликата {patistina}: {e}")
        return False

def pretvori_vo_sivo(slika):
    """
    Претвори слика во сива боја
    """
    return cv2.cvtColor(slika, cv2.COLOR_BGR2GRAY)