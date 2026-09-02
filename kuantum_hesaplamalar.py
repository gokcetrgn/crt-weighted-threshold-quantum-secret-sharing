import random
import numpy as np
import math
from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator
from itertools import combinations
from qiskit.circuit.library import UnitaryGate

def U(theta):
    
    #Makaledeki U(θ) = [[cos θ, -sin θ], [sin θ, cos θ]]
    #Qiskit UnitaryGate olarak döndürüyor
    
    mat = np.array([
        [np.cos(theta), -np.sin(theta)],
        [np.sin(theta),  np.cos(theta)]
    ])
    return UnitaryGate(mat)

# bloch küeresini düşünebiliriz


def theta_hesapla(x, A_bar):
    #θ = 2πx / Ā
    return (2 * np.pi * x) / A_bar

def katilimci_islemi(devre, k):
    #U(-ϑi) — katılımcının faz  kaydırması, T kübite (kübit 0) uygulandı
    xi = partial_keys[k]
    theta_i = (2 * math.pi * xi / A_bar) % (2 * math.pi)
    devre.ry(-2 * theta_i, 0)  # T qubit = qubit 0
    return devre

def bell_decode(olcum):
    #Bell ölçüm sonucunu bit çiftine dönüştürdük
    return {
        "00": "00",  # |ω+⟩
        "01": "01",  # |ω-⟩
        "10": "10",  # |ε+⟩
        "11": "11",  # |ε-⟩
    }[olcum]