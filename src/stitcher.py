import cv2
import numpy as np

class PanoramaStitcher:
    def __init__(self):
        """
        Иницијализирај го stitching алгоритмот
        """

        self.broj_na_kliucevi = 5000
        self.odnos_na_sovpadanje = 0.75
        self.ransac_reproj_threshold = 5.0


        self.detektor = cv2.SIFT_create(nfeatures=self.broj_na_kliucevi)
        self.matcher = cv2.BFMatcher()

    def najdi_kliucevi_i_deskriptori(self, slika):
        """
        Најди клучеви точки и дескриптори на слика

        Args:
            slika: Влезна слика

        Returns:
            tuple: Клучни точки и дескриптори
        """

        if len(slika.shape) == 3:
            slika_siva = cv2.cvtColor(slika, cv2.COLOR_BGR2GRAY)
        else:
            slika_siva = slika


        kliucevi, deskriptori = self.detektor.detectAndCompute(slika_siva, None)

        return kliucevi, deskriptori

    def najdi_sovpadanja(self, deskriptori1, deskriptori2):
        """
        Најди совпаѓања помеѓу две сетови на дескриптори

        Args:
            deskriptori1: Дескриптори на првата слика
            deskriptori2: Дескриптори на втората слика

        Returns:
            list: Листа на добри совпаѓања
        """

        sovpadanja_grubi = self.matcher.knnMatch(deskriptori1, deskriptori2, k=2)

        # Primeni Lowe's ratio test za filtriranje na dobri sofpaganja
        dobri_sovpadanja = []

        for m, n in sovpadanja_grubi:
            if m.distance < self.odnos_na_sovpadanje * n.distance:
                dobri_sovpadanja.append(m)

        return dobri_sovpadanja

    def presmetaj_homografija(self, kliucevi1, kliucevi2, sovpadanja):
        """
        Пресметај хомографиска трансформација

        Args:
            kliucevi1: Клучни точки на првата слика
            kliucevi2: Клучни точки на втората слика
            sovpadanja: Листа на совпаѓања

        Returns:
            tuple: Хомографиска матрица и статус
        """
        if len(sovpadanja) < 4:
            print("Недоволно совпаѓања за да се пресмета хомографија")
            return None, None


        tocki1 = np.float32([kliucevi1[m.queryIdx].pt for m in sovpadanja]).reshape(-1, 1, 2)
        tocki2 = np.float32([kliucevi2[m.trainIdx].pt for m in sovpadanja]).reshape(-1, 1, 2)


        homografija, maska = cv2.findHomography(
            tocki2, tocki1, cv2.RANSAC, self.ransac_reproj_threshold
        )

        return homografija, maska

    def spoji_dve_sliki(self, slika1, slika2):
        """
        Спој ги две слики

        Args:
            slika1: Лева слика
            slika2: Десна слика

        Returns:
            array: Споена слика
        """

        print("Пронаоѓање на клучни точки...")
        kliucevi1, deskriptori1 = self.najdi_kliucevi_i_deskriptori(slika1)
        kliucevi2, deskriptori2 = self.najdi_kliucevi_i_deskriptori(slika2)


        print(f"Пронајдени {len(kliucevi1)} клучни точки во првата слика")
        print(f"Пронајдени {len(kliucevi2)} клучни точки во втората слика")

        sovpadanja = self.najdi_sovpadanja(deskriptori1, deskriptori2)
        print(f"Пронајдени {len(sovpadanja)} совпаѓања")


        homografija, maska = self.presmetaj_homografija(kliucevi1, kliucevi2, sovpadanja)

        if homografija is None:
            print("Неуспех при пресметка на хомографија")
            return None


        visina1, sirina1 = slika1.shape[:2]
        visina2, sirina2 = slika2.shape[:2]


        tocki = np.array([
            [0, 0],
            [0, visina1],
            [sirina1, visina1],
            [sirina1, 0]
        ], dtype=np.float32).reshape(-1, 1, 2)

        tocki_transformirani = cv2.perspectiveTransform(
            np.array([
                [0, 0],
                [0, visina2],
                [sirina2, visina2],
                [sirina2, 0]
            ], dtype=np.float32).reshape(-1, 1, 2), homografija
        )

        site_tocki = np.concatenate((tocki, tocki_transformirani), axis=0)

        [x_min, y_min] = np.int32(site_tocki.min(axis=0).ravel() - 0.5)
        [x_max, y_max] = np.int32(site_tocki.max(axis=0).ravel() + 0.5)

        translacija = [-x_min, -y_min]
        homografija_T = np.array([
            [1, 0, translacija[0]],
            [0, 1, translacija[1]],
            [0, 0, 1]
        ])


        slika2_transformirana = cv2.warpPerspective(
            slika2, homografija_T.dot(homografija),
            (x_max - x_min, y_max - y_min)
        )


        slika2_transformirana[
        translacija[1]:translacija[1] + visina1,
        translacija[0]:translacija[0] + sirina1
        ] = slika1

        return slika2_transformirana

    def napravi_panorama(self, sliki):
        """
        Направи панорама од повеќе слики

        Args:
            sliki (list): Листа на слики

        Returns:
            array: Панорамска слика
        """
        if len(sliki) < 2:
            print("Потребни се најмалку 2 слики за панорама")
            return None

        print(f"Започнувам креирање на панорама од {len(sliki)} слики...")


        panorama = sliki[0]


        for i in range(1, len(sliki)):
            print(f"Спојување на слика {i+1}/{len(sliki)}...")
            panorama = self.spoji_dve_sliki(panorama, sliki[i])

            if panorama is None:
                print(f"Неуспех при спојување на слика {i+1}")
                return None


        panorama = self.iseci_crna_ramka(panorama)

        print("Панорамата е успешно креирана!")
        return panorama

    def iseci_crna_ramka(self, slika, prag=10):
        """
        Исечи ја црната рамка од сликата

        Args:
            slika: Влезна слика
            prag (int): Праг за детекција на црна боја

        Returns:
            array: Исечена слика
        """
        if len(slika.shape) == 3:
            siva = cv2.cvtColor(slika, cv2.COLOR_BGR2GRAY)
        else:
            siva = slika


        nenulti = cv2.findNonZero((siva > prag).astype(np.uint8))

        if nenulti is None:
            return slika


        x, y, w, h = cv2.boundingRect(nenulti)

        return slika[y:y+h, x:x+w]