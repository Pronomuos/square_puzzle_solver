import numpy as np

import image_utils
from piece import RotatedPiece, calc_side
from analize import ImageAnalysis


class Chromosome(object):
    FITNESS_FACTOR = 1000

    def __init__(self, pieces, rows, columns, shuffle=True):
        self.pieces = pieces
        self.rows = rows
        self.columns = columns
        self._fitness = None

        if shuffle:
            self.pieces = [RotatedPiece(piece) for piece in pieces]
            np.random.shuffle(self.pieces)
            for i in range(len(self.pieces)):
                self.pieces[i].set_orientation(np.random.randint(0, 4))

        # Map piece ID to index in Individual's list
        self._piece_mapping = {piece.content.id: index for index, piece in enumerate(self.pieces)}

    def __getitem__(self, key):
        return self.pieces[key * self.columns:(key + 1) * self.columns]

    @property
    def fitness(self):
        if self._fitness is None:
            fitness_value = 0
            # For each two adjacent pieces in rows
            for i in range(self.rows):
                for j in range(self.columns - 1):
                    first_piece, second_piece = self[i][j], self[i][j + 1]
                    first_side, second_side = calc_side(first_piece.orientation, 3), calc_side(second_piece.orientation, 1)
                    fitness_value += ImageAnalysis.get_dissimilarity((first_piece.content.id, second_piece.content.id,
                                                                      first_side, second_side))
            # For each two adjacent pieces in columns
            for i in range(self.rows - 1):
                for j in range(self.columns):
                    first_piece, second_piece = self[i][j], self[i + 1][j]
                    first_side, second_side = calc_side(first_piece.orientation, 2), calc_side(second_piece.orientation, 0)
                    fitness_value += ImageAnalysis.get_dissimilarity((first_piece.content.id, second_piece.content.id,
                                                                      first_side, second_side))
            self._fitness = fitness_value

        return self._fitness

    def piece_size(self):
        return self.pieces[0].content.size

    def piece_by_id(self, piece_id):
        return self.pieces[self._piece_mapping[piece_id]]

    def to_image(self):
        pieces = []
        for piece in self.pieces:
            pieces.append(piece.get_rotated_image())
        return image_utils.assemble_image(pieces, self.rows, self.columns)

    def get_adj_piece(self, piece_id, orientation, side):
        piece_index = self._piece_mapping[piece_id]

        side = calc_side(orientation, side)

        if (side == 0) and (piece_index >= self.columns):
            return self.pieces[piece_index - self.columns]

        if (side == 1) and (piece_index % self.columns > 0):
            return self.pieces[piece_index - 1]

        if (side == 2) and (piece_index < (self.rows - 1) * self.columns):
            return self.pieces[piece_index + self.columns]

        if (side == 3) and (piece_index % self.columns < self.columns - 1):
            return self.pieces[piece_index + 1]
