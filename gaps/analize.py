from dissimilarity import DissimilarityMeasure


class ImageAnalysis(object):
    best_match_table = {}
    dissimilarity_measures = {}

    @classmethod
    def analyze_image(cls, pieces):
        for piece in pieces:
            cls.best_match_table[piece.id] = {
                0: [],
                1: [],
                2: [],
                3: []
            }
        iterations = len(pieces) - 1
        for first in range(iterations):
            for first_side in range(0, 4):
                for second in range(first + 1, len(pieces)):
                    for second_side in range(0, 4):
                        dis = DissimilarityMeasure.calc_dissimilarity_measure((pieces[first], first_side),
                                                                              (pieces[second], second_side))
                        cls.put_dissimilarity((first, second, first_side, second_side), dis)
                        cls.put_dissimilarity((second, first, second_side, first_side), dis)
                        cls.best_match_table[first][first_side].append((dis, second, second_side))
                        cls.best_match_table[second][second_side].append((dis, first, first_side))
                cls.best_match_table[first][first_side].sort(key=lambda x: x[0])

    @classmethod
    def put_dissimilarity(cls, conf, value):
        cls.dissimilarity_measures[conf] = value

    @classmethod
    def get_dissimilarity(cls, conf):
        return cls.dissimilarity_measures[conf]
