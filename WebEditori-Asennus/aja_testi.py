# -*- coding: utf-8 -*-
"""Kaynnistaa asennustestin taustaprosessina (loki: _build/testi.log)."""
import os
import subprocess
import sys

KANSIO = os.path.dirname(os.path.abspath(__file__))
LOKI = os.path.join(KANSIO, '_build', 'testi.log')
PID = os.path.join(KANSIO, '_build', 'testi.pid')

os.makedirs(os.path.join(KANSIO, '_build'), exist_ok=True)
lokitiedosto = open(LOKI, 'w', encoding='utf-8')
prosessi = subprocess.Popen(
    [sys.executable, '-u', 'asennus_testi.py'],
    cwd=KANSIO, stdout=lokitiedosto, stderr=lokitiedosto,
)
with open(PID, 'w') as tiedosto:
    tiedosto.write(str(prosessi.pid))
print('TESTI KAYNNISSA PID=%d' % prosessi.pid)