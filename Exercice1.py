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
    response.encoding ='utf-8'

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
            'specs':{},
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

        # Extraire le nom
        nom_elem = card.find('h2', class_='product-name')
        if nom_elem:
            produit['Nom'] = nom_elem.text.strip()

        # Extraire le prix

        prix_elem = card.find('div', class_='price')
        if prix_elem:
            produit['Prix'] = extraire_prix(prix_elem.text.strip())
            produit['Unite'] = prix_elem.find('span').text.replace('/','')

        # Extraire le fournisseur

        fournisseur_elem = card.find('p', class_='supplier')
        if fournisseur_elem:
            produit['Fournisseur'] = fournisseur_elem.text.replace('Fournisseur :', '').strip()
        # A completer : extraire les autres champs...

        # Extraire les caractéristiques techniques
        div_specs_elem = card.find('div', class_='specs')
        spec_item_elem = div_specs_elem.find_all('div', class_='spec-item')
        items = {
                'Résistance':'',
                 'Classe':'',
                'Délai':'',
                'Région':'',
                'Limite élastique':'',
                'Diamètre':'',
                'Résistance thermique':'',
                'Épaisseur':''
                 }
        for spec_item in spec_item_elem:
            label_elem = spec_item.find('span', class_='spec-label')
            value_elem = spec_item.find('span', class_='spec-value')
            items[label_elem.text.replace(':','').strip()] = value_elem.text.strip()
        #produit['specs'] = items
        produit['Delai']=items['Délai']
        produit['Region']=items['Région']

        # Extraire la note
        note_elem = card.find('div', class_='rating')
        if note_elem:
            produit['Note'] = compter_etoiles(note_elem.text.strip())

        # Extraire la disponibilité
        dispo_elem = card.find('span', class_='availability')
        if dispo_elem:
            produit['Disponibilite'] = dispo_elem.text.strip()

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
    plusCher = df.loc[df['Prix'].idxmax()]
    print(f"Le plus cher est {plusCher['Nom']}, il coute {plusCher['Prix']:.2f} € chez {plusCher['Fournisseur']}")
    moinsCher = df.loc[df['Prix'].idxmin()]
    print(f"Le plus cher est {moinsCher['Nom']}, il coute {moinsCher['Prix']:.2f} € chez {moinsCher['Fournisseur']}")

    # Prix moyen par catégorie
    print(f"\n📦 PRIX MOYEN PAR CATÉGORIE")
    prix_par_type = df.groupby('Type')['Prix'].agg(['mean', 'count']).sort_values('mean', ascending=False)
    for idx, row in prix_par_type.iterrows():
        print(f"   {idx:15s} : {row['mean']:8.2f} € (n={int(row['count'])})")
    # A completer : autres analyses...

    # Prix moyen par fournisseur
    print(f"\n🏭 PRIX MOYEN PAR FOURNISSEUR")
    prix_par_fournisseur = df.groupby('Fournisseur')['Prix'].agg(['mean', 'count']).sort_values('mean',
                                                                                                ascending=False)
    for idx, row in prix_par_fournisseur.head(10).iterrows():
        print(f"   {idx:25s} : {row['mean']:8.2f} € (n={int(row['count'])})")

# Répartition de la disponibilité
    print(f"\n📦 DISPONIBILITÉ DES PRODUITS")
    dispo_counts = df['Disponibilite'].value_counts()
    for dispo, count in dispo_counts.items():
        pourcentage = (count / len(df)) * 100
        print(f"   {dispo:20s} : {count:3d} produits ({pourcentage:5.1f}%)")

    # Note moyenne
    print(f"\n⭐ QUALITÉ")
    print(f"   Note moyenne : {df['Note'].mean():.2f}/5")
    print(f"   Note médiane : {df['Note'].median():.1f}/5")

    # Répartition par région
    print(f"\n🗺️  RÉPARTITION PAR RÉGION")
    region_counts = df['Region'].value_counts()
    for region, count in region_counts.items():
        pourcentage = (count / len(df)) * 100
        print(f"   {region:25s} : {count:3d} produits ({pourcentage:5.1f}%)")

def visualiser_donnees(df):
    """
    Crée des graphiques d'analyse

    Args:
        df (DataFrame): DataFrame contenant les données des produits
    """
    print(f"\n📊 Génération des visualisations...")

    # 1. Top 10 des produits les plus chers
    plt.figure(figsize=(14, 8))
    top10 = df.nlargest(10, 'Prix')
    colors = plt.cm.viridis(range(len(top10)))

    plt.barh(range(len(top10)), top10['Prix'], color=colors)
    plt.yticks(range(len(top10)), [f"{nom[:40]}..." if len(nom) > 40 else nom
                                   for nom in top10['Nom']], fontsize=10)
    plt.xlabel('Prix (€)', fontsize=12, fontweight='bold')
    plt.title('Top 10 des produits les plus chers', fontsize=16, fontweight='bold', pad=20)
    plt.grid(axis='x', alpha=0.3)
    plt.tight_layout()
    plt.savefig('top10_produits.png', dpi=300, bbox_inches='tight')
    print("   ✓ top10_produits.png créé")
    plt.close()

    # 2. Distribution des prix (histogramme)
    plt.figure(figsize=(12, 7))
    plt.hist(df['Prix'], bins=30, color='coral', edgecolor='black', alpha=0.7)
    plt.axvline(df['Prix'].mean(), color='red', linestyle='--', linewidth=2, label=f'Moyenne: {df["Prix"].mean():.2f}€')
    plt.axvline(df['Prix'].median(), color='green', linestyle='--', linewidth=2,
                label=f'Médiane: {df["Prix"].median():.2f}€')
    plt.xlabel('Prix (€)', fontsize=12, fontweight='bold')
    plt.ylabel('Nombre de produits', fontsize=12, fontweight='bold')
    plt.title('Distribution des prix des matériaux', fontsize=16, fontweight='bold', pad=20)
    plt.legend(fontsize=11)
    plt.grid(alpha=0.3)
    plt.tight_layout()
    plt.savefig('distribution_prix.png', dpi=300, bbox_inches='tight')
    print("   ✓ distribution_prix.png créé")
    plt.close()

    # 3. Répartition par catégorie (pie chart)
    plt.figure(figsize=(10, 10))
    type_counts = df['Type'].value_counts()
    colors_pie = plt.cm.Set3(range(len(type_counts)))

    wedges, texts, autotexts = plt.pie(type_counts, labels=type_counts.index,
                                       autopct='%1.1f%%', startangle=90,
                                       colors=colors_pie, textprops={'fontsize': 11})

    for autotext in autotexts:
        autotext.set_color('white')
        autotext.set_fontweight('bold')

    plt.title('Répartition des produits par catégorie', fontsize=16, fontweight='bold', pad=20)
    plt.tight_layout()
    plt.savefig('repartition_categories.png', dpi=300, bbox_inches='tight')
    print("   ✓ repartition_categories.png créé")
    plt.close()

    # 4. Prix moyen par fournisseur
    plt.figure(figsize=(14, 8))
    prix_fournisseur = df.groupby('Fournisseur')['Prix'].mean().sort_values()
    colors_bar = plt.cm.RdYlGn_r(range(len(prix_fournisseur)))

    plt.barh(range(len(prix_fournisseur)), prix_fournisseur.values, color=colors_bar)
    plt.yticks(range(len(prix_fournisseur)), prix_fournisseur.index, fontsize=10)
    plt.xlabel('Prix moyen (€)', fontsize=12, fontweight='bold')
    plt.title('Prix moyen par fournisseur', fontsize=16, fontweight='bold', pad=20)
    plt.grid(axis='x', alpha=0.3)
    plt.tight_layout()
    plt.savefig('prix_fournisseurs.png', dpi=300, bbox_inches='tight')
    print("   ✓ prix_fournisseurs.png créé")
    plt.close()

    # 5. Boxplot des prix par catégorie
    plt.figure(figsize=(12, 8))
    df.boxplot(column='Prix', by='Type', figsize=(12, 8), patch_artist=True)
    plt.suptitle('')
    plt.title('Distribution des prix par catégorie', fontsize=16, fontweight='bold', pad=20)
    plt.xlabel('Catégorie', fontsize=12, fontweight='bold')
    plt.ylabel('Prix (€)', fontsize=12, fontweight='bold')
    plt.xticks(rotation=45, ha='right')
    plt.grid(alpha=0.3)
    plt.tight_layout()
    plt.savefig('boxplot_categories.png', dpi=300, bbox_inches='tight')
    print("   ✓ boxplot_categories.png créé")
    plt.close()

    # 6. Disponibilité des produits
    plt.figure(figsize=(10, 7))
    dispo_counts = df['Disponibilite'].value_counts()
    colors_dispo = {'En stock': 'green', 'Stock limité': 'orange', 'Rupture stock': 'red'}
    bar_colors = [colors_dispo.get(x, 'gray') for x in dispo_counts.index]

    plt.bar(range(len(dispo_counts)), dispo_counts.values, color=bar_colors, edgecolor='black')
    plt.xticks(range(len(dispo_counts)), dispo_counts.index, fontsize=11)
    plt.ylabel('Nombre de produits', fontsize=12, fontweight='bold')
    plt.title('Disponibilité des produits', fontsize=16, fontweight='bold', pad=20)
    plt.grid(axis='y', alpha=0.3)
    plt.tight_layout()
    plt.savefig('disponibilite.png', dpi=300, bbox_inches='tight')
    print("   ✓ disponibilite.png créé")
    plt.close()



# Programme principal
def main():
    print("=" * 60)
    print("COLLECTEUR ET ANALYSEUR MARKETBTP")
    print("=" * 60)

    base_url = 'http://www.malomatique.free.fr/MarketBTP/'
    pages = ['index.html', 'page2.html', 'page3.html']
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
    #print(f"\nTotal de produits collectes : {len(df)}")

    # Nettoyage
    #df = df[df['Prix'] > 0]

    # Analyse
    analyser_donnees(df)

    # Visualisation
    #visualiser_donnees(df)

    # Export CSV
    df.to_csv('marketbtp_analyse.csv', index=False, encoding='utf-8')
    print("\nDonnees exportees dans 'marketbtp_analyse.csv'")


if __name__ == "__main__":
    main()
