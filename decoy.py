import random
from qiskit import QuantumCircuit


def decoy_ekle(veri_listesi, olasilik=0.3):
    #Veri listesine rastgele decoy ekler
    sonuc = []
    decoy_bilgi = []

    for veri in veri_listesi:
        sonuc.append(("veri", veri))

        if random.random() < olasilik:
            durum = random.choice(["0", "1", "+", "-"])
            sonuc.append(("decoy", durum))
            decoy_bilgi.append((len(sonuc) - 1, durum))

    return sonuc, decoy_bilgi




def decoy_hazirla(devre, q, durum):
    if durum == "1":
        devre.x(q)
    elif durum == "+":
        devre.h(q)
    elif durum == "-":
        devre.x(q)
        devre.h(q)


def decoy_olc(devre, q, durum):
    if durum in ["+", "-"]:
        devre.h(q)
    devre.measure(q, q)


def decoy_kontrol(bilgi, olcumler, esik=0.2):
    #Hata oranına göre kanal güvenli mi kontrol eder

    hata = 0

    for (gelen, beklenen), olculen in zip(bilgi, olcumler):
        # Sadece klasik bitler kontrol ediliyor
        if beklenen in ["0", "1"]:
            # Beklenen ile ölçülen farklıysa hata say
            if beklenen != olculen:
                hata += 1

    oran = hata / len(bilgi) if bilgi else 0

    print(f"Hata oranı: {oran:.2f}")

    if oran > esik:
        print("Saldırı tespit edildi!")
        return False

    print("Kanal güvenli")
    return True

def decoy_guvenlik_kontrolu(simulator, genis_liste, decoy_bilgi, eve_saldirdi=False):
    # Bob tarafında decoy ölçümleri yapılır ve kanal güvenliği kontrol edilir

    olcumler = []

    for tip, veri in genis_liste:
        if tip == "decoy":
            devre = QuantumCircuit(1, 1)
            decoy_hazirla(devre, 0, veri)

             # Eve saldırdıysa 
            if eve_saldirdi:
                if random.random() < 0.5:
                    devre.x(0) 
            decoy_olc(devre, 0, veri)

            sonuc = simulator.run(devre, shots=100).result().get_counts()
            olcum = max(sonuc, key=sonuc.get)
            olcumler.append(olcum)

    guvenli = decoy_kontrol(decoy_bilgi, olcumler)
    
    if not guvenli:
        print("Saldırı tespit edildi! İletim durduruluyor.")
        exit()

    hata_sayisi = 0

    for (_, beklenen), olculen in zip(decoy_bilgi, olcumler):
        if beklenen in ["0", "1"]:
            if beklenen != olculen:
                hata_sayisi += 1

    hata_orani = hata_sayisi / len(decoy_bilgi) if decoy_bilgi else 0

    veri_qubitleri = []

    for tip, veri in genis_liste:
        if tip == "veri":
            veri_qubitleri.append(veri)

    return True, hata_orani, veri_qubitleri

def sequence_e_decoy_ekle(t_listesi):
    
    return decoy_ekle(t_listesi)