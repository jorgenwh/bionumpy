import sys
import time

from bionumpy.parser import BufferedNumpyParser
from bionumpy.kmers import TwoBitHash

k = 31
#cuda = True 
cuda = int(sys.argv[2])
print(f"cuda: {cuda}")

parser = BufferedNumpyParser.from_filename(sys.argv[1], chunk_size=10000000)
hasher = TwoBitHash(k=k, is_cuda=cuda)

t = time.time_ns()
for chunk in parser.get_chunks():
    #Can move data to gpu already here
    #chunk is FileBuffer object
    if cuda:
        chunk.to_cuda()

    sequences = chunk.get_sequences()

    kmers = hasher.get_kmer_hashes(sequences)
    print(kmers)
    # kmers can be passed to counter

print(f"time: {time.time_ns() - t}")