import cv2
import numpy as np

class PanoramaStitcher:
    def __init__(self, smer='auto'):
        """
        Иницијализирај го stitching алгоритмот

        Args:
            smer (str): 'auto' за автоматска детекција, 'horizontal' за хоризонтална, 'vertical' за вертикална
        """
        self.smer = smer
        self.broj_na_kliucevi = 5000
        self.odnos_na_sovpadanje = 0.7
        self.ransac_reproj_threshold = 5.0
        self.min_sovpadanja = 10

        # Праг за дали сликите се преклопуваат
        self.min_preklop_za_spojuvanje = 0.1  # 10% минимален преклоп

        self.detektor = cv2.SIFT_create(nfeatures=self.broj_na_kliucevi)
        self.matcher = cv2.BFMatcher()

        # Праг за детекција на вертикална насока при спојување без преклоп
        self.vertical_direction_threshold = 30  # пиксели

    def odredi_smer_na_preklop(self, slika1, slika2):
        """
        Автоматски одреди дали преклопот е хоризонтален или вертикален
        Враќа: 'horizontal', 'vertical' или 'unknown'
        """
        try:
            # Најди клучни точки и совпаѓања
            kliucevi1, deskriptori1 = self.najdi_kliucevi_i_deskriptori(slika1)
            kliucevi2, deskriptori2 = self.najdi_kliucevi_i_deskriptori(slika2)

            if deskriptori1 is None or deskriptori2 is None or len(kliucevi1) < 5 or len(kliucevi2) < 5:
                return 'unknown'

            sovpadanja = self.najdi_sovpadanja(deskriptori1, deskriptori2)

            if len(sovpadanja) < 10:  # Потребни се барем 10 совпаѓања за сигурна детекција
                return 'unknown'

            # Собери ги позициите на совпаѓањата
            tocki1 = np.float32([kliucevi1[m.queryIdx].pt for m in sovpadanja])
            tocki2 = np.float32([kliucevi2[m.trainIdx].pt for m in sovpadanja])

            # Пресметај релативни движења помеѓу совпаѓањата
            dx = tocki2[:, 0] - tocki1[:, 0]
            dy = tocki2[:, 1] - tocki1[:, 1]

            # Пресметај средни апсолутни движења
            mean_dx = np.mean(np.abs(dx))
            mean_dy = np.mean(np.abs(dy))

            # Пресметај варијанса на движењата
            var_dx = np.var(dx)
            var_dy = np.var(dy)

            # Доколку движењата во x-правец се порамномерни (помала варијанса) и поголеми, тогаш е хоризонтален преклоп
            # Доколку движењата во y-правец се порамномерни и поголеми, тогаш е вертикален преклоп
            print(f"Детекција на насока: средно |dx|={mean_dx:.1f}, средно |dy|={mean_dy:.1f}")
            print(f"                 варијанса dx={var_dx:.1f}, варијанса dy={var_dy:.1f}")

            if mean_dx > mean_dy and var_dx < var_dy * 2:  # Повеќе движење по x и порамномерно
                return 'horizontal'
            elif mean_dy > mean_dx and var_dy < var_dx * 2:  # Повеќе движење по y и порамномерно
                return 'vertical'
            else:
                # Провери и односот на сликите
                h1, w1 = slika1.shape[:2]
                h2, w2 = slika2.shape[:2]

                # Ако сликите се повеќе portrait (висина > ширина), веројатно е вертикален панорама
                aspect1 = h1 / w1
                aspect2 = h2 / w2

                if aspect1 > 1.2 and aspect2 > 1.2:  # Portrait слики
                    return 'vertical'
                elif aspect1 < 0.8 and aspect2 < 0.8:  # Landscape слики
                    return 'horizontal'
                else:
                    return 'unknown'

        except Exception as e:
            print(f"Грешка при детекција на насока: {e}")
            return 'unknown'

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

    def spoji_so_homografija(self, slika1, slika2, smer='horizontal'):
        """
        Спој ги две слики со хомографија (само ако има преклоп)
        """
        print(f"Обид за спојување со хомографија ({smer})...")

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

        print(f"✅ Успешно споени со хомографија ({smer})")
        return rezultat

    def spoji_edno_do_drugo(self, slika1, slika2, smer='horizontal', stack_new_on_top=False):
        """
        Едноставно спојување: додај ја втората слика до крајот на првата
        За вертикални панорами: ако stack_new_on_top=True, додавај ја новата слика на врвот
        """
        if smer == 'horizontal':
            print("Спојување едно до друго (хоризонтално)...")

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

        else:  # vertical
            print("Спојување едно до друго (вертикално)...")

            visina1, sirina1 = slika1.shape[:2]
            visina2, sirina2 = slika2.shape[:2]

            # Најди заедничка ширина (средна)
            if abs(sirina1 - sirina2) > 20:
                # Ако има голема разлика, користи ја помалата
                min_sirina = min(sirina1, sirina2)

                # Центрирај ги сликите
                if sirina1 > min_sirina:
                    razlika = sirina1 - min_sirina
                    slika1 = slika1[:, razlika//2:razlika//2 + min_sirina]
                    sirina1 = min_sirina

                if sirina2 > min_sirina:
                    razlika = sirina2 - min_sirina
                    slika2 = slika2[:, razlika//2:razlika//2 + min_sirina]
                    sirina2 = min_sirina

            zajednichka_sirina = max(sirina1, sirina2)

            # Креирај нова слика
            nova_visina = visina1 + visina2
            rezultat = np.zeros((nova_visina, zajednichka_sirina, 3), dtype=np.uint8)

            # За вертикално спојување: провери дали треба да додадеме нова слика на врвот
            if stack_new_on_top:
                print("  Додавање на нова слика на врвот на панорамата")
                # Новата слика (slika2) оди на врвот, тековната панорама (slika1) оди долу
                rezultat[0:visina2, 0:sirina2] = slika2  # Нова слика горе
                rezultat[visina2:visina2+visina1, 0:sirina1] = slika1  # Тековна панорама долу
            else:
                print("  Додавање на нова слика на дното на панорамата")
                # Стандарден режим: тековната панорама (slika1) горе, новата слика (slika2) долу
                rezultat[0:visina1, 0:sirina1] = slika1  # Тековна панорама горе
                rezultat[visina1:visina1+visina2, 0:sirina2] = slika2  # Нова слика долу

        return rezultat

    def odredi_vertikalna_nasoka(self, panorama, nova_slika):
        """
        Одреди дали новата слика треба да се додаде на врвот или на дното
        Враќа True ако новата слика треба да се додаде на врвот
        """
        try:
            # Прво провери дали има некакви совпаѓања
            preklop_procent, broj_sovpadanja = self.proveri_dali_ima_preklop(panorama, nova_slika)

            if broj_sovpadanja > 0:
                # Ако има некои совпаѓања, пробај да ги анализираш
                kliucevi1, deskriptori1 = self.najdi_kliucevi_i_deskriptori(panorama)
                kliucevi2, deskriptori2 = self.najdi_kliucevi_i_deskriptori(nova_slika)

                if deskriptori1 is not None and deskriptori2 is not None:
                    sovpadanja = self.najdi_sovpadanja(deskriptori1, deskriptori2)

                    if len(sovpadanja) > 5:  # Има доволно совпаѓања за анализа
                        tocki1 = np.float32([kliucevi1[m.queryIdx].pt for m in sovpadanja])
                        tocki2 = np.float32([kliucevi2[m.trainIdx].pt for m in sovpadanja])

                        # Пресметај просечна y разлика
                        avg_y_diff = np.mean(tocki2[:, 1] - tocki1[:, 1])

                        print(f"  Просечна y-разлика: {avg_y_diff:.1f} пиксели")

                        # Ако просечната y разлика е негативна, втората слика е повисоко (на врвот)
                        if avg_y_diff < -10:
                            print(f"  ✅ Детектирано: новата слика е повисоко (на врвот)")
                            return True
                        elif avg_y_diff > 10:
                            print(f"  ✅ Детектирано: новата слика е подолу (на дното)")
                            return False

            # Ако не може да се одреди од совпаѓањата, претпостави дека сликите се дадени во редослед
            # од долу кон горе (прва слика е најдолна, последна слика е најгорна)
            # Затоа новата слика секогаш треба да се додаде на врвот
            print(f"  ℹ️ Не можам да одредам насока од совпаѓањата. Претпоставувам дека новата слика е на врвот.")
            return True

        except Exception as e:
            print(f"Грешка при детекција на вертикална насока: {e}")
            # При грешка, претпостави дека новата слика е на врвот
            return True

    def spoji_dve_sliki(self, slika1, slika2, smer='auto'):
        """
        Интелигентно спојување на две слики
        """
        print("="*40)

        # Одреди ја насоката ако е 'auto'
        if smer == 'auto':
            detected_smer = self.odredi_smer_na_preklop(slika1, slika2)
            if detected_smer == 'unknown':
                # Ако не може да се детектира, пробај да се пресмета од димензиите
                h1, w1 = slika1.shape[:2]
                h2, w2 = slika2.shape[:2]
                aspect1 = h1 / w1
                aspect2 = h2 / w2

                if aspect1 > 1.3 and aspect2 > 1.3:  # Portrait слики
                    smer = 'vertical'
                else:
                    smer = 'horizontal'  # default на хоризонтално
            else:
                smer = detected_smer

        print(f"Анализа на сликите ({smer})...")

        # Прво провери дали сликите имаат преклоп
        preklop_procent, broj_sovpadanja = self.proveri_dali_ima_preklop(slika1, slika2)

        print(f"Пронајдени {broj_sovpadanja} совпаѓања")
        print(f"Проценет преклоп: {preklop_procent:.1%}")

        # Ако има доволно преклоп, пробај со хомографија
        if preklop_procent >= self.min_preklop_za_spojuvanje and broj_sovpadanja >= self.min_sovpadanja:
            print(f"Сликите имаат преклоп. Обид за спојување со хомографија ({smer})...")
            rezultat = self.spoji_so_homografija(slika1, slika2, smer)

            if rezultat is not None:
                return rezultat
            else:
                print(f"Хомографија не успеа. Користам едноставно спојување ({smer})...")

        # Ако нема преклоп или хомографија не успеа, користи едноставно спојување
        print(f"Сликите немаат доволно преклоп. Користам едноставно спојување ({smer})...")

        # За вертикални панорами, пробај да одредиш дали новата слика треба да биде на врвот
        if smer == 'vertical':
            stack_new_on_top = self.odredi_vertikalna_nasoka(slika1, slika2)
            return self.spoji_edno_do_drugo(slika1, slika2, smer, stack_new_on_top)
        else:
            return self.spoji_edno_do_drugo(slika1, slika2, smer)

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

        # Автоматско детектирање на насоката од првите две слики
        if self.smer == 'auto':
            print("Автоматско детектирање на насока на панорамата...")
            detected_smer = self.odredi_smer_na_preklop(sliki[0], sliki[1])
            if detected_smer == 'unknown':
                # Ако не може да се детектира, пробај да се пресмета од димензиите
                h1, w1 = sliki[0].shape[:2]
                h2, w2 = sliki[1].shape[:2]
                aspect1 = h1 / w1
                aspect2 = h2 / w2

                if aspect1 > 1.3 and aspect2 > 1.3:  # Portrait слики
                    panorama_smer = 'vertical'
                else:
                    panorama_smer = 'horizontal'  # default на хоризонтално
            else:
                panorama_smer = detected_smer
            print(f"✅ Детектирана насока: {panorama_smer}")
        else:
            panorama_smer = self.smer

        print(f"Започнувам креирање на {panorama_smer} панорама од {len(sliki)} слики...")

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
                print(f"Има преклоп. Обид за спојување со хомографија ({panorama_smer})...")
                nov_panorama = self.spoji_so_homografija(panorama, sliki[i], panorama_smer)

                if nov_panorama is not None:
                    panorama = nov_panorama
                    print(f"✅ Успешно споена слика {i+1} со хомографија ({panorama_smer})")
                else:
                    print(f"❌ Хомографија не успеа за слика {i+1}. Користам едноставно спојување ({panorama_smer})...")
                    # ЗА ВЕРТИКАЛНИ ПАНОРАМИ: Одреди дали новата слика треба да биде на врвот
                    if panorama_smer == 'vertical':
                        stack_new_on_top = self.odredi_vertikalna_nasoka(panorama, sliki[i])
                        panorama = self.spoji_edno_do_drugo(panorama, sliki[i], panorama_smer, stack_new_on_top)
                    else:
                        panorama = self.spoji_edno_do_drugo(panorama, sliki[i], panorama_smer)
            else:
                print(f"⚠️ Нема доволно преклоп за слика {i+1}. Користам едноставно спојување ({panorama_smer})...")
                # ЗА ВЕРТИКАЛНИ ПАНОРАМИ: Одреди дали новата слика треба да биде на врвот
                if panorama_smer == 'vertical':
                    stack_new_on_top = self.odredi_vertikalna_nasoka(panorama, sliki[i])
                    panorama = self.spoji_edno_do_drugo(panorama, sliki[i], panorama_smer, stack_new_on_top)
                else:
                    panorama = self.spoji_edno_do_drugo(panorama, sliki[i], panorama_smer)

        # Исечи ја црната рамка
        panorama = self.iseci_crna_ramka(panorama)

        print("\n" + "="*60)
        print(f"✅ {panorama_smer.upper()} ПАНОРАМАТА Е УСПЕШНО КРЕИРАНА!")
        print("="*60)

        return panorama