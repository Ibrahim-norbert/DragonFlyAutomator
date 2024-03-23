import logging

import cv2 as cv
import numpy as np

logger = logging.getLogger("DragonFlyWellPlateAutomation.RestAPI.fusionrest")
logger.info("This log message is from {}.py".format(__name__))


def linearspacing(topright, topleft, bottomright, bottomleft, c_n, r_n):
    length = np.linalg.norm(topleft - topright)
    height = np.linalg.norm(topleft - bottomleft)

    # There has to be regular spacing between cells
    x_coord, x_spacing = np.linspace(topleft[0], topright[0], c_n, retstep=True)
    y_coord, y_spacing = np.linspace(topleft[1], bottomleft[1], r_n, retstep=True)

    logger.log(level=20, msg="Well plate dimension: length - {}, height - {}".format(length, height))
    logger.log(level=20, msg="Computed well spacing: x:spacing = {} and y_spacing = {}".format(
        x_spacing, y_spacing))

    xv, yv = np.meshgrid(x_coord, y_coord)

    vectors = np.stack([xv, yv], axis=-1)  # rows,columns,coordinate i.e. [x,y] in column direction

    vectors = vectors.reshape(r_n * c_n, 2)  # rows,columns,coordinate i.e. [x,y] in column direction

    vectors = [x.tolist() for x in vectors]

    wellcoords_key = sum([[str(r + 1) + "-" + str(c + 1) for c in range(c_n)] for r in range(r_n)], [])

    return vectors, wellcoords_key, length, height, x_spacing, y_spacing


def linearcorrectionmatrix(topright, topleft, bottomright, bottomleft, c_n, r_n):
    """correction matrix obtained from:
        https://scripts.iucr.org/cgi-bin/paper?S2053230X18016515"""

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
          range(1, (c_n+1))] for r in range(1, (r_n+1))], [])

    logger.log(level=20, msg="The resulting bottom right and middle well coordinates: {}".format([vectors[int((c_n*r_n)/2)],
                                                                                                 vectors[-1]]))

    wellcoords_key = sum([[str(r+1) + "-" + str(c + 1) for c in range(c_n)] for r in range(r_n)], [])

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

    wellcoords = [np.flip([int(x.split("-")[0]), int(x.split("-")[1])]) for x in wellcoords_key]

    pts_src = np.array(wellcoords, dtype=np.float32)[:4]
    if len(pts_src[0]) < 3:
        pts_src = np.hstack((np.array(wellcoords, dtype=np.float32), np.ones((len(vectors),1))))[:4]
    logger.log(level=20, msg="The chosen well coords {}".format(pts_src))

    pts_dst = np.array(vectors, dtype=np.float32)[:4]
    if len(vectors[0]) < 3:
        pts_dst = np.hstack((np.array(vectors, dtype=np.float32), np.ones((len(vectors),1))))[:4]
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
        A = [] #3,9
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


def homography_application(homography, c_n, r_n, blpred=np.array([-47.7, 37, 0])):
    # The Hi3 cooefficient is very important !!!
    vectors, wellnames, wellcoords = list(zip(*sum(
        [[(np.dot(homography, np.array(np.array((c +1,  r +1, 1)))), str(r + 1) + "-" + str(c + 1), [r +1,  c +1]) for c in
          range(c_n)] for r in range(r_n)], [])))

    # vectors = []
    # # for wellcoord in wellcoords:
    # #     h_11, h_12, h_13 = homography[0]
    # #     h_21, h_22, h_23 = homography[1]
    # #     h_31, h_32, h_33 = homography[2]
    # #     r,c = wellcoord
    # #     vector = [(c*h_11 + r*h_12 + h_13),
    # #               (c*h_21 + r*h_22 + h_23)]
    # #     vectors += [vector]
    print(vectors[(r_n * c_n) - c_n])
    fixit = (np.array([-47.7, -37, 0]) - np.array(vectors[(r_n * c_n) - c_n]))
    vectors_corr = []
    for indx,vector in enumerate(vectors):
        vector = np.array(vector)
        # if indx > ((r_n/2)*c_n)-1:
        #     vector =  vector + fixit
        vectors_corr += [vector + fixit]
    logger.log(level=20, msg="Outputted vectors: {}".format(vectors))
    logger.log(level=20, msg="Outputted well names: {}".format(wellnames))
    return vectors_corr, wellnames


def homography_fixit_calibration(blpred, bl, homography, c, r, c_n, r_n):
    fixit = (np.append(bl, 0) - np.append(blpred, 0)) / float((c_n - 1) * (r_n - 1))
    return homography_application(homography, c, r) + fixit
