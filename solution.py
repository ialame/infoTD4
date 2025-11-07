# =============================================================================
# TD4 : WEB SCRAPING AVANCÉ ET ANALYSE DE DONNÉES - CORRECTION COMPLÈTE
# ESTP - Génie Civil
# =============================================================================

from bs4 import BeautifulSoup
import pandas as pd
import matplotlib.pyplot as plt
import re

# Configuration matplotlib pour affichage correct des accents
plt.rcParams['font.sans-serif'] = ['DejaVu Sans']
plt.rcParams['figure.figsize'] = (12, 8)
# Désactiver les warnings pour les glyphes manquants
import warnings

warnings.filterwarnings('ignore', category=UserWarning, module='matplotlib')


# =============================================================================
# FONCTIONS UTILITAIRES
# =============================================================================

def extraire_prix(texte_prix):
    """
    Extrait le prix numérique d'une chaîne
    Ex: '95.50 €/m³' -> 95.50
    """
    match = re.search(r'(\d+\.?\d*)', texte_prix)
    if match:
        return float(match.group(1))
    return 0.0


def compter_etoiles(texte_note):
    """
    Compte le nombre d'étoiles pleines
    Ex: '★★★★☆' -> 4
    """
    return texte_note.count('★')


def nettoyer_texte(texte):
    """
    Nettoie un texte en enlevant les espaces superflus et caractères problématiques

    Args:
        texte (str): Texte à nettoyer

    Returns:
        str: Texte nettoyé
    """
    if not texte:
        return ''

    texte = texte.strip()

    # Remplacer les caractères Unicode problématiques pour matplotlib
    remplacements = {
        '²': '2',
        '³': '3',
        '⁴': '4',
        'º': 'deg',
        '°': 'deg',
        '€': 'EUR',
        'µ': 'micro',
        '±': '+/-',
        '×': 'x',
        '÷': '/',
        '≤': '<=',
        '≥': '>=',
        '≠': '!=',
        '∞': 'inf',
        '√': 'sqrt'
    }

    for ancien, nouveau in remplacements.items():
        texte = texte.replace(ancien, nouveau)

    return texte


# =============================================================================
# EXERCICE 1 : SCRAPER ET ANALYSER LE CATALOGUE MARKETBTP
# =============================================================================

def scraper_page(fichier):
    """
    Scrape une page HTML et retourne la liste des produits

    Args:
        fichier (str): Chemin vers le fichier HTML

    Returns:
        list: Liste de dictionnaires contenant les données des produits
    """
    with open(fichier, 'r', encoding='utf-8') as f:
        html = f.read()

    soup = BeautifulSoup(html, 'html.parser')
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

        # Extraire le type de produit
        type_elem = card.find('span', class_='product-type')
        if type_elem:
            produit['Type'] = nettoyer_texte(type_elem.text)

        # Extraire le nom du produit
        nom_elem = card.find('h2', class_='product-name')
        if nom_elem:
            produit['Nom'] = nettoyer_texte(nom_elem.text)

        # Extraire le fournisseur
        fournisseur_elem = card.find('p', class_='supplier')
        if fournisseur_elem:
            texte = nettoyer_texte(fournisseur_elem.text)
            produit['Fournisseur'] = texte.replace('Fournisseur :', '').replace('Fournisseur:', '').strip()

        # Extraire le prix et l'unité
        prix_elem = card.find('div', class_='price')
        if prix_elem:
            texte_prix = prix_elem.text.strip()
            produit['Prix'] = extraire_prix(texte_prix)

            # Extraire l'unité
            unite_elem = prix_elem.find('span', class_='unit')
            if unite_elem:
                produit['Unite'] = nettoyer_texte(unite_elem.text).replace('/', '')

        # Extraire la note (étoiles)
        note_elem = card.find('div', class_='rating')
        if note_elem:
            produit['Note'] = compter_etoiles(note_elem.text)

        # Extraire la disponibilité
        dispo_elem = card.find('span', class_='availability')
        if dispo_elem:
            produit['Disponibilite'] = nettoyer_texte(dispo_elem.text)

        # Extraire les caractéristiques techniques
        specs_div = card.find('div', class_='specs')
        if specs_div:
            spec_items = specs_div.find_all('div', class_='spec-item')
            for spec in spec_items:
                label_elem = spec.find('span', class_='spec-label')
                value_elem = spec.find('span', class_='spec-value')

                if label_elem and value_elem:
                    label = nettoyer_texte(label_elem.text).replace(':', '')
                    value = nettoyer_texte(value_elem.text)

                    if 'Délai' in label or 'Delai' in label:
                        produit['Delai'] = value
                    elif 'Région' in label or 'Region' in label:
                        produit['Region'] = value

        produits.append(produit)

    return produits


def analyser_donnees(df):
    """
    Analyse statistique complète des données

    Args:
        df (DataFrame): DataFrame contenant les données des produits
    """
    print("\n" + "=" * 70)
    print("ANALYSE DES DONNÉES - CATALOGUE MARKETBTP")
    print("=" * 70)

    # Informations générales
    print(f"\n📊 INFORMATIONS GÉNÉRALES")
    print(f"   Nombre total de produits : {len(df)}")
    print(f"   Nombre de catégories : {df['Type'].nunique()}")
    print(f"   Catégories : {', '.join(df['Type'].unique())}")
    print(f"   Nombre de fournisseurs : {df['Fournisseur'].nunique()}")
    print(f"   Nombre de régions : {df['Region'].nunique()}")

    # Statistiques sur les prix
    print(f"\n💰 STATISTIQUES DES PRIX")
    print(f"   Prix moyen : {df['Prix'].mean():.2f} €")
    print(f"   Prix médian : {df['Prix'].median():.2f} €")
    print(f"   Prix minimum : {df['Prix'].min():.2f} €")
    print(f"   Prix maximum : {df['Prix'].max():.2f} €")
    print(f"   Écart-type : {df['Prix'].std():.2f} €")

    # Statistiques détaillées
    print(f"\n📈 STATISTIQUES DÉTAILLÉES")
    print(df['Prix'].describe())

    # Produit le plus cher et le moins cher
    print(f"\n🏆 PRODUITS EXTRÊMES")
    plus_cher = df.loc[df['Prix'].idxmax()]
    moins_cher = df.loc[df['Prix'].idxmin()]
    print(f"   Plus cher : {plus_cher['Nom']}")
    print(f"              {plus_cher['Prix']:.2f} {plus_cher['Unite']} - {plus_cher['Fournisseur']}")
    print(f"   Moins cher : {moins_cher['Nom']}")
    print(f"               {moins_cher['Prix']:.2f} {moins_cher['Unite']} - {moins_cher['Fournisseur']}")

    # Prix moyen par catégorie
    print(f"\n📦 PRIX MOYEN PAR CATÉGORIE")
    prix_par_type = df.groupby('Type')['Prix'].agg(['mean', 'count']).sort_values('mean', ascending=False)
    for idx, row in prix_par_type.iterrows():
        print(f"   {idx:15s} : {row['mean']:8.2f} € (n={int(row['count'])})")

    # Prix moyen par fournisseur
    print(f"\n🏭 PRIX MOYEN PAR FOURNISSEUR")
    prix_par_fournisseur = df.groupby('Fournisseur')['Prix'].agg(['mean', 'count']).sort_values('mean', ascending=False)
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


# =============================================================================
# EXERCICE 2 : ANALYSE COMPARATIVE AVANCÉE
# =============================================================================

def analyse_comparative(df):
    """
    Analyse comparative avancée des données

    Args:
        df (DataFrame): DataFrame contenant les données des produits
    """
    print("\n" + "=" * 70)
    print("ANALYSE COMPARATIVE AVANCÉE")
    print("=" * 70)

    # 1. Analyse par région
    print("\n🗺️  PRIX MOYEN PAR RÉGION")
    prix_region = df.groupby('Region').agg({
        'Prix': ['mean', 'median', 'min', 'max', 'count']
    }).round(2)
    print(prix_region)

    # Graphique comparatif par région
    plt.figure(figsize=(12, 7))
    prix_region_mean = df.groupby('Region')['Prix'].mean().sort_values()
    plt.bar(range(len(prix_region_mean)), prix_region_mean.values,
            color='skyblue', edgecolor='black')
    plt.xticks(range(len(prix_region_mean)), prix_region_mean.index,
               rotation=45, ha='right', fontsize=10)
    plt.ylabel('Prix moyen (€)', fontsize=12, fontweight='bold')
    plt.title('Prix moyen par région', fontsize=16, fontweight='bold', pad=20)
    plt.grid(axis='y', alpha=0.3)
    plt.tight_layout()
    plt.savefig('prix_par_region.png', dpi=300, bbox_inches='tight')
    print("   ✓ Graphique prix_par_region.png créé")
    plt.close()

    # 2. Analyse des délais
    print("\n⏱️  ANALYSE DES DÉLAIS")
    delais_stats = df.groupby('Delai').size().sort_values(ascending=False)
    print("\nRépartition des délais:")
    for delai, count in delais_stats.head(10).items():
        pourcentage = (count / len(df)) * 100
        print(f"   {delai:15s} : {count:3d} produits ({pourcentage:5.1f}%)")

    # 3. Rapport qualité/prix
    print("\n⭐ RAPPORT QUALITÉ/PRIX")
    # Normaliser les prix pour avoir un score comparable
    df['Prix_normalise'] = (df['Prix'] - df['Prix'].min()) / (df['Prix'].max() - df['Prix'].min())
    # Score qualité/prix : plus la note est élevée et le prix bas, mieux c'est
    df['Score_QP'] = df['Note'] / (df['Prix_normalise'] + 0.1)  # +0.1 pour éviter division par 0

    top_qp = df.nlargest(15, 'Score_QP')[['Nom', 'Type', 'Prix', 'Unite', 'Note', 'Fournisseur', 'Score_QP']]
    print("\nTop 15 meilleurs rapports qualité/prix:")
    print(top_qp.to_string(index=False))

    # 4. Comparaison fournisseurs
    print("\n🏭 COMPÉTITIVITÉ DES FOURNISSEURS")
    fournisseurs_stats = df.groupby('Fournisseur').agg({
        'Prix': 'mean',
        'Note': 'mean',
        'Nom': 'count'
    }).rename(columns={'Nom': 'Nb_produits'}).round(2)
    fournisseurs_stats = fournisseurs_stats.sort_values('Prix')
    print(fournisseurs_stats)

    # Graphique : note vs prix moyen par fournisseur
    plt.figure(figsize=(12, 8))
    plt.scatter(fournisseurs_stats['Prix'], fournisseurs_stats['Note'],
                s=fournisseurs_stats['Nb_produits'] * 50, alpha=0.6,
                c=range(len(fournisseurs_stats)), cmap='viridis')

    for idx, row in fournisseurs_stats.iterrows():
        plt.annotate(idx, (row['Prix'], row['Note']), fontsize=9)

    plt.xlabel('Prix moyen (€)', fontsize=12, fontweight='bold')
    plt.ylabel('Note moyenne (/5)', fontsize=12, fontweight='bold')
    plt.title('Compétitivité des fournisseurs (taille = nb produits)',
              fontsize=16, fontweight='bold', pad=20)
    plt.grid(alpha=0.3)
    plt.tight_layout()
    plt.savefig('competitivite_fournisseurs.png', dpi=300, bbox_inches='tight')
    print("   ✓ Graphique competitivite_fournisseurs.png créé")
    plt.close()

    # 5. Opportunités (en stock + bon prix + bonne note)
    print("\n💡 OPPORTUNITÉS DÉTECTÉES")
    prix_q1 = df['Prix'].quantile(0.25)  # Premier quartile

    opportunites = df[
        (df['Disponibilite'] == 'En stock') &
        (df['Prix'] < prix_q1) &
        (df['Note'] >= 4)
        ].sort_values('Prix')

    print(f"\nCritères : En stock + Prix < {prix_q1:.2f}€ (Q1) + Note ≥ 4/5")
    print(f"Nombre d'opportunités : {len(opportunites)}")

    if len(opportunites) > 0:
        print("\nTop 10 opportunités:")
        print(opportunites[['Type', 'Nom', 'Prix', 'Unite', 'Note', 'Fournisseur']].head(10).to_string(index=False))

        economie_moyenne = df['Prix'].mean() - opportunites['Prix'].mean()
        print(f"\n💰 Économie potentielle moyenne : {economie_moyenne:.2f} € par rapport au prix moyen du catalogue")

    return opportunites


# =============================================================================
# PROGRAMME PRINCIPAL - EXERCICE 2
# =============================================================================

def exercice2_main():
    """Programme principal de l'exercice 2"""
    print("=" * 70)
    print("EXERCICE 2 : COLLECTEUR ET ANALYSEUR MARKETBTP")
    print("=" * 70)

    # Liste des fichiers à scraper
    fichiers = ['marketbtp/index.html', 'marketbtp/page2.html', 'marketbtp/page3.html']
    tous_les_produits = []

    # Scraping des 3 pages
    for i, fichier in enumerate(fichiers, 1):
        print(f"\n📄 Scraping page {i}...")
        try:
            produits = scraper_page(fichier)
            tous_les_produits.extend(produits)
            print(f"   ✓ {len(produits)} produits collectés")
        except FileNotFoundError:
            print(f"   ✗ ERREUR : Fichier {fichier} non trouvé")
            print(f"   → Assurez-vous que les fichiers HTML sont dans le dossier 'marketbtp/'")

    if not tous_les_produits:
        print("\n⚠️  Aucun produit collecté. Vérifiez les chemins des fichiers.")
        return None

    # Conversion en DataFrame
    df = pd.DataFrame(tous_les_produits)

    print(f"\n✓ Total de produits collectés : {len(df)}")

    # Nettoyage des données
    print("\n🧹 Nettoyage des données...")
    taille_avant = len(df)
    df = df[df['Prix'] > 0]  # Supprimer les produits sans prix
    df = df.drop_duplicates()  # Supprimer les doublons
    print(f"   ✓ {taille_avant - len(df)} entrées supprimées")
    print(f"   ✓ {len(df)} produits valides")

    # Analyse des données
    analyser_donnees(df)

    # Visualisation
    visualiser_donnees(df)

    # Export CSV
    print(f"\n💾 Export des données...")
    df.to_csv('marketbtp_analyse.csv', index=False, encoding='utf-8')
    print(f"   ✓ Données exportées dans 'marketbtp_analyse.csv'")

    print("\n" + "=" * 70)
    print("EXERCICE 2 TERMINÉ AVEC SUCCÈS")
    print("=" * 70)

    return df


# =============================================================================
# PROGRAMME PRINCIPAL - EXERCICE 3
# =============================================================================

def exercice3_main():
    """Programme principal de l'exercice 3"""
    print("\n" + "=" * 70)
    print("EXERCICE 3 : ANALYSE COMPARATIVE AVANCÉE")
    print("=" * 70)

    # Charger les données du CSV généré par l'exercice 2
    try:
        df = pd.read_csv('marketbtp_analyse.csv')
        print(f"\n✓ Données chargées : {len(df)} produits")
    except FileNotFoundError:
        print("\n⚠️  Fichier 'marketbtp_analyse.csv' non trouvé.")
        print("   → Exécutez d'abord l'exercice 2 pour générer les données.")
        return

    # Analyse comparative
    opportunites = analyse_comparative(df)

    # Export des opportunités
    if opportunites is not None and len(opportunites) > 0:
        print(f"\n💾 Export des opportunités...")
        opportunites.to_csv('opportunites_marketbtp.csv', index=False, encoding='utf-8')
        print(f"   ✓ Opportunités exportées dans 'opportunites_marketbtp.csv'")

    print("\n" + "=" * 70)
    print("EXERCICE 3 TERMINÉ AVEC SUCCÈS")
    print("=" * 70)


# =============================================================================
# MINI-PROJET : DASHBOARD COMPLET
# =============================================================================

class DashboardMarketBTP:
    """Classe pour analyser le marché des matériaux BTP"""

    def __init__(self, dossier_html='marketbtp'):
        self.dossier = dossier_html
        self.df = None
        self.fichiers = ['index.html', 'page2.html', 'page3.html']

    def scraper_catalogue(self):
        """Collecte toutes les données du catalogue"""
        print("📥 Collecte des données en cours...")
        tous_les_produits = []

        for i, fichier in enumerate(self.fichiers, 1):
            chemin = f"{self.dossier}/{fichier}"
            try:
                produits = scraper_page(chemin)
                tous_les_produits.extend(produits)
                print(f"   ✓ Page {i} : {len(produits)} produits")
            except FileNotFoundError:
                print(f"   ✗ Page {i} : Fichier non trouvé")

        self.df = pd.DataFrame(tous_les_produits)
        print(f"   → Total : {len(self.df)} produits collectés")

    def nettoyer_donnees(self):
        """Nettoie et formate les données"""
        print("\n🧹 Nettoyage des données...")
        taille_avant = len(self.df)

        # Supprimer les doublons
        self.df = self.df.drop_duplicates()

        # Supprimer les produits sans prix
        self.df = self.df[self.df['Prix'] > 0]

        print(f"   ✓ {taille_avant - len(self.df)} entrées supprimées")
        print(f"   ✓ {len(self.df)} produits valides")

    def analyser_tendances(self):
        """Analyse les tendances du marché"""
        print("\n" + "=" * 70)
        print("📈 ANALYSE DES TENDANCES")
        print("=" * 70)

        # Prix moyen par catégorie
        tendances = self.df.groupby('Type').agg({
            'Prix': ['mean', 'min', 'max', 'count'],
            'Note': 'mean'
        }).round(2)

        tendances.columns = ['Prix_moyen', 'Prix_min', 'Prix_max', 'Nb_produits', 'Note_moyenne']
        tendances = tendances.sort_values('Prix_moyen', ascending=False)

        print("\nTendances par catégorie:")
        print(tendances)

        return tendances

    def identifier_opportunites(self):
        """Identifie les meilleures opportunités"""
        print("\n" + "=" * 70)
        print("💡 IDENTIFICATION DES OPPORTUNITÉS")
        print("=" * 70)

        # Critères : En stock + Prix < Q1 + Note >= 4
        q1_prix = self.df['Prix'].quantile(0.25)

        opportunites = self.df[
            (self.df['Disponibilite'] == 'En stock') &
            (self.df['Prix'] < q1_prix) &
            (self.df['Note'] >= 4)
            ].copy()

        # Calculer le score qualité/prix
        opportunites['Prix_normalise'] = (opportunites['Prix'] - opportunites['Prix'].min()) / \
                                         (opportunites['Prix'].max() - opportunites['Prix'].min())
        opportunites['Score_QP'] = opportunites['Note'] / (opportunites['Prix_normalise'] + 0.1)
        opportunites = opportunites.sort_values('Score_QP', ascending=False)

        print(f"\nCritères : En stock + Prix < {q1_prix:.2f}€ (Q1) + Note ≥ 4/5")
        print(f"Opportunités trouvées : {len(opportunites)}")

        if len(opportunites) > 0:
            economie = self.df['Prix'].mean() - opportunites['Prix'].mean()
            print(f"Économie potentielle : {economie:.2f} € en moyenne")

            print("\nTop 5 meilleures opportunités:")
            top5 = opportunites[['Type', 'Nom', 'Prix', 'Unite', 'Note', 'Fournisseur']].head(5)
            print(top5.to_string(index=False))

        return opportunites

    def comparer_fournisseurs(self):
        """Compare les fournisseurs"""
        print("\n" + "=" * 70)
        print("🏭 COMPARAISON DES FOURNISSEURS")
        print("=" * 70)

        comparison = self.df.groupby('Fournisseur').agg({
            'Prix': 'mean',
            'Note': 'mean',
            'Nom': 'count'
        }).rename(columns={'Nom': 'Nb_produits'}).round(2)

        comparison['Score'] = (comparison['Note'] / 5) * (1 - comparison['Prix'] / comparison['Prix'].max())
        comparison = comparison.sort_values('Score', ascending=False)

        print("\nClassement des fournisseurs:")
        print(comparison)

        return comparison

    def generer_visualisations(self):
        """Crée le dashboard complet"""
        print("\n📊 Génération du dashboard...")

        fig, axes = plt.subplots(2, 3, figsize=(18, 12))
        fig.suptitle('Dashboard MarketBTP - Analyse Complète',
                     fontsize=20, fontweight='bold', y=0.995)

        # 1. Prix par catégorie
        prix_cat = self.df.groupby('Type')['Prix'].mean().sort_values()
        axes[0, 0].barh(range(len(prix_cat)), prix_cat.values, color='steelblue')
        axes[0, 0].set_yticks(range(len(prix_cat)))
        axes[0, 0].set_yticklabels(prix_cat.index)
        axes[0, 0].set_xlabel('Prix moyen (€)')
        axes[0, 0].set_title('Prix moyen par catégorie', fontweight='bold')
        axes[0, 0].grid(axis='x', alpha=0.3)

        # 2. Distribution des notes
        note_counts = self.df['Note'].value_counts().sort_index()
        axes[0, 1].bar(note_counts.index, note_counts.values, color='orange', edgecolor='black')
        axes[0, 1].set_xlabel('Note (/5)')
        axes[0, 1].set_ylabel('Nombre de produits')
        axes[0, 1].set_title('Distribution des notes', fontweight='bold')
        axes[0, 1].grid(axis='y', alpha=0.3)

        # 3. Top 5 fournisseurs
        top_fourn = self.df['Fournisseur'].value_counts().head(5)
        axes[0, 2].barh(range(len(top_fourn)), top_fourn.values, color='lightgreen')
        axes[0, 2].set_yticks(range(len(top_fourn)))
        axes[0, 2].set_yticklabels(top_fourn.index)
        axes[0, 2].set_xlabel('Nombre de produits')
        axes[0, 2].set_title('Top 5 fournisseurs', fontweight='bold')
        axes[0, 2].grid(axis='x', alpha=0.3)

        # 4. Disponibilité
        dispo_counts = self.df['Disponibilite'].value_counts()
        colors_dispo = {'En stock': 'green', 'Stock limité': 'orange', 'Rupture stock': 'red'}
        colors_list = [colors_dispo.get(x, 'gray') for x in dispo_counts.index]
        axes[1, 0].pie(dispo_counts, labels=dispo_counts.index, autopct='%1.1f%%',
                       colors=colors_list, startangle=90)
        axes[1, 0].set_title('Disponibilité', fontweight='bold')

        # 5. Prix par région
        prix_region = self.df.groupby('Region')['Prix'].mean().sort_values()
        axes[1, 1].bar(range(len(prix_region)), prix_region.values, color='coral')
        axes[1, 1].set_xticks(range(len(prix_region)))
        axes[1, 1].set_xticklabels(prix_region.index, rotation=45, ha='right')
        axes[1, 1].set_ylabel('Prix moyen (€)')
        axes[1, 1].set_title('Prix moyen par région', fontweight='bold')
        axes[1, 1].grid(axis='y', alpha=0.3)

        # 6. Distribution des prix
        axes[1, 2].hist(self.df['Prix'], bins=25, color='purple', alpha=0.7, edgecolor='black')
        axes[1, 2].axvline(self.df['Prix'].mean(), color='red', linestyle='--',
                           linewidth=2, label=f"Moyenne: {self.df['Prix'].mean():.2f}€")
        axes[1, 2].set_xlabel('Prix (€)')
        axes[1, 2].set_ylabel('Fréquence')
        axes[1, 2].set_title('Distribution des prix', fontweight='bold')
        axes[1, 2].legend()
        axes[1, 2].grid(alpha=0.3)

        plt.tight_layout()
        plt.savefig('dashboard_complet.png', dpi=300, bbox_inches='tight')
        print("   ✓ dashboard_complet.png créé")
        plt.close()

    def generer_rapport(self):
        """Génère un rapport texte de synthèse"""
        print("\n📝 Génération du rapport...")

        rapport = []
        rapport.append("=" * 80)
        rapport.append("RAPPORT D'ANALYSE MARKETBTP")
        rapport.append(f"Date : {pd.Timestamp.now().strftime('%d/%m/%Y %H:%M')}")
        rapport.append("=" * 80)
        rapport.append("")

        # Vue d'ensemble
        rapport.append("1. VUE D'ENSEMBLE")
        rapport.append(f"   • Nombre total de produits : {len(self.df)}")
        rapport.append(f"   • Nombre de catégories : {self.df['Type'].nunique()}")
        rapport.append(f"   • Catégories : {', '.join(self.df['Type'].unique())}")
        rapport.append(f"   • Nombre de fournisseurs : {self.df['Fournisseur'].nunique()}")
        rapport.append(f"   • Nombre de régions : {self.df['Region'].nunique()}")
        rapport.append("")

        # Statistiques prix
        rapport.append("2. STATISTIQUES DES PRIX")
        rapport.append(f"   • Prix moyen : {self.df['Prix'].mean():.2f} €")
        rapport.append(f"   • Prix médian : {self.df['Prix'].median():.2f} €")
        rapport.append(f"   • Prix minimum : {self.df['Prix'].min():.2f} €")
        rapport.append(f"   • Prix maximum : {self.df['Prix'].max():.2f} €")
        rapport.append(f"   • Écart-type : {self.df['Prix'].std():.2f} €")
        rapport.append("")

        # Produits extrêmes
        rapport.append("3. PRODUITS EXTRÊMES")
        plus_cher = self.df.loc[self.df['Prix'].idxmax()]
        moins_cher = self.df.loc[self.df['Prix'].idxmin()]
        rapport.append(f"   • Plus cher : {plus_cher['Nom']}")
        rapport.append(f"                {plus_cher['Prix']:.2f} {plus_cher['Unite']} ({plus_cher['Fournisseur']})")
        rapport.append(f"   • Moins cher : {moins_cher['Nom']}")
        rapport.append(f"                 {moins_cher['Prix']:.2f} {moins_cher['Unite']} ({moins_cher['Fournisseur']})")
        rapport.append("")

        # Catégories
        rapport.append("4. ANALYSE PAR CATÉGORIE")
        prix_cat = self.df.groupby('Type').agg({'Prix': 'mean', 'Nom': 'count'}).round(2)
        prix_cat.columns = ['Prix_moyen', 'Nb_produits']
        prix_cat = prix_cat.sort_values('Prix_moyen', ascending=False)
        for idx, row in prix_cat.iterrows():
            rapport.append(f"   • {idx:15s} : {row['Prix_moyen']:8.2f} € (n={int(row['Nb_produits'])})")
        rapport.append("")

        # Opportunités
        rapport.append("5. OPPORTUNITÉS IDENTIFIÉES")
        q1 = self.df['Prix'].quantile(0.25)
        opportunites = self.df[
            (self.df['Disponibilite'] == 'En stock') &
            (self.df['Prix'] < q1) &
            (self.df['Note'] >= 4)
            ]
        rapport.append(f"   • Critères : En stock + Prix < {q1:.2f}€ + Note ≥ 4/5")
        rapport.append(f"   • Nombre d'opportunités : {len(opportunites)}")

        if len(opportunites) > 0:
            economie = self.df['Prix'].mean() - opportunites['Prix'].mean()
            rapport.append(f"   • Économie potentielle : {economie:.2f} € en moyenne")
            rapport.append("")
            rapport.append("   Top 3 recommandations :")
            for i, row in opportunites.head(3).iterrows():
                rapport.append(f"     {i + 1}. {row['Nom']}")
                rapport.append(
                    f"        {row['Prix']:.2f} {row['Unite']} - {row['Fournisseur']} - Note: {row['Note']}/5")
        rapport.append("")

        # Qualité
        rapport.append("6. QUALITÉ GLOBALE")
        rapport.append(f"   • Note moyenne : {self.df['Note'].mean():.2f}/5")
        rapport.append(f"   • Note médiane : {self.df['Note'].median():.1f}/5")
        dispo = self.df['Disponibilite'].value_counts()
        total = len(self.df)
        rapport.append(f"   • Disponibilité :")
        for k, v in dispo.items():
            rapport.append(f"     - {k}: {v} produits ({v / total * 100:.1f}%)")
        rapport.append("")

        rapport.append("=" * 80)
        rapport.append("FIN DU RAPPORT")
        rapport.append("=" * 80)

        # Sauvegarder
        contenu = '\n'.join(rapport)
        with open('rapport_marketbtp.txt', 'w', encoding='utf-8') as f:
            f.write(contenu)

        print("   ✓ rapport_marketbtp.txt créé")

        # Afficher
        print("\n" + contenu)

    def exporter_donnees(self):
        """Exporte tous les résultats"""
        print("\n💾 Export des données...")

        # CSV principal
        self.df.to_csv('marketbtp_complet.csv', index=False, encoding='utf-8')
        print("   ✓ marketbtp_complet.csv")

        # Opportunités
        q1 = self.df['Prix'].quantile(0.25)
        opportunites = self.df[
            (self.df['Disponibilite'] == 'En stock') &
            (self.df['Prix'] < q1) &
            (self.df['Note'] >= 4)
            ]

        if len(opportunites) > 0:
            opportunites.to_csv('opportunites.csv', index=False, encoding='utf-8')
            print("   ✓ opportunites.csv")

    def executer_analyse_complete(self):
        """Exécute le pipeline complet d'analyse"""
        print("=" * 70)
        print("DASHBOARD MARKETBTP - ANALYSE COMPLÈTE")
        print("=" * 70)

        self.scraper_catalogue()
        self.nettoyer_donnees()
        self.analyser_tendances()
        self.identifier_opportunites()
        self.comparer_fournisseurs()
        self.generer_visualisations()
        self.generer_rapport()
        self.exporter_donnees()

        print("\n" + "=" * 70)
        print("✅ ANALYSE TERMINÉE AVEC SUCCÈS")
        print("=" * 70)


def mini_projet_main():
    """Programme principal du mini-projet"""
    dashboard = DashboardMarketBTP(dossier_html='marketbtp')
    dashboard.executer_analyse_complete()


# =============================================================================
# POINT D'ENTRÉE PRINCIPAL
# =============================================================================

if __name__ == "__main__":
    import sys

    print("\n" + "=" * 70)
    print("TD4 : WEB SCRAPING AVANCÉ ET ANALYSE DE DONNÉES")
    print("=" * 70)
    print("\nChoisissez l'exercice à exécuter:")
    print("  1. Exercice 2 : Scraper et analyser MarketBTP")
    print("  2. Exercice 3 : Analyse comparative avancée")
    print("  3. Mini-projet : Dashboard complet")
    print("  4. Tout exécuter")

    choix = input("\nVotre choix (1-4): ").strip()

    if choix == '1':
        df = exercice2_main()
    elif choix == '2':
        exercice3_main()
    elif choix == '3':
        mini_projet_main()
    elif choix == '4':
        print("\n🚀 Exécution complète de tous les exercices...")
        df = exercice2_main()
        if df is not None:
            exercice3_main()
            mini_projet_main()
    else:
        print("❌ Choix invalide")

    print("\n✅ Programme terminé!")