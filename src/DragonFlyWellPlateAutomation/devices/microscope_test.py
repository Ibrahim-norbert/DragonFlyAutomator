from DragonFlyWellPlateAutomation.devices.micrscope import Microscope


def main():
    import argparse

    parser = argparse.ArgumentParser(description='Testing microscope stage for movement of z stage')

    parser.add_argument("--test", type=bool, default=False, help="Boolean")

    args = parser.parse_args()

    microscope = Microscope()

    microscope.test = args.test

    print(" ")
    print(" ")
    # Current endpoint
    print("Endpoint: {}".format(microscope.endpoint))

    # Get state
    state = microscope.get_state()
    print("Get state: {}".format(state))

    # Get current z height
    state, z = microscope.get_current_z()
    print("Current z height: {}".format(z))

    # Move stage closer to sample by increment
    print(" ")
    print("---------------------------")
    print("Move stage closer to sample by z increment: ")
    z_increment = float(input())
    microscope.move_z_axis(z_increment={"up": False, "Value": z_increment})
    print("Moved z height from {} to {}".format(z, microscope.get_current_z()[-1]))


if __name__ == '__main__':
    main()
