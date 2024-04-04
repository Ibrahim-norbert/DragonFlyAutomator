from DragonFlyWellPlateAutomation.devices.image_based_autofocus import AutoFocus
from DragonFlyWellPlateAutomation.devices.protocol import Protocol


def main():
    import argparse
    import os
    parser = argparse.ArgumentParser(description='Test the script {}'.format(__name__))

    parser.add_argument("--test", type=bool, default=True)

    parser.add_argument("--wellname", type=str, required=True, help="Enter well coordinates as 0-0 "
                                                                       "instead of A1")

    parser.add_argument("--z_spacing", type=float, required=True, help="Enter z spacing for z-stack")

    parser.add_argument("--n_acquisitions", type=int, required=True, help="Enter number of acquisitions "
                                                                          "in z-stack")

    parser.add_argument("--image_dir", type=str, required=True, help="Enter the image directory path")

    parser.add_argument("--img_name", type=str, required=False, help="Enter image name",
                        default="test_image")

    parser.add_argument("--autofocus_alg", type=str, required=False,
                        help="Choose autofocus algorithm: " + str(AutoFocus().metrics), default="Brenner")

    parser.add_argument("--coordinate_frame_algorithm", type=str,
                        required=False, help="Enter the algorithm to predict the grid", default="Homography")

    parser.add_argument("--homography_matrix_algorithm", type=str,
                        required=False, help="Enter the algorithm to estimate the homography matrix",
                        default="Eigendecomposition")

    args = parser.parse_args()

    imagename = args.img_name
    wellname = args.wellname
    z_spacing = args.z_spacing
    n_aqcuisitions = args.n_acquisitions
    autofocus_alg = args.autofocus_alg
    coordinate_frame_algorithm = args.coordinate_frame_algorithm
    homography_matrix_algorithm = args.homography_matrix_algorithm

    protocol = Protocol()

    print("This is a test run, no change in state of the microscope is performed.")

    protocol.test = args.test

    protocol.image_name = imagename
    protocol.image_dir = args.image_dir

    protocol.autofocus_algorithm = autofocus_alg

    print("Current Protocol: {}".format(protocol.get_state()))
    print(" ")
    print("Perform image acquisition...")
    img_path = protocol.image_acquisition(img_path=os.path.join(protocol.image_dir, protocol.image_name), protocol_name="Protocol 59")
    print("Image is saved at: {}".format(img_path))

    print(" ")
    print("Perform autofocus on well {} with parameters: z upwards and downwards increment {} and number of acquisitions {}"
          .format(wellname, z_spacing, n_aqcuisitions))
    well_dir = protocol.autofocusing(wellname=wellname, z_increment=z_spacing, n_acquisitions=n_aqcuisitions)
    print("Path of image: {}".format(img_path))

    print(" ")
    print("-------------------")
    print("Perform image acquisition at estimated focal plane....")
    print("Please enter protocol of choice: ")
    protocol_name = str(input())
    protocol.image_acquisition(os.path.join(well_dir, protocol.image_name), protocol_name)


    # Save data
    protocol.savedatafromexecution([-48, 33.1, 0], coordinate_frame_algorithm, homography_matrix_algorithm, well_dir)


if __name__ == '__main__':
    main()
