from .npdataclass import NpDataClass, VarLenArray, SeqArray
from .parser import FileBuffer, NEWLINE
from .bed_parser import *
from dataclasses import dataclass
import numpy as np


class DelimitedBuffer(FileBuffer):
    DELIMITER = ord("\t")
    COMMENT = ord("#")

    def __init__(self, data, new_lines):
        super().__init__(data, new_lines)
        self._delimiters = np.concatenate(([-1],
            np.flatnonzero(self._data == self.DELIMITER),
            self._new_lines))
        self._delimiters.sort(kind="mergesort")

    @classmethod
    def from_raw_buffer(cls, chunk):
        new_lines = np.flatnonzero(chunk==NEWLINE)
        return cls(chunk[:new_lines[-1]+1], new_lines)

    def get_integers(self, cols):
        cols = np.asanyarray(cols)
        integer_starts = self._delimiters[:-1].reshape(-1, self._n_cols)[:, cols]+1
        integer_ends = self._delimiters[1:].reshape(-1, self._n_cols)[:, cols]
        integers = self._extract_integers(integer_starts.ravel(), integer_ends.ravel())
        return integers.reshape(-1, cols.size)

    def _extract_integers(self, integer_starts, integer_ends):
        digit_chars = self._move_intervals_to_2d_array(integer_starts, integer_ends, DigitEncoding.MIN_CODE)
        n_digits = digit_chars.shape[-1]
        powers = np.uint32(10)**np.arange(n_digits)[::-1]
        return DigitEncoding.from_bytes(digit_chars) @ powers

    def get_text(self, col, fixed_length=True):
        self.validate_if_not()
        starts = self._delimiters[:-1].reshape(-1, self._n_cols)[:, col]+1
        ends = self._delimiters[1:].reshape(-1, self._n_cols)[:, col]
        if fixed_length:
            return self._move_intervals_to_2d_array(starts, ends)
        else:
            return self._move_intervals_to_ragged_array(starts, ends)

    def get_text_range(self, col, start=0, end=None):
        self.validate_if_not()
        # delimiters = self._delimiters.reshape(-1, self._n_cols)
        starts = self._delimiters[:-1].reshape(-1, self._n_cols)[:, col]+1+start
        if end is not None:
            ends = starts+end
        else:
            ends = self._delimiters[1:].reshape(-1, self._n_cols)[:, col]
        return self._move_intervals_to_2d_array(starts.ravel(), ends.ravel())

    def _validate(self):
        chunk = self._data
        delimiters = self._delimiters[1:]
        n_delimiters_per_line = next(i for i, d in enumerate(delimiters) if chunk[d] == NEWLINE) + 1
        self._n_cols = n_delimiters_per_line
        last_new_line = next(i for i, d in enumerate(delimiters[::-1]) if chunk[d] == NEWLINE)
        delimiters = delimiters[:delimiters.size-last_new_line]
        assert delimiters.size % n_delimiters_per_line == 0, f"irregular number of delimiters per line ({delimiters.size}, {n_delimiters_per_line})"
        delimiters = delimiters.reshape(-1, n_delimiters_per_line)
        assert np.all(chunk[delimiters[:, -1]] == NEWLINE)
        self._validated = True

class BedBuffer(DelimitedBuffer):
    data_class=SortedIntervals
    def get_intervals(self):
        self.validate_if_not()
        data = self.get_data()
        return Interval(data)

    def get_data(self):
        self.validate_if_not()
        return self.get_integers(cols=[1, 2])

    def get_chromosomes(self):
        self.validate_if_not()
        return self.get_text(col=0)

class VCFBuffer(DelimitedBuffer):
    def get_variants(self, fixed_length=False):
        self.validate_if_not()
        chromosomes = VarLenArray(self.get_text(0))
        position = self.get_integers(1).ravel()-1
        from_seq = self.get_text(3, fixed_length=fixed_length)
        to_seq = self.get_text(4, fixed_length=fixed_length)
        return SNP(chromosomes, position, from_seq, to_seq)

    def get_snps(self):
        return self.get_variants(fixed_length=True)

    def get_data(self):
        self.validate_if_not()
        chromosomes = self.get_text(0)
        position = self.get_integers(1)
        from_seq = self.get_text(3)
        to_seq = self.get_text(4)
        return SNP(chromosomes, position, from_seq.ravel(), to_seq.ravel())


class VCFMatrixBuffer(VCFBuffer):
    def get_entries(self):
        self.validate_if_not()
        chromosomes = self.get_text(0)
        position = self.get_integers(1).ravel()-1
        from_seq = self.get_text(3).ravel()
        to_seq = self.get_text(4).ravel()
        n_samples = self._n_cols-9
        genotypes = self.get_text_range(np.arange(9, self._n_cols), end=3)
        return SNP(chromosomes, position, from_seq, to_seq), GenotypeEncoding.from_bytes(genotypes.reshape(-1, n_samples, 3))

    def get_data(self):
        self.validate_if_not()
        chromosomes = self.get_text(0)
        position = self.get_integers(1)
        from_seq = self.get_text(3)
        to_seq = self.get_text(4)
        return SNP(chromosomes, position, from_seq.ravel(), to_seq.ravel())