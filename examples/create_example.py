import cv2
import numpy as np
import os

def sozdadi_horizontalni_primeri_sliki():
    """
    Креирај хоризонтални пример слики со природна текстура
    """
    os.makedirs("examples", exist_ok=True)

    print("Креирање на хоризонтални тест слики...")

    # Креирај голема хоризонтална слика и потоа исечи хоризонтални делови од неа
    golema_slika = np.zeros((500, 1500, 3), dtype=np.uint8)

    # Додади комплексна текстура
    # 1. Градиент позадина
    for i in range(500):
        for j in range(1500):
            golema_slika[i, j] = [
                (i + j) % 256,  # R
                (i * 2 + j) % 256,  # G
                (i + j * 2) % 256  # B
            ]

    # 2. Додади различни облици на различни места
    # Прв дел од сликата
    cv2.circle(golema_slika, (200, 200), 60, (255, 100, 50), -1)
    cv2.rectangle(golema_slika, (300, 100), (400, 300), (100, 200, 50), -1)
    cv2.putText(golema_slika, "A", (350, 250),
                cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 255, 255), 3)

    # Втор дел (преклоп со првиот)
    cv2.circle(golema_slika, (500, 250), 70, (50, 150, 255), -1)
    cv2.rectangle(golema_slika, (600, 150), (700, 350), (200, 50, 150), -1)
    cv2.putText(golema_slika, "B", (650, 300),
                cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 255, 255), 3)

    # Трет дел (преклоп со вториот)
    cv2.circle(golema_slika, (800, 300), 65, (150, 255, 100), -1)
    cv2.rectangle(golema_slika, (900, 200), (1000, 400), (50, 100, 200), -1)
    cv2.putText(golema_slika, "C", (950, 350),
                cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 255, 255), 3)

    # Додади линии кои минуваат низ сите делови
    cv2.line(golema_slika, (100, 400), (1400, 400), (255, 255, 0), 4)
    cv2.line(golema_slika, (150, 100), (1350, 100), (0, 255, 255), 4)

    # Сега исечи 3 преклопувачки делови (хоризонтално)
    slika1 = golema_slika[0:400, 0:600]  # Лево
    slika2 = golema_slika[0:400, 300:900]  # Средина (преклоп)
    slika3 = golema_slika[0:400, 600:1200]  # Десно (преклоп)

    # Зачувај ги
    cv2.imwrite("examples/slika1.jpg", slika1)
    cv2.imwrite("examples/slika2.jpg", slika2)
    cv2.imwrite("examples/slika3.jpg", slika3)

    print("✅ Креирани се 3 хоризонтални слики со голем преклоп!")
    print("  Сега алгоритмот треба да најде многу совпаѓања.")

def sozdadi_vertikalni_primeri_sliki():
    """
    Креирај вертикални пример слики со природна текстура
    """
    os.makedirs("examples", exist_ok=True)

    print("Креирање на вертикални тест слики...")

    # Креирај голема вертикална слика и потоа исечи вертикални делови од неа
    golema_slika = np.zeros((1500, 500, 3), dtype=np.uint8)  # Висока и тесна

    # Додади комплексна текстура - вертикален градиент
    for i in range(1500):
        for j in range(500):
            golema_slika[i, j] = [
                (i * 2 + j) % 256,  # R
                (i + j * 3) % 256,  # G
                (i * 3 + j * 2) % 256  # B
            ]

    # 2. Додади различни облици на различни висини (за вертикален преклоп)
    # Горен дел од сликата
    cv2.circle(golema_slika, (250, 200), 60, (255, 100, 50), -1)
    cv2.rectangle(golema_slika, (150, 300), (350, 400), (100, 200, 50), -1)
    cv2.putText(golema_slika, "1", (200, 380),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

    # Среден дел (преклоп со горниот)
    cv2.circle(golema_slika, (250, 500), 70, (50, 150, 255), -1)
    cv2.rectangle(golema_slika, (150, 600), (350, 700), (200, 50, 150), -1)
    cv2.putText(golema_slika, "2", (200, 680),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

    # Долен дел (преклоп со средниот)
    cv2.circle(golema_slika, (250, 800), 65, (150, 255, 100), -1)
    cv2.rectangle(golema_slika, (150, 900), (350, 1000), (50, 100, 200), -1)
    cv2.putText(golema_slika, "3", (200, 980),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

    # Додади вертикални линии кои минуваат низ сите делови
    cv2.line(golema_slika, (100, 100), (100, 1400), (255, 255, 0), 4)
    cv2.line(golema_slika, (400, 150), (400, 1350), (0, 255, 255), 4)

    # Додади хоризонтална линија низ целата слика за да се види дека е вертикална
    cv2.line(golema_slika, (0, 750), (500, 750), (255, 0, 255), 3)

    # Сега исечи 3 преклопувачки делови (вертикално)
    slika4 = golema_slika[0:600, 0:500]    # Горе
    slika5 = golema_slika[400:1000, 0:500]  # Средина (преклоп)
    slika6 = golema_slika[800:1400, 0:500]  # Долу (преклоп)

    # Зачувај ги
    cv2.imwrite("examples/slika4.jpg", slika4)
    cv2.imwrite("examples/slika5.jpg", slika5)
    cv2.imwrite("examples/slika6.jpg", slika6)

    print("✅ Креирани се 3 вертикални слики со голем преклоп!")
    print("  Овие се портрет-ориентирани слики за вертикална панорама.")

def sozdadi_primeri_sliki():
    """
    Креирај ги сите пример слики (хоризонтални и вертикални)
    """
    os.makedirs("examples", exist_ok=True)

    print("="*60)
    print("КРЕИРАЊЕ НА ПРИМЕР СЛИКИ ЗА ПАНОРАМА")
    print("="*60)

    # Креирај хоризонтални слики
    print("\n1. Креирање на хоризонтални слики...")
    sozdadi_horizontalni_primeri_sliki()

    print("\n" + "-"*60)

    # Креирај вертикални слики
    print("\n2. Креирање на вертикални слики...")
    sozdadi_vertikalni_primeri_sliki()

    print("\n" + "="*60)
    print("✅ Креирани се сите пример слики!")
    print("\nСега можете да ги тестирате панорамите:")
    print("\nЗа хоризонтална панорама:")
    print("  python main.py examples/slika1.jpg examples/slika2.jpg examples/slika3.jpg --pokazi")
    print("\nЗа вертикална панорама:")
    print("  python main.py examples/slika4.jpg examples/slika5.jpg examples/slika6.jpg --pokazi")
    print("\nЗа автоматска детекција на насока:")
    print("  python main.py examples/slika1.jpg examples/slika2.jpg examples/slika3.jpg --smer auto --pokazi")
    print("  python main.py examples/slika4.jpg examples/slika5.jpg examples/slika6.jpg --smer auto --pokazi")

if __name__ == "__main__":
    sozdadi_primeri_sliki()