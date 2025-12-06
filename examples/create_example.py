import cv2
import numpy as np
import os

def sozdadi_primeri_sliki():
    """
    Креирај подобрени пример слики со природна текстура
    """
    os.makedirs("examples", exist_ok=True)

    print("Креирање на подобрени тест слики...")

    # Креирај голема слика и потоа исечи делови од неа
    golema_slika = np.zeros((500, 1500, 3), dtype=np.uint8)

    # Додади комплексна текстура
    # 1. Градиент позадина
    for i in range(500):
        for j in range(1500):
            golema_slika[i, j] = [
                (i + j) % 256,        # R
                (i * 2 + j) % 256,    # G
                (i + j * 2) % 256     # B
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

    # Сега исечи 3 преклопувачки делови
    slika1 = golema_slika[0:400, 0:600]      # Лево
    slika2 = golema_slika[0:400, 300:900]    # Средина (преклоп)
    slika3 = golema_slika[0:400, 600:1200]   # Десно (преклоп)

    # Зачувај ги
    cv2.imwrite("examples/slika1.jpg", slika1)
    cv2.imwrite("examples/slika2.jpg", slika2)
    cv2.imwrite("examples/slika3.jpg", slika3)

    print("✅ Креирани се 3 слики со голем преклоп!")
    print("   Сега алгоритмот треба да најде многу совпаѓања.")
    print("\nТестирај: python main.py examples/slika1.jpg examples/slika2.jpg examples/slika3.jpg --pokazi")

if __name__ == "__main__":
    sozdadi_primeri_sliki()