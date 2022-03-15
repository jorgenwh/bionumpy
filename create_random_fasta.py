import sys
import random

def generate_random_sequence(num_bases):
    bases = ["A", "C", "G", "T"]
    sequence = ""
    for _ in range(num_bases):
        sequence += random.choice(bases)
    return sequence

if __name__ == "__main__":
    output_filename = sys.argv[1]
    num_bases = int(sys.argv[2])
    num_lines = int(sys.argv[3])

    assert num_bases >= num_lines 

    remaining = num_bases
    f = open(output_filename, "w")

    while remaining > 0:
        n = min(num_bases // num_lines, remaining)
        sequence = generate_random_sequence(n)
        f.write(f">Randomly generated sequence of {num_bases} base-pairs.\n")
        f.write(sequence)

        remaining -= n

    f.close()
    print("File generated.")

