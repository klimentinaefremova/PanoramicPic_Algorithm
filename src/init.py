"""
Панорама Стичер - Модул за слиење на слики

Овој модул содржи функции за креирање на панорамски слики
од повеќе влезни слики.
"""

from .image_loader import vcitaj_sliki, promeni_golemina_na_slikite
from .stitcher import PanoramaStitcher
from .utils import pokazi_slika, zacuvaj_slika, pretvori_vo_sivo

__version__ = "1.0.0"
__author__ = "Панорама Стиcher Тим"
__all__ = [
    'vcitaj_sliki',
    'promeni_golemina_na_slikite',
    'PanoramaStitcher',
    'pokazi_slika',
    'zacuvaj_slika',
    'pretvori_vo_sivo'
]