import random
import numpy as np
from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator
from qiskit_aer.noise import NoiseModel, depolarizing_error
from kuantum_hesaplamalar import U, theta_hesapla, bell_decode
from yardimci_fonklar import crt_hesapla, aralik_hesapla, mod_tersi, aralarinda_asal_uret
from decoy import decoy_ekle,decoy_hazirla,decoy_kontrol,decoy_olc,sequence_e_decoy_ekle,decoy_guvenlik_kontrolu




katilimcilar = ["Bob1", "Bob2", "Bob3", "Bob4"]
agirliklar = [1, 2, 2, 3]
esik = 4

n = len(katilimcilar)

a_degerleri = aralarinda_asal_uret(n)
alt_sinir, ust_sinir = aralik_hesapla(a_degerleri, agirliklar, esik)

print("Alt sinir:", alt_sinir)
print("Üst sinir:", ust_sinir)


# gizli anahtar
gizli_sayi = random.randint(alt_sinir + 1, ust_sinir)

while any(gizli_sayi % ai == 0 for ai in a_degerleri):
    gizli_sayi = random.randint(alt_sinir + 1, ust_sinir)

print("Gizli Anahtar:", gizli_sayi)

# gizli mesaj
gizli_bilgi = 157

binary = format(gizli_bilgi, 'b')

if len(binary) % 2 != 0:
    binary = "0" + binary

bitler = []
for i in range(0, len(binary), 2):
    bitler.append(binary[i:i+2])

print("Binary:", binary)
print("Bit çiftleri:", bitler)

paylar = {
    k: (a_degerleri[i], gizli_sayi % a_degerleri[i])
    for i, k in enumerate(katilimcilar)
}

print("\nPaylar:")
for k, v in paylar.items():
    print(f"{k} -> {v}")

A_toplam = np.prod(a_degerleri)

partial_key = {}
for k in katilimcilar:
    ai, bi = paylar[k]
    Ai = A_toplam // ai
    Ai_ters = mod_tersi(Ai, ai)
    partial_key[k] = (bi * Ai * Ai_ters) % A_toplam

print("\ Anahtarlar:")
for k, v in partial_key.items():
    print(f"{k} -> {v}")

# decoy ekleme
genis_dizi, decoy_bilgi = decoy_ekle(bitler)

# noise = NoiseModel()
# error1 = depolarizing_error(0.01, 1)  # 1 qubit gate için
# error2 = depolarizing_error(0.02, 2)  # 2 qubit gate için

# noise.add_all_qubit_quantum_error(error1, ['h', 'x', 'z'])
# noise.add_all_qubit_quantum_error(error2, ['cx'])
# simulator = AerSimulator(noise_model=noise)


simulator = AerSimulator()

decoy_sonuclar = []
H_verisi = []

for tip, veri in genis_dizi:
    if tip == "decoy":
        devre = QuantumCircuit(1, 1)
        decoy_hazirla(devre, 0, veri)
        decoy_olc(devre, 0, veri)

        sonuc = simulator.run(devre, shots=100).result().get_counts()
        decoy_sonuclar.append(list(sonuc.keys())[0])
    else:
        H_verisi.append(veri)

print("\nKanal kontrolü:")


if not decoy_kontrol(decoy_bilgi, decoy_sonuclar):
    print("Saldırı tespit edildi!")
    exit()

# kuaantum kısmı
print("\nKuantum iletim başladı")
sonuc_binary = ""

for bit in H_verisi:

    devre = QuantumCircuit(2, 2)

    # Bell state
    devre.h(0)
    devre.cx(0, 1)

    # encode
    if bit == "01":
        devre.z(0)
    elif bit == "10":
        devre.x(0)
    elif bit == "11":
        devre.x(0)
        devre.z(0)

    

    # U(theta)
    theta = theta_hesapla(gizli_sayi, A_toplam)
    devre.append(U(theta), [0])

    t_listesi = [devre]

    # Katılımcılar
    for i, k in enumerate(katilimcilar):

        genis, decoy_bilgi = sequence_e_decoy_ekle(t_listesi)
        #  eve saldırı simülesi
        eve_saldirdi = False
        if random.random() < 0.2:
            yeni_genis = []
            eve_saldirdi = True
            
            for tip, devre in genis:
                if tip == "veri":
                    olcum_devresi = devre.copy()  
                    olcum_devresi.measure_all()
                    olcum_sonuc = simulator.run(olcum_devresi, shots=1).result().get_counts()
                    olcumus_bit = list(olcum_sonuc.keys())[0] 

                    yeni_devre = QuantumCircuit(2, 2)

                    if olcumus_bit == "00":
                        pass
                    elif olcumus_bit == "01":
                        yeni_devre.x(1)
                    elif olcumus_bit == "10":
                        yeni_devre.x(0)
                    elif olcumus_bit == "11":
                        yeni_devre.x(0)
                        yeni_devre.x(1)

                    yeni_genis.append(("veri", yeni_devre))
                else:
                    yeni_genis.append((tip, devre))

            genis = yeni_genis


        sonuc = decoy_guvenlik_kontrolu(simulator, genis, decoy_bilgi, eve_saldirdi)


        # ters işlem
        theta_i = theta_hesapla(partial_key[k] % A_toplam, A_toplam)

        for d in t_listesi:
            d.append(U(-theta_i), [0])

    # Bell ölçüm
    final = t_listesi[0]
    final.cx(0, 1)
    final.h(0)
    final.measure([0, 1], [0, 1])

    sonuc = simulator.run(final, shots=100).result().get_counts()
    sonuc_binary += bell_decode(list(sonuc.keys())[0])

print("\nİletim tamamlandı")

elde_edilen = int(sonuc_binary, 2)

print("Binary:", sonuc_binary)
print("Sonuç:", elde_edilen)
print("Gerçek:", gizli_bilgi)
print("Durum:", "Doğru" if elde_edilen == gizli_bilgi else "Hatalı")


# crt yi gerielde etme
secilenler = ["Bob2", "Bob3"]

toplam = sum(agirliklar[katilimcilar.index(k)] for k in secilenler)

print("\nSeçilenler:", secilenler)
print("Toplam ağırlık:", toplam)

if toplam >= esik:

    a = [paylar[k][0] for k in secilenler]
    b = [paylar[k][1] for k in secilenler]

    sonuc = crt_hesapla(a, b)
    mod = np.prod(a)

    while sonuc < alt_sinir:
        sonuc += mod

    print("CRT sonucu:", sonuc)
    print("Doğrulama:", "Doğru" if sonuc == gizli_sayi else "Yanlış")

else:
    print("Eşik sağlanamadı")

