from ProjectRoot import change_wd_to_project_root
change_wd_to_project_root()
import matplotlib.pyplot as plt
import numpy as np
import json
import os

x_paths = ["/endpoint_outputs/Top right_xposition.json",
           "endpoint_outputs/Top left_xposition.json",
           "endpoint_outputs/Bottom left_xposition.json"]

y_paths = ["endpoint_outputs/Top right_yposition.json", "endpoint_outputs/Top left_yposition.json",
           "endpoint_outputs/Bottom left_yposition.json"]
data_path = os.getcwd()
print(data_path)
tr, tl, bl = [[eval(json.load(open(data_path + "/" + x))["Value"]), eval(json.load(open(data_path + "/" + y))["Value"])]
              for x, y in zip(x_paths, y_paths)]
r_n, c_n = 16, 24


def create_plot(xmin=-50,
                xmax=62,
                ymin=-40,
                ymax=35, title='Real-Time {} well plate positioning'.format(c_n * r_n)):
    # All values are in mm

    fig, axis = plt.subplots(figsize=(11, 7.2))

    ## Reduce scatter point to field of view size
    fov = 250 * 10 ** (-6) * 1024

    axis.set_xlim(xmin, xmax)
    axis.set_ylim(ymin, ymax)



    borders_c = c_n +1
    borders_r = r_n +1
    x_coords, xstep = np.linspace(xmin, xmax, borders_c, retstep=True)
    y_coords, ystep = np.linspace(ymin, ymax, borders_r, retstep=True)

    vector_1 = sum([[np.array([x, y]) for indx, x in enumerate(x_coords[:c_n])] for y in np.flip(y_coords[:r_n])], [])
    vector_2 = vector_1 + np.array([xstep, ystep])

    mid_point = (np.array(vector_1) + np.array(vector_2))/ 2

    axis.set_xticks(x_coords, minor=True)
    axis.set_yticks(y_coords, minor=True)

    # Gridlines based on minor ticks
    axis.grid(which='minor')
    axis.tick_params(which='minor', bottom=False, left=False)

    axis.set_title(title, fontsize=20)
    # Major ticks
    x_values = list(range(1, c_n + 1))
    y_values = [x for x in "ABCDEFGHIJKLMNOPQRSTUVWXYZ"[:r_n]]
    axis.set_xticks(np.linspace(xmin + (xstep / 2), xmax - (xstep / 2), c_n), minor=False)
    axis.set_yticks(np.linspace(ymin + (ystep / 2), ymax - (ystep / 2), r_n), minor=False)

    # Labels for major ticks
    axis.set_xticklabels(x_values, minor=False)
    axis.set_yticklabels(reversed(y_values), minor=False)

    axis.tick_params(axis='x', labelsize='medium')

    axis.tick_params(axis='y', labelsize='medium')

    axis.set_aspect("equal")

    ### Get normalized length and height of axis
    # Scaling factor of y and x
    transform = ((404.43636364 - 79.78181818) / 72)
    well_h = 4.5
    print(transform)
    # Pixels
    well_h_pixels = (well_h * transform)
    # Points
    p = 72 / 100
    print(well_h_pixels)
    # s
    s = (well_h_pixels * p) ** 2
    y_offset = (2 / 16)
    x_offset = (2 / 24)
    fov = 250 * 10 ** (-6) * 1024  # height
    s = (fov * p) ** 2

    print("x and y step: {} and {}".format(xstep, ystep))
    print("Ymin {} and Ymax {}".format(min(y_coords), max(y_coords)))
    print("Xmin {} and Xmax {}".format(min(x_coords), max(x_coords)))
    return axis, tr, tl, bl, r_n, c_n, mid_point, vector_1, sum([[np.array([x, y]) for indx, x in enumerate(x_coords[:c_n])] for y in np.flip(y_coords[1:])], [])


from DragonFlyWellPlateAutomation.devices.wellplate import WellPlate as wp


def initwellplate():
    WellPlate = wp(test=True)
    WellPlate.homography_source_coordinates["Top right well"] = WellPlate.vector_2_state_dict(tr)
    WellPlate.homography_source_coordinates["Top left well"] = WellPlate.vector_2_state_dict(tl)
    WellPlate.homography_source_coordinates["Bottom left well"] = WellPlate.vector_2_state_dict(bl)
    # WellPlate.homography_source_coordinates["Middle well"] = WellPlate.vector_2_state_dict(ml)
    # print(WellPlate.homography_source_coordinates.items())
    return WellPlate


def merge_complex_autofocusimgs():
    import matplotlib.pyplot as plt
    import numpy as np

    wellnames = sum([[str(r + 1) + "-" + str(c + 1) for c in range(c_n)] for r in range(r_n)], [])

    for vector, wellname in zip(mid_points, wellnames):
        # print("Well name {} and its coordinate: {}".format(wellname, vector))
        x, y = vector

        indxs = dfs["Wellname"].isin([wellname])

        if True in indxs.tolist():
            # Get all autofocus imgs
            # Confirm if 1st imgs took place less than 500s before complex img
            # print("---------------- \n Dataframe: {} \n Minimum: {} \n --------------------".format(dfs.loc[indxs, "time"].values, dfs.loc[indxs,"time"].min()))
            diffs = sorted([(datetime.strptime(x, "%H.%M.%S") - datetime.strptime(dfs.loc[indxs, "time"].min(),
                                                                                  "%H.%M.%S")).total_seconds() for x in
                            dt["time"]])

            c = [y for x, y in dt[["time", "Img_ID"]].values if (
                        datetime.strptime(x, "%H.%M.%S") - datetime.strptime(dfs.loc[indxs, "time"].min(),
                                                                             "%H.%M.%S")).total_seconds() < 800 and
                 (datetime.strptime(x, "%H.%M.%S") - datetime.strptime(dfs.loc[indxs, "time"].min(),
                                                                       "%H.%M.%S")).total_seconds() > 400]
            if c:
                dfs.loc[indxs, "complex_img"] = c[0]

            print("Minimum: {} \n Differences: {} \n Img ID: {}".format(dfs.loc[indxs, "time"].min(),
                                                                        [x for x in diffs if x > 400 and x < 800],
                                                                        c))
    dfs_merge = dfs.merge(right=dt, how="outer", left_on="complex_img", right_on="Img_ID")
    dfs_merge.to_csv(os.path.join(save_dir, "dt.csv"))

