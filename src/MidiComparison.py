import pretty_midi
import os


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



if __name__ == "__main__":
    midi_a = os.path.join("media", "midi", "test_output_clean.mid")
    midi_b = os.path.join("media", "midi", "PinkPanther.midi")

    similarity, lcs_len, len1, len2 = compare_midis(midi_a, midi_b)
    print(f"Similarity: {similarity:.2f}%")
    print(f"Common notes in the longest sequence: {lcs_len}")
    print(f"Generated sequence size: {len1}, Original sequence size: {len2}")
