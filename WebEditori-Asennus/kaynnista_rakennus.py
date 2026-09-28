# -*- coding: utf-8 -*-
"""Kaynnistaa rakenna.py:n taustaprosessina ja kirjaa tulokset tiedostoon.

Aja:  python kaynnista_rakennus.py
Loki: _build/rakennus.log ja _build/rakennus_virhe.log
"""
import os
import subprocess
import sys

KANSIO = os.path.dirname(os.path.abspath(__file__))
LOKI = os.path.join(KANSIO, '_build', 'rakennus.log')
VIRHE = os.path.join(KANSIO, '_build', 'rakennus_virhe.log')
PID = os.path.join(KANSIO, '_build', 'rakennus.pid')

os.makedirs(os.path.join(KANSIO, '_build'), exist_ok=True)
lokitiedosto = open(LOKI, 'w', encoding='utf-8')
virhetiedosto = open(VIRHE, 'w', encoding='utf-8')
prosessi = subprocess.Popen(
    [sys.executable, '-u', 'rakenna.py'],
    cwd=KANSIO, stdout=lokitiedosto, stderr=virhetiedosto,
)
with open(PID, 'w') as tiedosto:
    tiedosto.write(str(prosessi.pid))
print('RAKENNUS KAYNNISSA PID=%d' % prosessi.pid)
print('Loki: ' + LOKI)