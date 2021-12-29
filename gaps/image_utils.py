import numpy as np


def assemble_image(pieces, rows, columns):
    vertical_stack = []
    for i in range(rows):
        horizontal_stack = []
        for j in range(columns):
            horizontal_stack.append(pieces[i * columns + j])
        vertical_stack.append(np.hstack(horizontal_stack))
    return np.vstack(vertical_stack).astype(np.uint8)
