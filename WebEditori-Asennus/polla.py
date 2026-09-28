# -*- coding: utf-8 -*-
"""Nayttaa taustaprosessin tilan ja lokin loppu.

Aja:  python polla.py                         (rakennus)
tai:  python polla.py _build/testi.log _build/testi.pid
"""
import os
import sys

try:
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
except Exception:
    pass

KANSIO = os.path.dirname(os.path.abspath(__file__))
LOKI = os.path.join(KANSIO, sys.argv[1] if len(sys.argv) > 1
                    else os.path.join('_build', 'rakennus.log'))
PID = os.path.join(KANSIO, sys.argv[2] if len(sys.argv) > 2
                   else os.path.join('_build', 'rakennus.pid'))


def lue_rivit(polku, riveja=25):
    if not os.path.exists(polku):
        return []
    with open(polku, 'r', encoding='utf-8', errors='replace') as tiedosto:
        sisalto = tiedosto.read()
    rivit = sisalto.splitlines()
    return rivit[-riveja:]


tilanne = 'VALMIS (prosessi lopetti)'
if os.path.exists(PID):
    try:
        pid = int(open(PID).read().strip())
        if sys.platform == 'win32':
            import ctypes
            kahva = ctypes.windll.kernel32.OpenProcess(0x1000, False, pid)
            if kahva:
                tilanne = 'KAYNNISSA (PID=%d)' % pid
                ctypes.windll.kernel32.CloseHandle(kahva)
    except Exception:
        pass

print('TILA: ' + tilanne)
for rivi in lue_rivit(LOKI):
    print(rivi)
if tilanne.startswith('KAYNISSA'):
    print('(prosessi viela kaynissa - ajat uudelleen hetken paasta)')