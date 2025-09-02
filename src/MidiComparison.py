import pretty_midi
import os
import matplotlib.pyplot as plt

""" Module pour comparer deux fichiers MIDI en utilisant l'algorithme de la Plus Longue Sous-séquence Commune (PLSC) sans tenir compte des instruments."""
def extraire_sequence(chemin_midi):
    pm = pretty_midi.PrettyMIDI(chemin_midi)
    notes = []
    for instrument in pm.instruments:
        for note in instrument.notes:
            notes.append((note.start, note.pitch % 12))

    notes.sort(key=lambda note: note[0])

    notes_triees = []
    for _, hauteur in notes:
        notes_triees.append(hauteur)

    return notes_triees


def plsc(sequence1, sequence2):
    lignes = len(sequence1)
    colonnes = len(sequence2)

    # Créer une matrice pour stocker la longueur de la sous-séquence commune pour différentes parties des séquences
    longueurs_sous_sequences = [[0] * (colonnes + 1) for _ in range(lignes + 1)]

    # Remplir la matrice
    for ligne in range(lignes):
        for col in range(colonnes):
            if sequence1[ligne] == sequence2[col]:
                # Si les éléments actuels correspondent, ajouter 1 au résultat des éléments précédents des deux séquences
                longueurs_sous_sequences[ligne + 1][col + 1] = longueurs_sous_sequences[ligne][col] + 1
            else:
                # Si les éléments actuels ne correspondent pas, prendre le maximum en sautant un élément de sequence1 ou sequence2
                longueurs_sous_sequences[ligne + 1][col + 1] = max(
                    longueurs_sous_sequences[ligne + 1][col],  # Sauter l'élément actuel dans sequence2
                    longueurs_sous_sequences[ligne][col + 1]   # Sauter l'élément actuel dans sequence1
                )

    # La cellule en bas à droite contient la longueur de la PLSC
    return longueurs_sous_sequences[lignes][colonnes]

def comparer_midis(midi1, midi2):
    seq1 = extraire_sequence(midi1)
    seq2 = extraire_sequence(midi2)

    longueur_commune = plsc(seq1, seq2)

    pourcentage = (2 * longueur_commune) / (len(seq1) + len(seq2)) * 100
    return pourcentage, longueur_commune, len(seq1), len(seq2)

def extraire_sequence_avec_details(chemin_midi):
    pm = pretty_midi.PrettyMIDI(chemin_midi)
    notes = []

    for instrument in pm.instruments:
        for note in instrument.notes:
            notes.append({
                'debut': note.start,
                'fin': note.end,
                'hauteur': note.pitch % 12,
                'octave': note.pitch // 12,
                'vitesse': note.velocity,
                'duree': note.end - note.start
            })

    notes.sort(key=lambda x: x['debut'])

    sequence_hauteur = [note['hauteur'] for note in notes]
    sequence_temps = [note['debut'] for note in notes]
    sequence_duree = [note['duree'] for note in notes]
    sequence_vitesse = [note['vitesse'] for note in notes]

    return sequence_hauteur, sequence_temps, sequence_duree, sequence_vitesse

def obtenir_indices_plsc(seq1, seq2):
    n, m = len(seq1), len(seq2)
    dp = [[0] * (m + 1) for _ in range(n + 1)]

    # Remplissage de la table DP
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            if seq1[i - 1] == seq2[j - 1]:
                dp[i][j] = dp[i - 1][j - 1] + 1
            else:
                dp[i][j] = max(dp[i - 1][j], dp[i][j - 1])

    # Retour en arrière pour trouver les indices de la PLSC
    indices1, indices2 = [], []
    i, j = n, m
    while i > 0 and j > 0:
        if seq1[i - 1] == seq2[j - 1]:
            indices1.append(i - 1)
            indices2.append(j - 1)
            i -= 1
            j -= 1
        elif dp[i - 1][j] >= dp[i][j - 1]:
            i -= 1
        else:
            j -= 1

    return list(reversed(indices1)), list(reversed(indices2))

def visualiseur_comparaison_detaillee(midi1, midi2, titre="Comparaison MIDI Détaillée", methode="plsc"):
        sequence_hauteur1, sequence_temps1, sequence_duree1, sequence_vitesse1 = extraire_sequence_avec_details(midi1)
        sequence_hauteur2, sequence_temps2, sequence_duree2, sequence_vitesse2 = extraire_sequence_avec_details(midi2)

        pourcentage, valeur_metrico, _, _ = comparer_midis(midi1, midi2)
        nom_metrico = "PLSC"
        indices1, indices2 = obtenir_indices_plsc(sequence_hauteur1, sequence_hauteur2)

        # Création d'un seul graphique
        plt.figure(figsize=(12, 8))

        noms_fichiers = [os.path.basename(midi1), os.path.basename(midi2)]
        noms_notes = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']

        # Créer des ensembles pour les indices communs
        indices_communs1 = set(indices1)
        indices_communs2 = set(indices2)

        # Notes non communes du premier fichier (bleues)
        temps_non_communs1 = [temps for idx, temps in enumerate(sequence_temps1) if idx not in indices_communs1]
        hauteurs_non_communes1 = [hauteur for idx, hauteur in enumerate(sequence_hauteur1) if idx not in indices_communs1]
        plt.scatter(temps_non_communs1, hauteurs_non_communes1, s=70, c='royalblue', alpha=0.7,
                    label=f"{noms_fichiers[0]} uniquement", marker='o', edgecolors='navy')

        # Notes non communes du deuxième fichier (vertes)
        temps_non_communs2 = [temps for idx, temps in enumerate(sequence_temps2) if idx not in indices_communs2]
        hauteurs_non_communes2 = [hauteur for idx, hauteur in enumerate(sequence_hauteur2) if idx not in indices_communs2]
        plt.scatter(temps_non_communs2, hauteurs_non_communes2, s=70, c='forestgreen', alpha=0.7,
                    label=f"{noms_fichiers[1]} uniquement", marker='s', edgecolors='darkgreen')

        # Notes communes (rouges)
        temps_communs1 = [sequence_temps1[i] for i in indices1]
        hauteurs_communes1 = [sequence_hauteur1[i] for i in indices1]
        plt.scatter(temps_communs1, hauteurs_communes1, s=100, c='red', alpha=0.8,
                    label='Notes communes', marker='*', edgecolors='darkred')

        # Configuration du graphique
        plt.title(f"{titre}\nSimilarité: {pourcentage:.1f}% ({nom_metrico}: {valeur_metrico})", fontsize=16)
        plt.yticks(range(12), noms_notes)
        plt.ylabel('Note')
        plt.xlabel('Temps (secondes)')
        plt.grid(True, linestyle='--', alpha=0.7)
        plt.legend(loc='upper right')

        plt.tight_layout()

        # Enregistrement de l'image
        nom_fichier = os.path.join("media", "graphs", f"comparison_merged_{methode}_{os.path.basename(midi1)}_{os.path.basename(midi2)}.png")
        plt.savefig(nom_fichier)
        print(f"Visualisation sauvegardée sous {nom_fichier}")

        plt.show()

def visualiseur_comparaison_separee(midi1, midi2, titre="Comparaison MIDI Détaillée", methode="plsc"):
    sequence_hauteur1, sequence_temps1, sequence_duree1, sequence_vitesse1 = extraire_sequence_avec_details(midi1)
    sequence_hauteur2, sequence_temps2, sequence_duree2, sequence_vitesse2 = extraire_sequence_avec_details(midi2)

    pourcentage, valeur_metrico, _, _ = comparer_midis(midi1, midi2)
    nom_metrico = "PLSC"
    indices1, indices2 = obtenir_indices_plsc(sequence_hauteur1, sequence_hauteur2)

    # Création de deux sous-graphiques
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10), sharex=True)

    noms_fichiers = [os.path.basename(midi1), os.path.basename(midi2)]
    noms_notes = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']

    # Premier graphique - Fichier 1
    ax1.scatter(sequence_temps1, sequence_hauteur1, s=70, c='royalblue', alpha=0.7,
                label=f"{noms_fichiers[0]}", marker='o', edgecolors='navy')

    # Notes communes sur le premier graphique
    if indices1:
        temps_communs1 = [sequence_temps1[i] for i in indices1]
        hauteurs_communes1 = [sequence_hauteur1[i] for i in indices1]
        ax1.scatter(temps_communs1, hauteurs_communes1, s=100, c='red', alpha=0.8,
                   marker='*', label='Notes communes', edgecolors='darkred')

    ax1.set_title(f"{noms_fichiers[0]}", fontsize=12)
    ax1.set_yticks(range(12))
    ax1.set_yticklabels(noms_notes)
    ax1.set_ylabel('Note')
    ax1.grid(True, linestyle='--', alpha=0.7)
    ax1.legend(loc='upper right')

    # Deuxième graphique - Fichier 2
    ax2.scatter(sequence_temps2, sequence_hauteur2, s=70, c='forestgreen', alpha=0.7,
                label=f"{noms_fichiers[1]}", marker='s', edgecolors='darkgreen')

    # Notes communes sur le deuxième graphique
    if indices2:
        temps_communs2 = [sequence_temps2[i] for i in indices2]
        hauteurs_communes2 = [sequence_hauteur2[i] for i in indices2]
        ax2.scatter(temps_communs2, hauteurs_communes2, s=100, c='red', alpha=0.8,
                   marker='*', label='Notes communes', edgecolors='darkred')

    ax2.set_title(f"{noms_fichiers[1]}", fontsize=12)
    ax2.set_yticks(range(12))
    ax2.set_yticklabels(noms_notes)
    ax2.set_xlabel('Temps (secondes)')
    ax2.set_ylabel('Note')
    ax2.grid(True, linestyle='--', alpha=0.7)
    ax2.legend(loc='upper right')

    # Titre global
    fig.suptitle(f"{titre}\nSimilarité: {pourcentage:.1f}% ({nom_metrico}: {valeur_metrico})",
                fontsize=16, y=0.98)

    plt.tight_layout()
    fig.subplots_adjust(top=0.9)

    # Enregistrement de l'image
    nom_fichier = os.path.join("media", "graphs", f"comparison_split_{methode}_{os.path.basename(midi1)}_{os.path.basename(midi2)}.png")
    plt.savefig(nom_fichier)
    print(f"Visualisation séparée sauvegardée sous {nom_fichier}")

    plt.show()


""" Module pour comparer deux fichiers MIDI en utilisant l'algorithme de la Plus Longue Sous-séquence Commune (PLSC) en tenant compte des instruments."""
def extraire_sequence_instruments(chemin_midi):
    pm = pretty_midi.PrettyMIDI(chemin_midi)
    notes = []
    for instrument in pm.instruments:
        for note in instrument.notes:
            notes.append((note.start, note.pitch % 12, instrument.program))

    notes.sort(key=lambda note: note[0])

    notes_triees = []
    for _, pitch, program in notes:
        notes_triees.append((pitch, program))

    return notes_triees

def plsc_avec_instruments(sequence1, sequence2):
    lignes = len(sequence1)
    colonnes = len(sequence2)

    # Création de la matrice pour stocker les longueurs des sous-séquences communes
    longueurs_sous_sequences = [[0] * (colonnes + 1) for _ in range(lignes + 1)]

    # Remplissage de la matrice
    for ligne in range(lignes):
        for col in range(colonnes):
            # Comparaison des tuples (hauteur de note, programme d'instrument)
            if sequence1[ligne] == sequence2[col]:
                longueurs_sous_sequences[ligne + 1][col + 1] = longueurs_sous_sequences[ligne][col] + 1
            else:
                longueurs_sous_sequences[ligne + 1][col + 1] = max(
                    longueurs_sous_sequences[ligne + 1][col],
                    longueurs_sous_sequences[ligne][col + 1]
                )

    return longueurs_sous_sequences[lignes][colonnes]

def comparer_midis_instruments(midi1, midi2):
    seq1 = extraire_sequence_instruments(midi1)
    seq2 = extraire_sequence_instruments(midi2)

    longueur_commune = plsc_avec_instruments(seq1, seq2)

    pourcentage = (2 * longueur_commune) / (len(seq1) + len(seq2)) * 100
    return pourcentage, longueur_commune, len(seq1), len(seq2)


""" Test de similarité rythmique entre deux fichiers MIDI """
def extraire_sequence_rythme(chemin_midi):
    pm = pretty_midi.PrettyMIDI(chemin_midi)
    notes = []
    for instrument in pm.instruments:
        for note in instrument.notes:
            notes.append((note.start, note.end - note.start))  # (temps de début, durée)

    notes.sort(key=lambda note: note[0])

    # Quantifier les durées pour simplifier la comparaison
    durees = []
    prev_start = notes[0][0] if notes else 0
    for start, duration in notes:
        # Ajouter l'intervalle entre les notes et la durée
        durees.append((round((start - prev_start) * 4) / 4, round(duration * 4) / 4))
        prev_start = start

    return durees

def comparer_midis_rythme(midi1, midi2):
    seq1 = extraire_sequence_rythme(midi1)
    seq2 = extraire_sequence_rythme(midi2)

    # Calculer la distance d'édition entre les séquences rythmiques
    from difflib import SequenceMatcher
    matcher = SequenceMatcher(None, seq1, seq2)
    similarite = matcher.ratio() * 100

    return similarite


""" Test d'analyse mélodique par intervalles entre deux fichiers MIDI """
def extraire_sequence_intervalles(chemin_midi):
    pm = pretty_midi.PrettyMIDI(chemin_midi)
    notes = []
    for instrument in pm.instruments:
        for note in instrument.notes:
            notes.append((note.start, note.pitch))

    notes.sort(key=lambda note: note[0])
    hauteurs = [pitch for _, pitch in notes]

    # Calculer les intervalles entre notes consécutives
    intervalles = []
    for i in range(1, len(hauteurs)):
        intervalles.append(hauteurs[i] - hauteurs[i-1])

    return intervalles

def comparer_midis_intervalles(midi1, midi2):
    seq1 = extraire_sequence_intervalles(midi1)
    seq2 = extraire_sequence_intervalles(midi2)

    longueur_commune = plsc(seq1, seq2)
    pourcentage = (2 * longueur_commune) / (len(seq1) + len(seq2)) * 100 if (len(seq1) + len(seq2)) > 0 else 0

    return pourcentage, longueur_commune, len(seq1), len(seq2)


""" Visualisation par densité de notes dans deux fichiers MIDI """
def comparaison_densite_notes(midi1, midi2, titre="Comparaison de Densité Temporelle"):
        """
        Crée un histogramme montrant la distribution temporelle des notes pour deux fichiers MIDI,
        avec alignement temporel pour une comparaison directe.
        """
        # Extraction des données temporelles des deux fichiers
        sequence_hauteur1, sequence_temps1, sequence_duree1, _ = extraire_sequence_avec_details(midi1)
        sequence_hauteur2, sequence_temps2, sequence_duree2, _ = extraire_sequence_avec_details(midi2)

        # Création d'une figure de taille adaptée
        fig, ax = plt.subplots(figsize=(14, 8))

        # Noms des fichiers pour la légende
        noms_fichiers = [os.path.basename(midi1), os.path.basename(midi2)]

        # Calcul de la durée totale pour définir l'axe x
        debut_temps1 = min(sequence_temps1) if sequence_temps1 else 0
        debut_temps2 = min(sequence_temps2) if sequence_temps2 else 0
        fin_temps1 = max(sequence_temps1) if sequence_temps1 else 0
        fin_temps2 = max(sequence_temps2) if sequence_temps2 else 0

        min_debut = min(debut_temps1, debut_temps2)
        max_fin = max(fin_temps1, fin_temps2)

        # Définir des intervalles identiques pour les deux histogrammes pour un alignement parfait
        n_bins = min(int(max_fin - min_debut) + 1, 40)  # Maximum 40 bins
        bords_bins = [min_debut + i * (max_fin - min_debut) / n_bins for i in range(n_bins + 1)]

        # Histogramme de densité temporelle avec des couleurs distinctes
        comptes1, bins1, _ = ax.hist(sequence_temps1, bins=bords_bins, alpha=0.7, label=f"{noms_fichiers[0]}",
                                   color='royalblue', edgecolor='navy', linewidth=1.2)
        comptes2, bins2, _ = ax.hist(sequence_temps2, bins=bords_bins, alpha=0.7, label=f"{noms_fichiers[1]}",
                                   color='forestgreen', edgecolor='darkgreen', linewidth=1.2)

        # Amélioration des étiquettes et de la présentation
        ax.set_xlabel('Temps (secondes)', fontsize=12)
        ax.set_ylabel('Nombre de notes par intervalle de temps', fontsize=12)
        ax.set_title('Distribution temporelle des notes\n(Alignement temporel pour comparaison directe)', fontsize=14)

        # Marquer les points de début et fin des morceaux
        ax.axvline(x=debut_temps1, color='royalblue', linestyle='--', alpha=0.6)
        ax.axvline(x=fin_temps1, color='royalblue', linestyle=':', alpha=0.6)
        ax.axvline(x=debut_temps2, color='forestgreen', linestyle='--', alpha=0.6)
        ax.axvline(x=fin_temps2, color='forestgreen', linestyle=':', alpha=0.6)

        # Calcul et affichage des informations supplémentaires
        temps_total1 = fin_temps1 - debut_temps1
        temps_total2 = fin_temps2 - debut_temps2
        duree_moyenne1 = sum(sequence_duree1) / len(sequence_duree1) if sequence_duree1 else 0
        duree_moyenne2 = sum(sequence_duree2) / len(sequence_duree2) if sequence_duree2 else 0

        # Calcul des densités (notes par seconde)
        densite1 = len(sequence_temps1) / temps_total1 if temps_total1 > 0 else 0
        densite2 = len(sequence_temps2) / temps_total2 if temps_total2 > 0 else 0

        # Légende améliorée avec plus d'informations
        ax.legend(labels=[
            f"{noms_fichiers[0]} ({len(sequence_temps1)} notes, {densite1:.1f} notes/sec)",
            f"{noms_fichiers[1]} ({len(sequence_temps2)} notes, {densite2:.1f} notes/sec)"
        ], loc='upper right', fontsize=11)

        # Grille en arrière-plan pour faciliter la lecture
        ax.grid(True, linestyle='--', alpha=0.6)

        # Affichage des statistiques complètes en bas du graphique
        texte_info = (
            f"Statistiques détaillées:\n\n"
            f"│ {noms_fichiers[0]} │ Durée: {temps_total1:.2f}s │ Notes: {len(sequence_temps1)} │ Densité: {densite1:.2f} notes/sec │ Durée moyenne: {duree_moyenne1:.3f}s │\n\n"
            f"│ {noms_fichiers[1]} │ Durée: {temps_total2:.2f}s │ Notes: {len(sequence_temps2)} │ Densité: {densite2:.2f} notes/sec │ Durée moyenne: {duree_moyenne2:.3f}s │"
        )

        plt.figtext(0.5, 0.01, texte_info, fontsize=10, ha='center',
                   bbox=dict(boxstyle="round,pad=0.5", facecolor="white", alpha=0.8))

        plt.tight_layout()
        plt.subplots_adjust(bottom=0.2)

        # Sauvegarde de l'image
        nom_fichier = os.path.join("media", "graphs", f"densite_temporelle_{os.path.basename(midi1)}_{os.path.basename(midi2)}.png")
        plt.savefig(nom_fichier)
        print(f"Analyse de densité temporelle sauvegardée sous {nom_fichier}")

        plt.show()




if __name__ == "__main__":
    midi_a = os.path.join("media", "midi", "test_output_clean.mid")
    midi_b = os.path.join("media", "midi", "SuperMario.mid")

    similarite, lcs_len, len1, len2 = comparer_midis(midi_a, midi_b)
    print("--- Sans Instruments ---")
    print(f"Similarité: {similarite:.2f}%")
    print(f"Notes communes dans la plus longue séquence: {lcs_len}")
    print(f"Taille de la séquence générée: {len1}, Taille de la séquence originale: {len2}")
    print("-------------------------\n")

    print("--- Avec Instruments ---")
    similarite_inst, lcs_len_inst, len1_inst, len2_inst = comparer_midis_instruments(midi_a, midi_b)
    print(f"Similarité: {similarite_inst:.2f}%")
    print(f"Notes communes dans la plus longue séquence: {lcs_len_inst}")
    print(f"Taille de la séquence générée: {len1_inst}, Taille de la séquence originale: {len2_inst}")
    print("-------------------------\n")

    print("--- Similarité Rythmique ---")
    similarite_rythme = comparer_midis_rythme(midi_a, midi_b)
    print(f"Similarité rythmique: {similarite_rythme:.2f}%")
    print("-------------------------\n")

    print("--- Similarité par Intervalles ---")
    similarite_intervalle, commun_intervalles, len_int1, len_int2 = comparer_midis_intervalles(midi_a, midi_b)
    print(f"Similarité: {similarite_intervalle:.2f}%")
    print(f"Intervalles communs dans la plus longue séquence: {commun_intervalles}")
    print(f"Taille de la séquence d'intervalles générée: {len_int1}, Taille de la séquence d'intervalles originale: {len_int2}")
    print("-------------------------\n")

    print("--- Analyse de Densité de Notes ---")
    comparaison_densite_notes(midi_a, midi_b, "Densité de notes entre MIDI généré et original")
    print("-------------------------\n")



    visualiseur_comparaison_detaillee(midi_a, midi_b, "Comparaison détaillée entre MIDI généré et original")
    visualiseur_comparaison_separee(midi_a, midi_b, "Comparaison détaillée entre MIDI généré et original")
