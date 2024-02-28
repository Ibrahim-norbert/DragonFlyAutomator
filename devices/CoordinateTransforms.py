import logging
import numpy as np

logger = logging.getLogger(__name__)
logger.info("This log message is from another module.")


def linearspacing(topright, topleft, bottomright, bottomleft, c_n, r_n):
    length = np.linalg.norm(topleft - topright)
    height = np.linalg.norm(topleft - bottomleft)

    # There has to be regular spacing between cells
    x_coord, x_spacing = np.linspace(topright[0], topleft[0], c_n, retstep=True)
    y_coord, y_spacing = np.linspace(topright[1], bottomright[1], r_n, retstep=True)

    logging.log(level=20, msg="Well plate dimension: length - {}, height - {}".format(length, height))
    logging.log(level=20, msg="Computed well spacing: x:spacing = {} and y_spacing = {}".format(
        x_spacing, y_spacing))

    xv, yv = np.meshgrid(x_coord, y_coord)

    vectors = np.stack([xv, yv], axis=-1)  # rows,columns i.e. x,y,2

    vectors = vectors.reshape(r_n * c_n, 2)

    well_names = sum([[str(r) + " " + str(c + 1) for c in range(c_n)] for r in range(r_n)], [])

    return vectors, well_names, length, height, x_spacing, y_spacing


def linearcorrectionmatrix(topright, topleft, bottomright, bottomleft, c_n, r_n):
    """correction matrix obtained from:
        https://scripts.iucr.org/cgi-bin/paper?S2053230X18016515"""

    corx = topleft / float(c_n - 1)
    cory = bottomright / float(r_n - 1)

    # cor is the correction matrix to account for misalignment of the plate vs. translation directions in x,y,z
    cor = np.array(([corx[0], cory[0], 0],
                    [corx[1], cory[1], 0],
                    [0, 0, 0]))

    logging.log(level=20, msg="The correction matrix: {}".format(cor))

    blpred = np.dot(cor, np.array(((c_n - 1), (r_n - 1), 0)))  # predicted position of bl based on tl and br
    logging.log(level=20, msg="The bottom left well coordinate prediction: {}".format(blpred))

    fixit = (np.append(bottomleft, 0) - blpred) / float((c_n - 1) * (r_n - 1))  # this is the correction based on bl
    logging.log(level=20, msg="The non linear prediction: {}".format(fixit))
    # x = numbers i.e. columns
    # y = letters i.e. rows
    vectors = sum(
        [[(np.dot(cor, np.array(np.array((c, r, 0)))) + fixit * (c * r)) + np.append(topright, 0) for c in
          range(c_n)] for r in range(r_n)], [])

    logging.log(level=20, msg="The resulting vectors: {}".format(vectors))

    well_names = sum([[str(r) + " " + str(c + 1) for c in range(c_n)] for r in range(r_n)], [])

    x_spacing = np.abs(vectors[int(c_n / 2)][0] - vectors[int(c_n / 2) + 1][0])
    y_spacing = np.abs(vectors[c_n * 2][1] - vectors[(c_n * 2) + 1][1])

    length = np.linalg.norm(topleft - topright)
    height = np.linalg.norm(topleft - bottomleft)

    return vectors, well_names, length, height, x_spacing, y_spacing
