""" All methods gotten from:
Koho, S., Fazeli, E., Eriksson, J. et al. Image Quality Ranking Method for Microscopy.
Sci Rep 6, 28962 (2016). https://doi.org/10.1038/srep28962"""
import glob
import os
from imaris_ims_file_reader.ims import ims
import numpy as np
import pandas as pd


# TODO add perform testing of the file
def calculate_power_spectrum(data, normalize=True):
    """
    A function that is used to calculate a centered 2D power spectrum.
    Additionally, the power spectrum can be normalized by image dimensions
    and image intensity mean, if necessary.
    """

    power = np.abs(np.fft.fftshift(np.fft.fft2(data))) ** 2
    if normalize:
        dims = data.shape[0] * data.shape[1]
        mean = np.mean(data)
        power = power / (dims * mean)

    return power


def calculate_percent_spectrum(simple_power):
    simple_power /= (simple_power.sum() / 100)
    return simple_power


class AutoFocus:
    def __init__(self):
        self.variables = None
        self.metrics = [func for indx, func in enumerate(dir(self)) if callable(getattr(self, func)) and
                        indx < 5]
        self.refresh()

    def refresh(self):
        self.variables = {
            "Img_ID": [], "Z plane": [], "Well coords": [], "Acquisition number": [], "Metrics": [], "Value": [],
        "Variables": [], "Frequency": [], "Total power": []}

    def savestats2dict(self, key, res, img_name):
        self.variables["Metrics"] += [key]
        self.variables["Value"] += [res]  # self.collector
        self.variables["Img_ID"] += [img_name]
        self.variables["Z plane"] += [eval((img_name.split("_zheigth")[1]).split(".")[0])]
        self.variables["Well coords"] += [(img_name.split("_well")[1]).split("_zheigth")[0]]
        self.variables["Acquisition number"] += [eval((img_name.split("_n")[1]).split("_well")[0])]

    def calculate_summed_power(self, power, x_spacing=(1 / 0.01), img_name=None):
        """
            Calculate a 1D power spectrum from 2D power spectrum, by summing all rows and
            columns, and then summing negative and positive frequencies, to form a
            N/2+1 long 1D array. This approach is significantly faster to calculate
            than the radial average.
            """

        # Sum rows and columns
        sum_ = np.sum([np.sum(power, axis=i) for i in range(power.ndim)], axis=0)
        # Using 0 center, add the negative Hz to the positive Hz
        zero = int(np.floor([float(sum_.size) / 2])[0])
        sum_[zero + 1:] = sum_[zero + 1:] + sum_[:zero - 1][::-1]
        sum_ = sum_[zero:]

        f_k = np.linspace(0, 1, sum_.size) * (1.0 / (2 * x_spacing))

        key = "Psw"
        self.variables["Variables"] += [key]

        self.variables["Total power"] += [sum_.tolist()]
        self.variables["Frequency"] += [f_k.tolist()]

        self.variables["Img_ID"] += [img_name]
        self.variables["Z plane"] += [eval((img_name.split("_zheigth")[1]).split(".")[0])]
        self.variables["Well coords"] += [(img_name.split("_well")[1]).split("_zheigth")[0]]
        self.variables["Acquisition number"] += [eval((img_name.split("_n")[1]).split("_well")[0])]

        return [f_k, sum_]

    def power_spectrum(self, img, power_threshold=0.02, img_name=None):
        power = calculate_power_spectrum(img)

        summed_power = self.calculate_summed_power(power, x_spacing=(1 / 0.01), img_name=img_name)

        # Extract the power spectrum tail
        return summed_power[1][summed_power[0] > power_threshold * summed_power[0].max()]

    def turn2dt(self):
        df = pd.DataFrame.from_dict(
            self.variables, orient="index")
        return df.transpose()

    def save2DT_excel(self, directory, dt):
        dt.to_csv(os.path.join(directory, "well_plate_data.csv"))
        self.variables = {
            "Img_ID": [], "Z plane": [], "Well coords": [], "Acquisition number": [], "Metrics": [], "Value": []}

    def Variance(self, img, img_name=None):
        res = np.var(img)
        key = "Variance"
        self.savestats2dict(key, res, img_name)
        return res

    def Brenner(self, img, img_name=None):
        temp = ((img[:, 0:-2] - img[:, 2:]) ** 2)
        res = temp.sum()
        key = "Brenner"
        self.savestats2dict(key, res, img_name)
        return res

    def Spectral_moments(self, img, img_name):
        """
        Our implementation of the Spectral Moments autofocus metric
        Firestone, L. et al (1991). Comparison of autofocus methods for automated
        microscopy. Cytometry, 12(3), 195–206.
        http://doi.org/10.1002/cyto.990120302
        """

        power = calculate_power_spectrum(img)

        something, summed_power = self.calculate_summed_power(power, x_spacing=(1 / 0.01), img_name=img_name)

        percent_spectrum = calculate_percent_spectrum(summed_power)

        bin_index = np.arange(1, percent_spectrum.shape[0] + 1)

        res = (percent_spectrum * np.log10(bin_index)).sum()

        key = "Spectral Moments"
        self.savestats2dict(key, res, img_name)

        return res

    def Psw_mean(self, img, img_name, power_threshold=0.02):
        """
        Run the image quality analysis on the power spectrum
        """

        res = np.mean(self.power_spectrum(img, power_threshold=power_threshold, img_name=img_name))
        key = "Psm mean"
        self.savestats2dict(key, res, img_name)

        return res

    def Psw_std(self, img, power_threshold=0.02, img_name=None):
        """
        Run the image quality analysis on the power spectrum
        """

        res = np.std(self.power_spectrum(img, power_threshold=power_threshold, img_name=img_name))
        key = "Psm std"
        self.savestats2dict(key, res, img_name)

        return res

    def Psw_meanbin(self, img, power_threshold=0.02, img_name=None):
        res = np.mean(self.power_spectrum(img, power_threshold=power_threshold, img_name=img_name)[0:5])
        key = "Psm meanbin"
        self.savestats2dict(key, res, img_name)

        return res

    def combinatorial(self):
        # Combine INvsStd and Entropy for noise and fine detail?
        pass


def main():
    autofocus = AutoFocus()
    # os.path.join(os.getcwd(), "test_rn/2024-03-05/*.ims")
    img_paths = glob.glob(
        "/media/ibrahim/Extended Storage/cloud/Internship/bioquant/348_wellplate_automation/test_rn/2024-03-05/*.ims")

    print("Before update: {}".format(autofocus.variables))

    for img_path in img_paths:
        img = ims(img_path, squeeze_output=True)
        img = img[0, :, 0]

        img_name = os.path.basename(img_path)

        autofocus.Variance(img, img_name=img_name)

        autofocus.Brenner(img, img_name=img_name)

        autofocus.Psw_mean(img, img_name=img_name)

        autofocus.Spectral_moments(img, img_name=img_name)

    print("After update: {}".format(autofocus.variables))
    df = pd.DataFrame.from_dict(
        autofocus.variables, orient="index")
    df = df.transpose()
    df.to_csv("/media/ibrahim/Extended Storage/cloud/Internship/bioquant/348_wellplate_automation/test_rn/df.csv")
if __name__ == '__main__':
    main()
