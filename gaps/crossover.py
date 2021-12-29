import random
import heapq

from analize import ImageAnalysis
from chromosome import Chromosome
from piece import RotatedPiece, calc_side

SHARED_PIECE_PRIORITY = -10
BUDDY_PIECE_PRIORITY = -1


# 0 stands for top, 1 - left, 2 - down, 3 - right.
def complementary_side(side):
    return {
        0: 2,
        1: 3,
        2: 0,
        3: 1
    }.get(side, None)


def calc_rotations(initial_side, dest_side):
    if initial_side == 0:
        return {
            0: 0,
            1: 1,
            2: 2,
            3: 3
        }.get(dest_side, None)
    if initial_side == 1:
        return {
            0: 3,
            1: 0,
            2: 1,
            3: 2
        }.get(dest_side, None)
    if initial_side == 2:
        return {
            0: 2,
            1: 3,
            2: 0,
            3: 1
        }.get(dest_side, None)
    if initial_side == 3:
        return {
            0: 1,
            1: 2,
            2: 3,
            3: 0
        }.get(dest_side, None)


class Crossover(object):

    def __init__(self, first_parent, second_parent, pieces):
        self._parents = (first_parent, second_parent)
        self._pieces_length = len(first_parent.pieces)
        self._child_rows = first_parent.rows
        self._child_columns = first_parent.columns
        self.pieces = pieces

        # Borders of growing kernel
        self._min_row = 0
        self._max_row = 0
        self._min_column = 0
        self._max_column = 0

        self._kernel = {}
        self._taken_positions = set()

        self._candidate_pieces = []

    def child(self):
        new_pieces = [None] * self._pieces_length

        for piece_id, (position, orientation) in self._kernel.items():
            row, column = position
            index = (row - self._min_row) * self._child_columns + (column - self._min_column)
            new_pieces[index] = RotatedPiece(self.pieces[piece_id], orientation)

        return Chromosome(new_pieces, self._child_rows, self._child_columns, shuffle=False)

    def run(self):
        self._initialize_kernel()

        while len(self._candidate_pieces) > 0 or not self._is_kernel_full():
            p, piece, relative_piece = heapq.heappop(self._candidate_pieces)
            position, piece_id, orientation = piece

            if position in self._taken_positions:
                continue

            if piece_id in self._kernel:
                self.find_piece_candidate(relative_piece[0], relative_piece[1], relative_piece[2], position)
                continue

            self._put_piece_to_kernel(piece_id, orientation, position)

    def _initialize_kernel(self):
        root_piece = self._parents[0].pieces[int(random.uniform(0, self._pieces_length))]
        self._put_piece_to_kernel(root_piece.content.id, root_piece.orientation, (0, 0))

    def _put_piece_to_kernel(self, piece_id, orientation, position):
        self._kernel[piece_id] = (position, orientation)
        self._taken_positions.add(position)
        self._update_candidate_pieces(piece_id, orientation, position)

    def _update_candidate_pieces(self, piece_id, orientation, position):
        available_boundaries = self._available_boundaries(position)

        for side, position in available_boundaries:
            self.find_piece_candidate(piece_id, orientation, side, position)

    def find_piece_candidate(self, piece_id, orientation, side, position):
        shared = self._get_shared_piece(piece_id, orientation, side)
        if shared is not None:
            shared_id, shared_orientation = shared
            if self._is_valid_piece(shared_id):
                self._add_piece_candidate(SHARED_PIECE_PRIORITY, (shared_id, shared_orientation),
                                          position, (piece_id, orientation, side))
                return

        buddy = self._get_buddy_piece(piece_id, orientation, side)
        if buddy is not None:
            buddy_id, buddy_orientation = buddy
            if self._is_valid_piece(buddy_id):
                self._add_piece_candidate(BUDDY_PIECE_PRIORITY, (buddy_id, buddy_orientation), position,
                                          (piece_id, orientation, side))
                return

        priority, best_match_id, best_match_side = self._get_best_match_piece(piece_id, orientation, side)
        best_match_orientation = calc_rotations(best_match_side, complementary_side(side))
        self._add_piece_candidate(priority, (best_match_id, best_match_orientation),
                                  position, (piece_id, orientation, side))
        return

    def _get_shared_piece(self, piece_id, orientation, side):
        first_parent, second_parent = self._parents
        first_parent_piece = first_parent.get_adj_piece(piece_id, orientation, side)
        second_parent_piece = second_parent.get_adj_piece(piece_id, orientation, side)

        if first_parent_piece is None or second_parent_piece is None:
            return

        if first_parent_piece.content.id == second_parent_piece.content.id \
                and first_parent_piece.orientation == second_parent_piece.orientation:
            return first_parent_piece.content.id, first_parent_piece.orientation

    def _get_buddy_piece(self, piece_id, orientation, side):
        correct_side = calc_side(orientation, side)
        first_buddy = ImageAnalysis.best_match_table[piece_id][correct_side][0]
        second_buddy = ImageAnalysis.best_match_table[first_buddy[1]][complementary_side(first_buddy[2])][0]

        if second_buddy[1] == piece_id and second_buddy[2] == correct_side:
            for piece in [parent.get_adj_piece(piece_id, orientation, side) for parent in self._parents]:
                if piece is not None:
                    if piece.content.id == first_buddy[1] and piece.orientation == first_buddy[2]:
                        return piece.content.id, piece.orientation

    def _get_best_match_piece(self, piece_id, orientation, side):
        side = calc_side(orientation, side)
        for dissimilarity_measure, piece_id, side in ImageAnalysis.best_match_table[piece_id][side]:
            if self._is_valid_piece(piece_id):
                return dissimilarity_measure, piece_id, side

    def _add_piece_candidate(self, priority, piece, position, relative_piece):
        piece_candidate = (priority, (position, piece[0], piece[1]), relative_piece)
        heapq.heappush(self._candidate_pieces, piece_candidate)

    def _available_boundaries(self, row_and_column):
        (row, column) = row_and_column
        boundaries = []

        # 0 stands for top, 1 - left, 2 - down, 3 - right.
        if not self._is_kernel_full():
            positions = {
                0: (row - 1, column),
                1: (row, column - 1),
                2: (row + 1, column),
                3: (row, column + 1)
            }

            for side, position in positions.items():
                if position not in self._taken_positions and self._is_in_range(position):
                    self._update_kernel_boundaries(position)
                    boundaries.append((side, position))

        return boundaries

    def _is_kernel_full(self):
        return len(self._kernel) == self._pieces_length

    def _is_in_range(self, row_and_column):
        (row, column) = row_and_column
        return self._is_row_in_range(row) and self._is_column_in_range(column)

    def _is_row_in_range(self, row):
        current_rows = abs(min(self._min_row, row)) + abs(max(self._max_row, row))
        return current_rows < self._child_rows

    def _is_column_in_range(self, column):
        current_columns = abs(min(self._min_column, column)) + abs(max(self._max_column, column))
        return current_columns < self._child_columns

    def _update_kernel_boundaries(self, row_and_column):
        (row, column) = row_and_column
        self._min_row = min(self._min_row, row)
        self._max_row = max(self._max_row, row)
        self._min_column = min(self._min_column, column)
        self._max_column = max(self._max_column, column)

    def _is_valid_piece(self, piece_id):
        return piece_id is not None and piece_id not in self._kernel
