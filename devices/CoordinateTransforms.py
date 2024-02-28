import logging
import numpy as np
from matplotlib import pyplot as plt

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


def homography_matrix_estimation():
    ##Use this to associate a homography matrix to a wellplate

    #
    #
    #
    #   # Must find the null space of a.T for a.Th = 0
    #  # x,y = well_coords
    #
    #  # print("Well coordinates: {}".format((x, y)))
    #
    #  # x_gt, y_gt = xyz_stage_coords
    #
    # #  print("Ground truth: " + str(x_gt))
    #
    #
    #   # # Assuming you have corresponding points in two images
    #   pts_src = np.array(well_coords, dtype=np.float32)
    #   pts_dst = np.array(xyz_stage_coords, dtype=np.float32)
    #   #
    #   # # Construct matrix A
    #   A = []
    #   for i in range(len(pts_src)):
    #    x, y = pts_src[i]
    #    u, v = pts_dst[i]
    #    A.append([-x, -y, -1, 0, 0, 0, x * u, y * u, u])
    #    A.append([0, 0, 0, -x, -y, -1, x * v, y * v, v])
    #    #A.append([0, 0, 0, -x, -y, -1, x * v, y * v, v])
    #
    #   A = np.array(A)
    #
    #   print("Before transpose: {}".format(A))
    #
    #   # Use SVD to find the solution to Ah = 0
    #   _, _, V = np.linalg.svd(A)
    #   H = V[-1].reshape(3, 3)
    #
    #   # Normalize the matrix (optional)
    #   H /= H[2, 2]
    #
    #   # Calculate A transpose times A
    #   # AtA = np.dot(A.T, A)
    #   #
    #   # print("After transpose: {}".format(AtA))
    #   #
    #   # # Use eig to find eigenvalues and eigenvectors
    #   # _, eigenvectors = np.linalg.eig(AtA)
    #   #
    #   # # Extract eigenvectors corresponding to the eigenvalue 0
    #   # null_space_vectors = eigenvectors[:, np.isclose(_, 0)]
    #   #
    #   # # Reshape the null space vectors into the homography matrix
    #   # H = null_space_vectors[:, 0].reshape(3, 3)
    #
    #   # Display the homography matrix
    #   print("Homography Matrix: {}".format(H))
    #
    #
    #  # h = cv.findHomography(well_coords, xyz_stage_coords)[0]
    #   # #[z_gt * np.array([x, y, z]), [0, 0, 0], -x_gt * np.array([x, y, z])]]
    #   # ax = np.array([[0, 0, 0], -z*np.array([x_gt, y_gt, z_gt]), y*np.array([x_gt, y_gt, z_gt])])
    #   # ax3 = np.array([-y*np.array([x_gt, y_gt, z_gt]), x*np.array([x_gt, y_gt, z_gt]), [0, 0, 0]])
    #   #
    #   # h3 = Matrix(ax3).nullspace()
    #   #
    #   # if len(h3) > 1:
    #   #     h3 = np.array(h3[0])
    #   #
    #   # h1 = Matrix(ax).nullspace()
    #   # if len(h1) > 1:
    #   #     h1 = np.array(h1[0])
    #   #pts_src =
    #   # Convert points to homogeneous coordinates
    #
    #   test = np.array([[6, 15]])
    #   pts_src_homogeneous = np.hstack((test, np.ones((test.shape[0], 1))))
    #
    #   # Apply perspective transformation
    #   pts_dst_homogeneous = np.dot(pts_src_homogeneous, H.T)
    #
    #   # Convert back to inhomogeneous coordinates
    #   pts_dst = pts_dst_homogeneous[:, :2] / pts_dst_homogeneous[:, 2:]

    well_coords, xyz_stage_coords = [16, 1], [-46.9, -35.939]  # Bottom left
    well_coords2, xyz_stage_coords2 = [1, 1], [-47.7, 33.1]  # Top left
    well_coords3, xyz_stage_coords3 = [1, 24], [59.4, 33.8]  # Top right
    well_coords4, xyz_stage_coords4 = [16, 24], [59.4, -35.939]  # Bottom right

    # Define source and destination coordinates
    pts_src = np.array([well_coords, well_coords2, well_coords3, well_coords4], dtype=np.float32)
    pts_dst = np.array([xyz_stage_coords, xyz_stage_coords2, xyz_stage_coords3, well_coords4], dtype=np.float32)

    # Construct matrix A
    A = []
    for i in range(len(pts_src)):
        x, y = pts_src[i]
        u, v = pts_dst[i]
        A.append([-x, -y, -1, 0, 0, 0, x * u, y * u, u])
        A.append([0, 0, 0, -x, -y, -1, x * v, y * v, v])

    A = np.array(A)

    # Use SVD to find the solution to Ah = 0
    _, _, V = np.linalg.svd(A)
    H = V[-1].reshape(3, 3)

    # Normalize the matrix (optional)
    H /= H[2, 2]

    # Unseen coordinate
    unseen_coord = np.array([10.0, 10.0, 1.0])

    # Transform the unseen coordinate using the computed homography matrix
    transformed_coord = np.dot(H, unseen_coord)

    # print("Homography Matrix:")
    # print(H)
    # print("\nTransformed Coordinate:")
    # print(transformed_coord)
    #
    # # eigenvalues, eigenvectors = np.linalg.eig(ax)
    #
    # # print("Eigenvalues {} \n Eigenvectors {}".format(eigenvalues, eigenvectors))
    #
    # # h1 = eigenvectors[np.argmin(eigenvalues[eigenvalues < 0 ])]
    #
    # # print("H3 {}".format(h3))
    #
    # # print("Numerator: {}".format(x_gt)T
    # # x_pred = np.sum(h1*np.array([x_gt, y_gt, z_gt]))/np.sum(h3*np.array([x_gt, y_gt, z_gt]))
    #
    # # x_pred = np.dot(np.array(well_coords + [0]), H)
    #
    # print("Prediction: " + str(pts_dst))

def homography_matrix_estimation_cv():
    ##Use this to associate a homography matrix to a wellplate

    import cv2 as cv
    #
    #  #
    #   # #[z_gt * np.array([x, y, z]), [0, 0, 0], -x_gt * np.array([x, y, z])]]
    #   # ax = np.array([[0, 0, 0], -z*np.array([x_gt, y_gt, z_gt]), y*np.array([x_gt, y_gt, z_gt])])
    #   # ax3 = np.array([-y*np.array([x_gt, y_gt, z_gt]), x*np.array([x_gt, y_gt, z_gt]), [0, 0, 0]])
    #   #
    #   # h3 = Matrix(ax3).nullspace()
    #   #
    #   # if len(h3) > 1:
    #   #     h3 = np.array(h3[0])
    #   #
    #   # h1 = Matrix(ax).nullspace()
    #   # if len(h1) > 1:
    #   #     h1 = np.array(h1[0])
    #   #pts_src =
    #   # Convert points to homogeneous coordinates
    #
    #   test = np.array([[6, 15]])
    #   pts_src_homogeneous = np.hstack((test, np.ones((test.shape[0], 1))))
    #
    #   # Apply perspective transformation
    #   pts_dst_homogeneous = np.dot(pts_src_homogeneous, H.T)
    #
    #   # Convert back to inhomogeneous coordinates
    #   pts_dst = pts_dst_homogeneous[:, :2] / pts_dst_homogeneous[:, 2:]

    well_coords1, xyz_stage_coords1 = [16, 1], [-46.9, -35.939]  # Bottom left
    well_coords2, xyz_stage_coords2 = [1, 1], [-47.7, 33.1]  # Top left
    well_coords3, xyz_stage_coords3 = [1, 24], [59.4, 33.8]  # Top right
    well_coords4, xyz_stage_coords4 = [16, 24], [59.4, -35.939]  # Bottom right

    well_coords, xyz_stage_coords = (np.array([well_coords1, well_coords2, well_coords3, well_coords4]),
                                     np.array([xyz_stage_coords1, xyz_stage_coords2, xyz_stage_coords3, xyz_stage_coords4]))

    h = cv.findHomography(well_coords, xyz_stage_coords)[0]

    # Unseen coordinate
    unseen_coord = np.array([10.0, 10.0, 1.0])

    # Transform the unseen coordinate using the computed homography matrix
    transformed_coord = np.dot(h, unseen_coord)

    print("Homography Matrix:")
    print(h)
    print("\nTransformed Coordinate:")
    print(transformed_coord)




import time
from memory_profiler import profile


# Your function to be tested
@profile
def your_function():
    # Your function code here
    result = 0
    for i in range(100):
        homography_matrix_estimation_cv()
        result += i
    return result


if __name__ == '__main__':
    your_function()
