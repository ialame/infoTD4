import requests
from bs4 import BeautifulSoup
import pandas as pd
import matplotlib.pyplot as plt
import re
import time

# Configuration matplotlib pour accents
plt.rcParams['font.sans-serif'] = ['DejaVu Sans']


def extraire_prix(texte_prix):
    """
    Extrait le prix numerique d'une chaine
    Ex: '95.50 euros/m3' -> 95.50
    """
    match = re.search(r'(\d+\.?\d*)', texte_prix)
    if match:
        return float(match.group(1))
    return 0.0


def compter_etoiles(texte_note):
    """
    Compte le nombre d'etoiles pleines
    Ex: 5 etoiles pleines, 0 vides -> 5
    """
    # Compter les etoiles pleines (caractere Unicode U+2605)
    return texte_note.count('\u2605')


def scraper_page(url):
    """Scrape une page et retourne la liste des produits"""
    response = requests.get(url)

    if response.status_code != 200:
        print(f"Erreur : {response.status_code}")
        return []

    soup = BeautifulSoup(response.text, 'html.parser')
    produits = []

    # Trouver tous les produits
    cards = soup.find_all('div', class_='product-card')

    for card in cards:
        produit = {
            'Type': '',
            'Nom': '',
            'Fournisseur': '',
            'Prix': 0.0,
            'Unite': '',
            'Note': 0,
            'Disponibilite': '',
            'Delai': '',
            'Region': ''
        }

        # A completer : extraire toutes les donnees
        # Extraire le type
        type_elem = card.find('span', class_='product-type')
        if type_elem:
            produit['Type'] = type_elem.text.strip()

        # A completer : extraire les autres champs...

        produits.append(produit)

    return produits


def analyser_donnees(df):
    """Analyse statistique des donnees"""
    print("\n" + "=" * 60)
    print("ANALYSE DES DONNEES - CATALOGUE MARKETBTP")
    print("=" * 60)

    # Informations generales
    print(f"\nNombre total de produits : {len(df)}")
    print(f"Nombre de categories : {df['Type'].nunique()}")
    print(f"Nombre de fournisseurs : {df['Fournisseur'].nunique()}")

    # Statistiques sur les prix
    print("\n--- STATISTIQUES DES PRIX ---")
    print(df['Prix'].describe())

    # A completer : autres analyses...


def visualiser_donnees(df):
    """Cree des graphiques"""

    # 1. Top 10 des produits les plus chers
    plt.figure(figsize=(12, 6))
    top10 = df.nlargest(10, 'Prix')
    plt.barh(range(len(top10)), top10['Prix'], color='steelblue')
    plt.yticks(range(len(top10)), top10['Nom'], fontsize=9)
    plt.xlabel('Prix (euros)', fontsize=12)
    plt.title('Top 10 des produits les plus chers',
              fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.savefig('top10_produits.png', dpi=300)
    plt.show()

    # A completer : autres graphiques...


# Programme principal
def main():
    print("=" * 60)
    print("COLLECTEUR ET ANALYSEUR MARKETBTP")
    print("=" * 60)

    base_url = 'http://www.malomatique.free.fr/MarketBTP/'
    pages = ['index.html', 'page-2.html', 'page-3.html']
    tous_les_produits = []

    # Scraping des 3 pages
    for i, page in enumerate(pages, 1):
        url = base_url + page
        print(f"\nScraping page {i}...")
        produits = scraper_page(url)
        tous_les_produits.extend(produits)
        time.sleep(1)  # Pause pour ne pas surcharger le serveur

    # Conversion en DataFrame
    df = pd.DataFrame(tous_les_produits)

    print(f"\nTotal de produits collectes : {len(df)}")

    # Nettoyage
    df = df[df['Prix'] > 0]

    # Analyse
    analyser_donnees(df)

    # Visualisation
    visualiser_donnees(df)

    # Export CSV
    df.to_csv('marketbtp_analyse.csv', index=False, encoding='utf-8')
    print("\nDonnees exportees dans 'marketbtp_analyse.csv'")


if __name__ == "__main__":
    main()
