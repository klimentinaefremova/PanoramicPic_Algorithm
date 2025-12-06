import cv2
import numpy as np

class PanoramaStitcher:
    def __init__(self):
        """
        Иницијализирај го stitching алгоритмот
        """
        self.broj_na_kliucevi = 5000
        self.odnos_na_sovpadanje = 0.7
        self.ransac_reproj_threshold = 5.0
        self.min_sovpadanja = 10

        # НОВО: Праг за дали сликите се преклопуваат
        self.min_preklop_za_spojuvanje = 0.1  # 10% минимален преклоп

        self.detektor = cv2.SIFT_create(nfeatures=self.broj_na_kliucevi)
        self.matcher = cv2.BFMatcher()

    def proveri_dali_ima_preklop(self, slika1, slika2):
        """
        Провери дали две слики имаат преклоп
        Враќа процент на преклоп (0-1) и број на совпаѓања
        """
        try:
            # Најди клучни точки
            kliucevi1, deskriptori1 = self.najdi_kliucevi_i_deskriptori(slika1)
            kliucevi2, deskriptori2 = self.najdi_kliucevi_i_deskriptori(slika2)

            if deskriptori1 is None or deskriptori2 is None:
                return 0.0, 0

            sovpadanja = self.najdi_sovpadanja(deskriptori1, deskriptori2)

            if len(sovpadanja) == 0:
                return 0.0, 0

            # Пресметај процентуално колку од сликата преклопува
            # (груба проценка базирана на број на совпаѓања)
            avg_matches_per_image = (len(kliucevi1) + len(kliucevi2)) / 2
            if avg_matches_per_image == 0:
                return 0.0, len(sovpadanja)

            preklop_procent = min(1.0, len(sovpadanja) / avg_matches_per_image * 2)

            return preklop_procent, len(sovpadanja)

        except Exception as e:
            print(f"Грешка при проверка на преклоп: {e}")
            return 0.0, 0

    def najdi_kliucevi_i_deskriptori(self, slika):
        """
        Најди клучеви точки и дескриптори на слика
        """
        if len(slika.shape) == 3:
            slika_siva = cv2.cvtColor(slika, cv2.COLOR_BGR2GRAY)
        else:
            slika_siva = slika

        try:
            kliucevi, deskriptori = self.detektor.detectAndCompute(slika_siva, None)
            return kliucevi, deskriptori
        except Exception as e:
            print(f"Грешка при детекција на клучни точки: {e}")
            return [], None

    def najdi_sovpadanja(self, deskriptori1, deskriptori2):
        """
        Најди совпаѓања помеѓу две сетови на дескриптори
        """
        if deskriptori1 is None or deskriptori2 is None:
            return []

        try:
            sovpadanja_grubi = self.matcher.knnMatch(deskriptori1, deskriptori2, k=2)
            dobri_sovpadanja = []

            for m, n in sovpadanja_grubi:
                if m.distance < self.odnos_na_sovpadanje * n.distance:
                    dobri_sovpadanja.append(m)

            return dobri_sovpadanja
        except Exception as e:
            print(f"Грешка при наоѓање совпаѓања: {e}")
            return []

    def presmetaj_homografija(self, kliucevi1, kliucevi2, sovpadanja):
        """
        Пресметај хомографиска трансформација
        """
        if len(sovpadanja) < self.min_sovpadanja:
            return None, None

        try:
            tocki1 = np.float32([kliucevi1[m.queryIdx].pt for m in sovpadanja]).reshape(-1, 1, 2)
            tocki2 = np.float32([kliucevi2[m.trainIdx].pt for m in sovpadanja]).reshape(-1, 1, 2)

            homografija, maska = cv2.findHomography(
                tocki2, tocki1, cv2.RANSAC, self.ransac_reproj_threshold
            )

            return homografija, maska
        except Exception as e:
            print(f"Грешка при пресметка на хомографија: {e}")
            return None, None

    def spoji_so_homografija(self, slika1, slika2):
        """
        Спој ги две слики со хомографија (само ако има преклоп)
        """
        print("Обид за спојување со хомографија...")

        # Најди клучни точки
        kliucevi1, deskriptori1 = self.najdi_kliucevi_i_deskriptori(slika1)
        kliucevi2, deskriptori2 = self.najdi_kliucevi_i_deskriptori(slika2)

        print(f"Пронајдени {len(kliucevi1)} клучни точки во првата слика")
        print(f"Пронајдени {len(kliucevi2)} клучни точки во втората слика")

        if len(kliucevi1) < 5 or len(kliucevi2) < 5:
            print("Премалку клучни точки. Не можам да спојам со хомографија.")
            return None

        sovpadanja = self.najdi_sovpadanja(deskriptori1, deskriptori2)
        print(f"Пронајдени {len(sovpadanja)} совпаѓања")

        if len(sovpadanja) < self.min_sovpadanja:
            print(f"Нема доволно совпаѓања ({len(sovpadanja)} < {self.min_sovpadanja})")
            return None

        homografija, maska = self.presmetaj_homografija(kliucevi1, kliucevi2, sovpadanja)

        if homografija is None:
            print("Неуспех при пресметка на хомографија.")
            return None

        # Примени трансформација
        visina1, sirina1 = slika1.shape[:2]
        visina2, sirina2 = slika2.shape[:2]

        # Пресметај димензии
        tocki = np.array([
            [0, 0],
            [0, visina2],
            [sirina2, visina2],
            [sirina2, 0]
        ], dtype=np.float32).reshape(-1, 1, 2)

        tocki_transformirani = cv2.perspectiveTransform(tocki, homografija)

        site_tocki = np.concatenate((
            np.array([[0, 0], [0, visina1], [sirina1, visina1], [sirina1, 0]],
                     dtype=np.float32).reshape(-1, 1, 2),
            tocki_transformirani
        ), axis=0)

        [x_min, y_min] = np.int32(site_tocki.min(axis=0).ravel() - 0.5)
        [x_max, y_max] = np.int32(site_tocki.max(axis=0).ravel() + 0.5)

        translacija = [-x_min, -y_min]
        homografija_T = np.array([
            [1, 0, translacija[0]],
            [0, 1, translacija[1]],
            [0, 0, 1]
        ])

        nova_sirina = x_max - x_min
        nova_visina = y_max - y_min

        # Провери дали резултатот е разумна големина
        if nova_sirina > 10000 or nova_visina > 10000:
            print("Резултатот би бил преголем.")
            return None

        slika2_transformirana = cv2.warpPerspective(
            slika2, homografija_T.dot(homografija),
            (nova_sirina, nova_visina)
        )

        # Копирај ја првата слика
        rezultat = slika2_transformirana.copy()

        # Додади ја првата слика
        x1_start = translacija[0]
        y1_start = translacija[1]
        x1_end = x1_start + sirina1
        y1_end = y1_start + visina1

        # Безбедни граници
        x1_start = max(0, x1_start)
        y1_start = max(0, y1_start)
        x1_end = min(nova_sirina, x1_end)
        y1_end = min(nova_visina, y1_end)

        if x1_end > x1_start and y1_end > y1_start:
            rezultat[y1_start:y1_end, x1_start:x1_end] = slika1[
                                                         :(y1_end - y1_start), :(x1_end - x1_start)
                                                         ]

        print("✅ Успешно споени со хомографија")
        return rezultat

    def spoji_edno_do_drugo(self, slika1, slika2):
        """
        Едноставно спојување: додај ја втората слика до крајот на првата
        """
        print("Спојување едно до друго (без преклоп)...")

        visina1, sirina1 = slika1.shape[:2]
        visina2, sirina2 = slika2.shape[:2]

        # Најди заедничка висина (средна)
        if abs(visina1 - visina2) > 20:
            # Ако има голема разлика, користи ја помалата
            min_visina = min(visina1, visina2)

            # Центрирај ги сликите
            if visina1 > min_visina:
                razlika = visina1 - min_visina
                slika1 = slika1[razlika//2:razlika//2 + min_visina, :]
                visina1 = min_visina

            if visina2 > min_visina:
                razlika = visina2 - min_visina
                slika2 = slika2[razlika//2:razlika//2 + min_visina, :]
                visina2 = min_visina

        zajednichka_visina = max(visina1, visina2)

        # Креирај нова слика
        nova_sirina = sirina1 + sirina2
        rezultat = np.zeros((zajednichka_visina, nova_sirina, 3), dtype=np.uint8)

        # Постави ја првата слика лево
        rezultat[0:visina1, 0:sirina1] = slika1

        # Постави ја втората слика десно
        rezultat[0:visina2, sirina1:sirina1 + sirina2] = slika2

        return rezultat

    def spoji_dve_sliki(self, slika1, slika2):
        """
        Интелигентно спојување на две слики
        """
        print("="*40)
        print("Анализа на сликите...")

        # Прво провери дали сликите имаат преклоп
        preklop_procent, broj_sovpadanja = self.proveri_dali_ima_preklop(slika1, slika2)

        print(f"Пронајдени {broj_sovpadanja} совпаѓања")
        print(f"Проценет преклоп: {preklop_procent:.1%}")

        # Ако има доволно преклоп, пробај со хомографија
        if preklop_procent >= self.min_preklop_za_spojuvanje and broj_sovpadanja >= self.min_sovpadanja:
            print("Сликите имаат преклоп. Обид за спојување со хомографија...")
            rezultat = self.spoji_so_homografija(slika1, slika2)

            if rezultat is not None:
                return rezultat
            else:
                print("Хомографија не успеа. Користам едноставно спојување...")

        # Ако нема преклоп или хомографија не успеа, користи едноставно спојување
        print("Сликите немаат доволно преклоп. Користам едноставно спојување...")
        return self.spoji_edno_do_drugo(slika1, slika2)

    def iseci_crna_ramka(self, slika, prag=10):
        """
        Исечи ја црната рамка од сликата
        """
        if len(slika.shape) == 3:
            siva = cv2.cvtColor(slika, cv2.COLOR_BGR2GRAY)
        else:
            siva = slika

        nenulti = cv2.findNonZero((siva > prag).astype(np.uint8))

        if nenulti is None or len(nenulti) == 0:
            return slika

        x, y, w, h = cv2.boundingRect(nenulti)
        return slika[y:y+h, x:x+w]

    def napravi_panorama(self, sliki):
        """
        Направи панорама од повеќе слики
        """
        if len(sliki) < 2:
            print("Потребни се најмалку 2 слики за панорама")
            return None

        print(f"Започнувам креирање на панорама од {len(sliki)} слики...")

        # Започни со првата слика
        panorama = sliki[0]

        # Додавај ги останатите слики
        for i in range(1, len(sliki)):
            print(f"\n{'='*60}")
            print(f"СПОЈУВАЊЕ НА СЛИКА {i+1}/{len(sliki)}")
            print(f"{'='*60}")

            # Провери дали следната слика преклопува со тековната панорама
            preklop_procent, broj_sovpadanja = self.proveri_dali_ima_preklop(panorama, sliki[i])

            print(f"Преклоп со панорамата: {preklop_procent:.1%} ({broj_sovpadanja} совпаѓања)")

            if preklop_procent >= self.min_preklop_za_spojuvanje and broj_sovpadanja >= self.min_sovpadanja:
                print("Има преклоп. Обид за спојување со хомографија...")
                nov_panorama = self.spoji_so_homografija(panorama, sliki[i])

                if nov_panorama is not None:
                    panorama = nov_panorama
                    print(f"✅ Успешно споена слика {i+1} со хомографија")
                else:
                    print(f"❌ Хомографија не успеа за слика {i+1}. Користам едноставно спојување...")
                    panorama = self.spoji_edno_do_drugo(panorama, sliki[i])
            else:
                print(f"⚠️  Нема доволно преклоп за слика {i+1}. Користам едноставно спојување...")
                panorama = self.spoji_edno_do_drugo(panorama, sliki[i])

        # Исечи ја црната рамка
        panorama = self.iseci_crna_ramka(panorama)

        print("\n" + "="*60)
        print("✅ ПАНОРАМАТА Е УСПЕШНО КРЕИРАНА!")
        print("="*60)

        return panorama