import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Charger les donnees du CSV genere
df = pd.read_csv('marketbtp_analyse.csv')

print("="*60)
print("ANALYSE COMPARATIVE AVANCEE")
print("="*60)

# 1. Analyse par region
print("\n--- PRIX MOYEN PAR REGION ---")
prix_region = df.groupby('Region')['Prix'].agg(['mean', 'median', 'count'])
print(prix_region)

# Graphique
plt.figure(figsize=(10, 6))
prix_region['mean'].plot(kind='bar', color='skyblue', edgecolor='black')
plt.title('Prix moyen par region', fontsize=14, fontweight='bold')
plt.ylabel('Prix moyen (euros)')
plt.xlabel('Region')
plt.xticks(rotation=45, ha='right')
plt.tight_layout()
plt.savefig('prix_par_region.png', dpi=300)
plt.show()

# 2. Rapport qualite/prix
print("\n--- RAPPORT QUALITE/PRIX ---")
# Calculer un score : Note / Prix (normalise)
df['Score_QP'] = df['Note'] / (df['Prix'] / df['Prix'].mean())

# Top 10 meilleurs rapports qualite/prix
top_qp = df.nlargest(10, 'Score_QP')[['Nom', 'Prix', 'Note', 'Score_QP']]
print("\nTop 10 meilleurs rapports qualite/prix :")
print(top_qp)

# 3. Opportunites (En stock + Prix < moyenne)
print("\n--- OPPORTUNITES ---")
prix_moyen = df['Prix'].mean()
opportunites = df[
    (df['Disponibilite'] == 'En stock') &
    (df['Prix'] < prix_moyen) &
    (df['Note'] >= 4)
].sort_values('Prix')

print(f"\n{len(opportunites)} opportunites detectees")
print(opportunites[['Type', 'Nom', 'Prix', 'Fournisseur']].head(10))

# Sauvegarder le rapport
opportunites.to_csv('opportunites_marketbtp.csv',
                    index=False, encoding='utf-8')
print("\nRapport sauvegarde dans 'opportunites_marketbtp.csv'")
