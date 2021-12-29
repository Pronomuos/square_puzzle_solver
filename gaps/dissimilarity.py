import numpy as np


class DissimilarityMeasure(object):

    @staticmethod
    def calc_dissimilarity_measure(first_piece, second_piece):
        first_piece_side = first_piece[0].get_side_by_id(first_piece[1]) / 255.0
        second_piece_side = second_piece[0].get_side_by_id(second_piece[1]) / 255.0
        first_side, second_side = (first_piece[1], second_piece[1]) if first_piece[1] < second_piece[1] \
            else (second_piece[1], first_piece[1])
        if first_side == second_side or first_side == 0 and second_side == 3 or first_side == 1 and second_side == 2:
            first_piece_side = first_piece_side[::-1]

        color_difference = first_piece_side - second_piece_side

        squared_color_difference = np.power(color_difference, 2)
        color_difference_per_row = np.sum(squared_color_difference, axis=1)
        total_difference = np.sum(color_difference_per_row, axis=0)

        value = np.sqrt(total_difference)

        return value
