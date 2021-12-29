import numpy as np

piece_positions = [0, 1, 2, 3]


def calc_side(orientation, side):
    index = side - orientation
    return piece_positions[index]


class Piece(object):
    def __init__(self, image, index):
        self.image = image[:]
        self.id = index

    def __getitem__(self, index):
        return self.image.__getitem__(index)

    def size(self):
        return self.image.shape[0]

    def shape(self):
        return self.image.shape

    # 0 stands for top, 1 - left, 2 - down, 3 - right.
    def get_side_by_id(self, side_id):
        if side_id == 0:
            return self.image[0, :, :]

        if side_id == 1:
            return self.image[:, 0, :]

        if side_id == 2:
            return self.image[-1, :, :]

        if side_id == 3:
            return self.image[:, -1, :]


class RotatedPiece(object):

    def __init__(self, content: Piece, orientation=0):
        self.content = content
        self.orientation = orientation

    def orientation(self):
        return self.orientation

    def set_orientation(self, orientation):
        self.orientation = orientation

    @staticmethod
    def rotate_image(image):
        return np.array([[image[j, i] for j in range(len(image))] for i in range(len(image[0]) - 1, -1, -1)])

    def get_rotated_image(self):
        image = self.content.image
        for _ in range(self.orientation):
            image = self.rotate_image(image)
        return image
