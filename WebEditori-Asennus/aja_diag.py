# -*- coding: utf-8 -*-
"""Kaynnistaa diagnoosin taustaprosessina (loki: _build/diag.log)."""
import os
import subprocess
import sys

KANSIO = os.path.dirname(os.path.abspath(__file__))
LOKI = os.path.join(KANSIO, '_build', 'diag.log')
PID = os.path.join(KANSIO, '_build', 'diag.pid')

os.makedirs(os.path.join(KANSIO, '_build'), exist_ok=True)
lokitiedosto = open(LOKI, 'w', encoding='utf-8')
prosessi = subprocess.Popen(
    [sys.executable, '-u', 'diag_ohjelma.py'],
    cwd=KANSIO, stdout=lokitiedosto, stderr=lokitiedosto,
)
with open(PID, 'w') as tiedosto:
    tiedosto.write(str(prosessi.pid))
print('DIAGNOOSI KAYNNISSA PID=%d' % prosessi.pid)