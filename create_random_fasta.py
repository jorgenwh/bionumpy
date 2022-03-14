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
    
    sequence = generate_random_sequence(num_bases)

    f = open(output_filename, "w")
    f.write(f">Randomly generated sequence of {num_bases} base-pairs.\n")
    f.write(sequence)
    f.close()

    print("File generated.")

