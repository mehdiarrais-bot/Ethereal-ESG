"""Configuration commune de la suite de tests.

TestClient (Starlette) envoie « Host: testserver » : ce nom est ajouté à la
liste blanche des hôtes AVANT l'import de main, qui la lit au chargement.
Les tests de sécurité (test_security.py) vérifient le refus des autres noms.
"""
import os

os.environ.setdefault("ESG_ALLOWED_HOSTS", "localhost,127.0.0.1,[::1],testserver")
