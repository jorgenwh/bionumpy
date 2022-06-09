import bionumpy as bnp
from bionumpy.string_matcher import StringMatcher

sequences = bnp.as_sequence_array(["ACGT", "ATGAT"], encoding=bnp.encodings.ACTGEncoding)
matcher = StringMatcher("AT", encoding=bnp.encodings.ACTGEncoding)
print( matcher.rolling_window(sequences) )
