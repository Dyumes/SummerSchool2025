import pretty_midi
import os
import matplotlib.pyplot as plt

""" Module for comparing two MIDI files using Longest Common Subsequence (LCS) algorithm without considering instruments."""
def extract_sequence(midi_path):
    pm = pretty_midi.PrettyMIDI(midi_path)
    notes = []
    for instrument in pm.instruments:
        for note in instrument.notes:
            notes.append((note.start, note.pitch % 12))

    notes.sort(key=lambda note: note[0])

    sorted_notes = []
    for _, pitch in notes:
        sorted_notes.append(pitch)

    return sorted_notes


def lcs(sequence1, sequence2):
    rows = len(sequence1)
    columns = len(sequence2)

    # Create a matrix to store the length of common subsequence for different parts of the sequences
    subsequence_lengths = [[0] * (columns + 1) for _ in range(rows + 1)]

    # Fill the matrix
    for row in range(rows):
        for col in range(columns):
            if sequence1[row] == sequence2[col]:
                # If current elements match, add 1 to the result from the previous elements of both sequences
                subsequence_lengths[row + 1][col + 1] = subsequence_lengths[row][col] + 1
            else:
                # If current elements don't match, take the maximum from either skipping an element from sequence1 or sequence2
                subsequence_lengths[row + 1][col + 1] = max(
                    subsequence_lengths[row + 1][col],  # Skip current element in sequence2
                    subsequence_lengths[row][col + 1]  # Skip current element in sequence1
                )

    # The bottom-right cell contains the length of the LCS
    return subsequence_lengths[rows][columns]

def compare_midis(midi1, midi2):
    seq1 = extract_sequence(midi1)
    seq2 = extract_sequence(midi2)

    common_length = lcs(seq1, seq2)

    percentage = (2 * common_length) / (len(seq1) + len(seq2)) * 100
    return percentage, common_length, len(seq1), len(seq2)

def extract_sequence_with_details(midi_path):
    pm = pretty_midi.PrettyMIDI(midi_path)
    notes = []

    for instrument in pm.instruments:
        for note in instrument.notes:
            notes.append({
                'start': note.start,
                'end': note.end,
                'pitch': note.pitch % 12,
                'octave': note.pitch // 12,
                'velocity': note.velocity,
                'duration': note.end - note.start
            })

    notes.sort(key=lambda x: x['start'])

    pitch_seq = [note['pitch'] for note in notes]
    time_seq = [note['start'] for note in notes]
    duration_seq = [note['duration'] for note in notes]
    velocity_seq = [note['velocity'] for note in notes]

    return pitch_seq, time_seq, duration_seq, velocity_seq

def get_lcs_indices(seq1, seq2):
    n, m = len(seq1), len(seq2)
    dp = [[0] * (m + 1) for _ in range(n + 1)]

    # Fill the DP table
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            if seq1[i - 1] == seq2[j - 1]:
                dp[i][j] = dp[i - 1][j - 1] + 1
            else:
                dp[i][j] = max(dp[i - 1][j], dp[i][j - 1])

    # Backtrack to find the indices of the LCS
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

def detailed_comparison_visualizer(midi1, midi2, title="Detailed MIDI Comparison", method="lcs"):
        pitch_seq1, time_seq1, duration_seq1, velocity_seq1 = extract_sequence_with_details(midi1)
        pitch_seq2, time_seq2, duration_seq2, velocity_seq2 = extract_sequence_with_details(midi2)

        percentage, metric_value, _, _ = compare_midis(midi1, midi2)
        metric_name = "LCS"
        indices1, indices2 = get_lcs_indices(pitch_seq1, pitch_seq2)

        # Création d'un seul graphique
        plt.figure(figsize=(12, 8))

        file_names = [os.path.basename(midi1), os.path.basename(midi2)]
        note_names = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']

        # Créer des ensembles pour les indices communs
        common_indices1 = set(indices1)
        common_indices2 = set(indices2)

        # Notes non communes du premier fichier (bleues)
        non_common_times1 = [time for idx, time in enumerate(time_seq1) if idx not in common_indices1]
        non_common_pitches1 = [pitch for idx, pitch in enumerate(pitch_seq1) if idx not in common_indices1]
        plt.scatter(non_common_times1, non_common_pitches1, s=70, c='royalblue', alpha=0.7,
                    label=f"{file_names[0]} uniquement", marker='o', edgecolors='navy')

        # Notes non communes du deuxième fichier (vertes)
        non_common_times2 = [time for idx, time in enumerate(time_seq2) if idx not in common_indices2]
        non_common_pitches2 = [pitch for idx, pitch in enumerate(pitch_seq2) if idx not in common_indices2]
        plt.scatter(non_common_times2, non_common_pitches2, s=70, c='forestgreen', alpha=0.7,
                    label=f"{file_names[1]} uniquement", marker='s', edgecolors='darkgreen')

        # Notes communes (rouges)
        common_times1 = [time_seq1[i] for i in indices1]
        common_pitches1 = [pitch_seq1[i] for i in indices1]
        plt.scatter(common_times1, common_pitches1, s=100, c='red', alpha=0.8,
                    label='Notes communes', marker='*', edgecolors='darkred')

        # Configuration du graphique
        plt.title(f"{title}\nSimilarité: {percentage:.1f}% ({metric_name}: {metric_value})", fontsize=16)
        plt.yticks(range(12), note_names)
        plt.ylabel('Note')
        plt.xlabel('Temps (secondes)')
        plt.grid(True, linestyle='--', alpha=0.7)
        plt.legend(loc='upper right')

        plt.tight_layout()

        # Enregistrement de l'image
        file_name = os.path.join("media", f"comparison_merged_{method}_{os.path.basename(midi1)}_{os.path.basename(midi2)}.png")
        plt.savefig(file_name)
        print(f"Visualisation sauvegardée sous {file_name}")

        plt.show()

def split_comparison_visualizer(midi1, midi2, title="Detailed MIDI Comparison", method="lcs"):
    pitch_seq1, time_seq1, duration_seq1, velocity_seq1 = extract_sequence_with_details(midi1)
    pitch_seq2, time_seq2, duration_seq2, velocity_seq2 = extract_sequence_with_details(midi2)

    percentage, metric_value, _, _ = compare_midis(midi1, midi2)
    metric_name = "LCS"
    indices1, indices2 = get_lcs_indices(pitch_seq1, pitch_seq2)

    # Création de deux sous-graphiques
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10), sharex=True)

    file_names = [os.path.basename(midi1), os.path.basename(midi2)]
    note_names = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']

    # Premier graphique - Fichier 1
    ax1.scatter(time_seq1, pitch_seq1, s=70, c='royalblue', alpha=0.7,
                label=f"{file_names[0]}", marker='o', edgecolors='navy')

    # Notes communes sur le premier graphique
    if indices1:
        common_times1 = [time_seq1[i] for i in indices1]
        common_pitches1 = [pitch_seq1[i] for i in indices1]
        ax1.scatter(common_times1, common_pitches1, s=100, c='red', alpha=0.8,
                   marker='*', label='Notes communes', edgecolors='darkred')

    ax1.set_title(f"{file_names[0]}", fontsize=12)
    ax1.set_yticks(range(12))
    ax1.set_yticklabels(note_names)
    ax1.set_ylabel('Note')
    ax1.grid(True, linestyle='--', alpha=0.7)
    ax1.legend(loc='upper right')

    # Deuxième graphique - Fichier 2
    ax2.scatter(time_seq2, pitch_seq2, s=70, c='forestgreen', alpha=0.7,
                label=f"{file_names[1]}", marker='s', edgecolors='darkgreen')

    # Notes communes sur le deuxième graphique
    if indices2:
        common_times2 = [time_seq2[i] for i in indices2]
        common_pitches2 = [pitch_seq2[i] for i in indices2]
        ax2.scatter(common_times2, common_pitches2, s=100, c='red', alpha=0.8,
                   marker='*', label='Notes communes', edgecolors='darkred')

    ax2.set_title(f"{file_names[1]}", fontsize=12)
    ax2.set_yticks(range(12))
    ax2.set_yticklabels(note_names)
    ax2.set_xlabel('Temps (secondes)')
    ax2.set_ylabel('Note')
    ax2.grid(True, linestyle='--', alpha=0.7)
    ax2.legend(loc='upper right')

    # Titre global
    fig.suptitle(f"{title}\nSimilarité: {percentage:.1f}% ({metric_name}: {metric_value})",
                fontsize=16, y=0.98)

    plt.tight_layout()
    fig.subplots_adjust(top=0.9)

    # Enregistrement de l'image
    file_name = os.path.join("media", f"comparison_split_{method}_{os.path.basename(midi1)}_{os.path.basename(midi2)}.png")
    plt.savefig(file_name)
    print(f"Visualisation séparée sauvegardée sous {file_name}")

    plt.show()


""" Module for comparing two MIDI files using Longest Common Subsequence (LCS) algorithm with considering instruments."""
def extract_sequence_instruments(midi_path):
    pm = pretty_midi.PrettyMIDI(midi_path)
    notes = []
    for instrument in pm.instruments:
        for note in instrument.notes:
            notes.append((note.start, note.pitch % 12, instrument.program))  # Include instrument program

    notes.sort(key=lambda note: note[0])

    sorted_notes = []
    for _, pitch, program in notes:
        sorted_notes.append((pitch, program))  # Include pitch and instrument program in the sequence

    return sorted_notes

def lcs_with_instruments(sequence1, sequence2):
    rows = len(sequence1)
    columns = len(sequence2)

    # Création de la matrice pour stocker les longueurs des sous-séquences communes
    subsequence_lengths = [[0] * (columns + 1) for _ in range(rows + 1)]

    # Remplissage de la matrice
    for row in range(rows):
        for col in range(columns):
            # Comparaison des tuples (hauteur de note, programme d'instrument)
            if sequence1[row] == sequence2[col]:
                subsequence_lengths[row + 1][col + 1] = subsequence_lengths[row][col] + 1
            else:
                subsequence_lengths[row + 1][col + 1] = max(
                    subsequence_lengths[row + 1][col],
                    subsequence_lengths[row][col + 1]
                )

    return subsequence_lengths[rows][columns]

def compare_midis_instruments(midi1, midi2):
    seq1 = extract_sequence_instruments(midi1)
    seq2 = extract_sequence_instruments(midi2)

    common_length = lcs_with_instruments(seq1, seq2)

    percentage = (2 * common_length) / (len(seq1) + len(seq2)) * 100
    return percentage, common_length, len(seq1), len(seq2)



if __name__ == "__main__":
    midi_a = os.path.join("media", "midi", "test_output_clean.mid")
    midi_b = os.path.join("media", "midi", "Gamme.mid")

    similarity, lcs_len, len1, len2 = compare_midis(midi_a, midi_b)
    print("--- Without Instruments ---")
    print(f"Similarity: {similarity:.2f}%")
    print(f"Common notes in the longest sequence: {lcs_len}")
    print(f"Generated sequence size: {len1}, Original sequence size: {len2}")

    print("--- With Instruments ---")
    similarity_inst, lcs_len_inst, len1_inst, len2_inst = compare_midis_instruments(midi_a, midi_b)
    print(f"Similarity: {similarity_inst:.2f}%")
    print(f"Common notes in the longest sequence: {lcs_len_inst}")
    print(f"Generated sequence size: {len1_inst}, Original sequence size: {len2_inst}")
    print("-------------------------")

    detailed_comparison_visualizer(midi_a, midi_b, "Detailed comparison between generated and original MIDI")
    split_comparison_visualizer(midi_a, midi_b, "Detailed comparison between generated and original MIDI")
