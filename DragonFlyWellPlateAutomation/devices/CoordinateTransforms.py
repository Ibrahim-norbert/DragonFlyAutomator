import logging

import cv2 as cv
import numpy as np

logger = logging.getLogger("DragonFlyWellPlateAutomation.RestAPI.fusionrest")
logger.info("This log message is from {}.py".format(__name__))


def linearspacing(topright, topleft, bottomleft, c_n, r_n):
    length = np.linalg.norm(topleft - topright)
    height = np.linalg.norm(topleft - bottomleft)

    x_coord, x_spacing = np.linspace(topleft[0], topright[0], c_n, retstep=True)
    y_coord, y_spacing = np.linspace(topleft[1], bottomleft[1], r_n, retstep=True)

    logger.log(level=20, msg="Well plate dimension: length - {}, height - {}".format(length, height))
    logger.log(level=20, msg="Computed well spacing: x:spacing = {} and y_spacing = {}".format(
        x_spacing, y_spacing))

    xv, yv = np.meshgrid(x_coord, y_coord)

    vectors = np.stack([xv, yv, np.ones(yv.shape)], axis=-1)  # rows,columns,coordinate i.e. [x,y] in column direction

    vectors = vectors.reshape(r_n * c_n, 3)  # rows,columns,coordinate i.e. [x,y] in column direction

    wellcoords_key = sum([[str(r + 1) + "-" + str(c + 1) for c in range(c_n)] for r in range(r_n)], [])

    return vectors, wellcoords_key, length, height, x_spacing, y_spacing


def linearcorrectionmatrix(topright, topleft, bottomright, bottomleft, c_n, r_n):
    """correction matrix obtained from:
        https://scripts.iucr.org/cgi-bin/paper?S2053230X18016515"""

    raise NotImplemented

    # topright, topleft, bottomright, bottomleft = np.array([topright, topleft, bottomright, bottomleft]) + 100

    corx = topright / float(c_n)
    cory = bottomleft / float(r_n)

    # cor is the correction matrix to account for misalignment of the plate vs. translation directions in x,y,z
    cor = np.array(([corx[0], cory[0], 0],
                    [corx[1], cory[1], 0],
                    [0, 0, 0]))

    logger.log(level=20, msg="The correction matrix: {}".format(cor))

    brpred = np.dot(cor, np.array((c_n, r_n, 0)))  # predicted position of bl based on tl and br
    logger.log(level=20, msg="The bottom left well coordinate prediction: {}".format(brpred))

    fixit = (np.append(bottomright, 0) - brpred) / float(c_n * r_n)  # this is the correction based on bl
    logger.log(level=20, msg="The non linear prediction: {}".format(fixit))
    # x = numbers i.e. columns
    # y = letters i.e. rows
    vectors = sum(
        [[(np.dot(cor, np.array(np.array((c, r, 1)))) + fixit * (c * r)) for c in
          range(1, (c_n + 1))] for r in range(1, (r_n + 1))], [])

    # vectors = np.array(vectors)-100
    logger.log(level=20,
               msg="The resulting bottom right and middle well coordinates: {}".format([vectors[int((c_n * r_n) / 2)],
                                                                                        vectors[-1]]))

    wellcoords_key = sum([[str(r + 1) + "-" + str(c + 1) for c in range(c_n)] for r in range(r_n)], [])

    x_spacing = np.abs(vectors[int(c_n / 2)][0] - vectors[int(c_n / 2) + 1][0])
    y_spacing = np.abs(vectors[c_n * 2][1] - vectors[(c_n * 2) + 1][1])

    length = np.linalg.norm(topleft - topright)
    height = np.linalg.norm(topleft - bottomleft)

    return vectors, wellcoords_key, length, height, x_spacing, y_spacing


def homography_matrix_estimation(method, vectors, wellcoords_key):
    # Use this to associate a homography matrix to a wellplate

    print("Learning the homography matrix using {} to map from well plate row and column arrangement "
          "to xzy-stage coordinate space".format(method))

    # Define source and destination coordinates
    #c,r
    wellcoords = [np.flip([int(x.split("-")[0]), int(x.split("-")[1])]) for x in wellcoords_key]

    pts_src = np.array(wellcoords, dtype=np.float32)
    if len(pts_src[0]) < 3:
        pts_src = np.hstack((np.array(wellcoords, dtype=np.float32), np.ones((len(vectors), 1))))
    logger.log(level=20, msg="The chosen well coords {}".format(pts_src))

    pts_dst = np.array(vectors, dtype=np.float32)
    if len(vectors[0]) < 3:
        pts_dst = np.hstack((np.array(vectors, dtype=np.float32), np.ones((len(vectors), 1))))
    logger.log(level=20, msg="The corresponding xyz coordinates {}".format(pts_dst))

    if method == "Levenberg-Marquardt":
        logger.log(level=20, msg="Homography estimation method: {}".format(method))
        H = cv.findHomography(pts_src, pts_dst)[0]

    elif method == "SVD":
        logger.log(level=20, msg="Homography estimation method: {}".format("SVD"))
        # Construct matrix A
        A = []
        for i in range(len(pts_src)):
            x, y, z = pts_src[i]
            u, v, z = pts_dst[i]
            A.append([-x, -y, -1, 0, 0, 0, x * u, y * u, u])
            A.append([0, 0, 0, -x, -y, -1, x * v, y * v, v])

        A = np.array(A)

        # Use SVD to find the solution to Ah = 0
        _, _, V = np.linalg.svd(A)
        H = V[-1].reshape(3, 3)

        # Normalize the matrix (optional)
        H /= H[2, 2]

    else:

        logger.log(level=20, msg="Homography estimation method: {}".format("Eigenvectors"))
        # Construct matrix A
        A = []  # 3,9
        for i in range(len(pts_src)):
            x, y, z = pts_src[i]
            u, v, z = pts_dst[i]
            A.append([-x, -y, -1, 0, 0, 0, x * u, y * u, u])
            A.append([0, 0, 0, -x, -y, -1, x * v, y * v, v])

        A = np.array(A)

        # 9,3 @ 3,9
        eigenvalues, eigenvectors = np.linalg.eig(A.T @ A)
        # Find the smallest eigenvalue and its index
        smallest_eigenvalue_index = np.argmin(eigenvalues)

        # Extract the eigenvector corresponding to the smallest eigenvalue
        homography_candidate = eigenvectors[:, smallest_eigenvalue_index]

        # Reshape and normalize the homography matrix
        homography = homography_candidate.reshape((3, 3))
        H = homography / homography[2, 2]

    return H


def homography_fixit_calibration(P24_coords, vectors, r_n, c_n):
    if not isinstance(vectors, np.ndarray):
        vectors = np.array(vectors)

    pred = vectors[-1]

    fixit = (np.append(P24_coords, 0) - pred)
    logger.log(level=20, msg="We have the following difference in prediction: {}".format(fixit))

    vector_f, vector_l = np.vsplit(vectors.reshape(r_n, c_n, 3),
                                   2)
    vector_l = np.array(sum(
        [[vector_l[r, c] + np.array([(fixit[0] / c_n) * c, (fixit[1] / r_n) * r, fixit[-1]]) for c in
          range(vector_l.shape[1])] for r in range(vector_l.shape[0])], [])).reshape(vector_l.shape)

    vector_ff, vector_fl = np.hsplit(vector_f, 2)

    vector_f = np.hstack((vector_ff, np.array(sum(
        [[vector_fl[r, c] + np.array([(fixit[0] / c_n) * c, (fixit[1] / r_n) * r, fixit[-1]]) for c in
          range(vector_fl.shape[1])] for r in range(vector_fl.shape[0])], [])).reshape(vector_fl.shape)))

    return np.vstack((vector_f, vector_l)).reshape(r_n * c_n, 3)


def homography_fixit(P24_coords, pred, vectors):
    if pred is None:
        pred = vectors[-1]
    fixit = (np.append(P24_coords, 0) - pred)
    logger.log(level=20, msg="We have the following difference in prediction: {}".format(fixit))
    return vectors + fixit


def homography_application(homography, c_n, r_n):

    # The Hi3 cooefficient is very important !!!
    vectors, wellnames, wellcoords = list(zip(*sum(
        [[(np.dot(homography, np.array([c + 1, r + 1, 1])), str(r + 1) + "-" + str(c + 1), [r + 1, c + 1]) for c in
          range(c_n)] for r in range(r_n)], [])))
    vectors = np.array(list(vectors))

    x_spacing = np.abs(vectors[0][0] - vectors[1][0])
    y_spacing = np.abs(vectors[0][1] - vectors[c_n][1])

    length = np.linalg.norm(vectors[0] - vectors[c_n-1])
    height = np.linalg.norm(vectors[0] - vectors[r_n*(c_n-1)])

    logger.log(level=20, msg="Outputted vectors: {}".format(vectors))
    logger.log(level=20, msg="Outputted well names: {}".format(wellnames))
    return vectors, wellnames, length, height, x_spacing, y_spacing
