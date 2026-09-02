import math
import numpy as np
from itertools import combinations

def mod_tersi(a, m):
    for x in range(1, m):
        if (a * x) % m == 1:
            return x

def aralik_hesapla(a_degerleri, agirliklar, esik):
    n = len(a_degerleri)
    yetkisiz_carpimlar = []
    yetkili_carpimlar = []

    for r in range(1, n + 1):
        for kombinasyon in combinations(range(n), r):
            agirlik_toplami = sum(agirliklar[i] for i in kombinasyon)
            carpim = np.prod([a_degerleri[i] for i in kombinasyon])

            if agirlik_toplami < esik:
                yetkisiz_carpimlar.append(carpim)
            else:
                yetkili_carpimlar.append(carpim)

    sigma = max(yetkisiz_carpimlar)
    fi = min(yetkili_carpimlar)

    if sigma >= fi:
        print("geçerli aralık yok!! a_degerlerini değiştir")
        exit()

    return sigma, fi

def aralarinda_asal_uret(n):
    sayilar = []
    aday = 3
    while len(sayilar) < n:
        asal_mi = all(math.gcd(aday, x) == 1 for x in sayilar)
        if asal_mi:
            sayilar.append(aday)
        aday += 1
    return sayilar

def crt_hesapla(a_listesi, b_listesi):
    toplam_carpim = np.prod(a_listesi)
    sonuc = 0

    for ai, bi in zip(a_listesi, b_listesi):
        p = toplam_carpim // ai
        ters = mod_tersi(p, ai)
        sonuc += bi * ters * p

    return sonuc % toplam_carpim