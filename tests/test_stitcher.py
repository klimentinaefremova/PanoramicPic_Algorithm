import unittest
import numpy as np
import cv2
import tempfile
import os

# Импортирај ги модулите за тестирање
from src.image_loader import vcitaj_sliki, promeni_golemina_na_slikite  # <-- CHANGED HERE
from src.stitcher import PanoramaStitcher
from src.utils import zacuvaj_slika

class TestPanoramaStitcher(unittest.TestCase):
    """Тестови за PanoramaStitcher класата"""

    def setUp(self):
        """Подготви тест податоци"""
        # Креирај тест слики
        self.slika1 = np.zeros((100, 100, 3), dtype=np.uint8)
        self.slika1[:, :50, 0] = 255  # Лева плава половина

        self.slika2 = np.zeros((100, 100, 3), dtype=np.uint8)
        self.slika2[:, 50:, 2] = 255  # Десна црвена половина

        self.stitcher = PanoramaStitcher()

    def test_init(self):
        """Тестирај иницијализација на stitcher"""
        self.assertIsNotNone(self.stitcher.detektor)
        self.assertIsNotNone(self.stitcher.matcher)
        self.assertEqual(self.stitcher.broj_na_kliucevi, 5000)

    def test_najdi_kliucevi_i_deskriptori(self):
        """Тестирај пронаоѓање на клучни точки"""
        kliucevi, deskriptori = self.stitcher.najdi_kliucevi_i_deskriptori(self.slika1)
        self.assertGreater(len(kliucevi), 0)
        self.assertIsNotNone(deskriptori)

    def test_spoji_dve_sliki(self):
        """Тестирај спојување на две слики"""
        rezultat = self.stitcher.spoji_dve_sliki(self.slika1, self.slika2)
        self.assertIsNotNone(rezultat)

        # Провери димензии
        self.assertGreaterEqual(rezultat.shape[1], 100)  # Ширината треба да биде >= 100

    def test_napravi_panorama(self):
        """Тестирај креирање на панорама"""
        sliki = [self.slika1, self.slika2]
        panorama = self.stitcher.napravi_panorama(sliki)
        self.assertIsNotNone(panorama)

    def test_iseci_crna_ramka(self):
        """Тестирај отсекување на црна рамка"""
        # Креирај слика со црна рамка
        slika = np.zeros((150, 150, 3), dtype=np.uint8)
        slika[25:125, 25:125] = [255, 255, 255]  # Бел квадрат во средината

        isecena = self.stitcher.iseci_crna_ramka(slika)
        self.assertEqual(isecena.shape, (100, 100, 3))

class TestImageLoader(unittest.TestCase):
    """Тестови за модулот за вчитување на слики"""

    def test_vcitaj_sliki(self):  # <-- CHANGED HERE
        """Тестирај вчитување на слики"""
        # Креирај привремени слики за тестирање
        with tempfile.TemporaryDirectory() as temp_dir:
            patistina1 = os.path.join(temp_dir, "test1.jpg")
            patistina2 = os.path.join(temp_dir, "test2.jpg")

            # Зачувај тест слики
            test_slika = np.zeros((100, 100, 3), dtype=np.uint8)
            cv2.imwrite(patistina1, test_slika)
            cv2.imwrite(patistina2, test_slika)

            # Тестирај вчитување
            sliki = vcitaj_sliki([patistina1, patistina2])  # <-- CHANGED HERE
            self.assertEqual(len(sliki), 2)

    def test_promeni_golemina_na_slikite(self):
        """Тестирај промена на големина на слики"""
        slika1 = np.zeros((200, 400, 3), dtype=np.uint8)
        slika2 = np.zeros((300, 600, 3), dtype=np.uint8)

        sliki = [slika1, slika2]
        sliki_promeneti = promeni_golemina_na_slikite(sliki, maksimalna_sirina=300)

        # Провери дали сите слики имаат ширина <= 300
        for slika in sliki_promeneti:
            self.assertLessEqual(slika.shape[1], 300)

class TestUtils(unittest.TestCase):
    """Тестови за помошни функции"""

    def test_zacuvaj_slika(self):
        """Тестирај зачувување на слика"""
        with tempfile.TemporaryDirectory() as temp_dir:
            patistina_izlez = os.path.join(temp_dir, "test_slika.jpg")
            test_slika = np.zeros((100, 100, 3), dtype=np.uint8)

            # Тестирај зачувување
            zacuvaj_slika(test_slika, patistina_izlez)

            # Провери дали фајлот постои
            self.assertTrue(os.path.exists(patistina_izlez))

            # Провери дали може да се вчита повторно
            vcitana_slika = cv2.imread(patistina_izlez)
            self.assertIsNotNone(vcitana_slika)

def run_tests():
    """Изврши ги сите тестови"""
    # Креирај тест суит
    test_suite = unittest.TestLoader().loadTestsFromTestCase(TestPanoramaStitcher)
    test_suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestImageLoader))
    test_suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestUtils))

    # Изврши тестови
    test_runner = unittest.TextTestRunner(verbosity=2)
    rezultat = test_runner.run(test_suite)

    return rezultat

if __name__ == '__main__':
    run_tests()