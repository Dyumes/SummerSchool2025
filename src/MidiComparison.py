import pretty_midi
import os
import matplotlib.pyplot as plt


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

    plt.figure(figsize=(12, 6))

    file_names = [os.path.basename(midi1), os.path.basename(midi2)]
    note_names = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']

    plt.subplot(211)
    plt.scatter(time_seq1, pitch_seq1, s=30, c='blue', alpha=0.6, label=file_names[0])
    if indices1:
        plt.scatter([time_seq1[i] for i in indices1], [pitch_seq1[i] for i in indices1],
                    s=40, c='red', marker='*', label='Common notes')
    plt.yticks(range(12), note_names)
    plt.ylabel('Note')
    plt.title(f'Note progression in {file_names[0]}')
    plt.legend()

    plt.subplot(212)
    plt.scatter(time_seq2, pitch_seq2, s=30, c='green', alpha=0.6, label=file_names[1])
    if indices2:
        plt.scatter([time_seq2[i] for i in indices2], [pitch_seq2[i] for i in indices2],
                    s=40, c='red', marker='*', label='Common notes')
    plt.yticks(range(12), note_names)
    plt.ylabel('Note')
    plt.xlabel('Time (seconds)')
    plt.title(f'Note progression in {file_names[1]}')
    plt.legend()

    plt.suptitle(f"{title}\nSimilarity: {percentage:.1f}% ({metric_name}: {metric_value})", fontsize=16)
    plt.tight_layout(rect=[0, 0, 1, 0.95])

    file_name = os.path.join("media", f"comparison_{method}_{os.path.basename(midi1)}_{os.path.basename(midi2)}.png")
    plt.savefig(file_name)
    print(f"Visualization saved as {file_name}")

    plt.show()

if __name__ == "__main__":
    midi_a = os.path.join("media", "midi", "test_output_clean.mid")
    midi_b = os.path.join("media", "midi", "PinkPanther.midi")

    similarity, lcs_len, len1, len2 = compare_midis(midi_a, midi_b)
    print(f"Similarity: {similarity:.2f}%")
    print(f"Common notes in the longest sequence: {lcs_len}")
    print(f"Generated sequence size: {len1}, Original sequence size: {len2}")

    detailed_comparison_visualizer(midi_a, midi_b, "Detailed comparison between generated and original MIDI")
