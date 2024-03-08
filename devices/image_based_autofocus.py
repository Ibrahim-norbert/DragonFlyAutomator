""" All methods gotten from:
Koho, S., Fazeli, E., Eriksson, J. et al. Image Quality Ranking Method for Microscopy.
Sci Rep 6, 28962 (2016). https://doi.org/10.1038/srep28962"""

import numpy as np


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
    simple_power[1] /= (simple_power[1].sum() / 100)
    return simple_power[1]


class AutoFocus:
    def __init__(self):
        self.num = 0
        self.variables = {"Time to execute": None, "Memory requirement": None, "Accuracy estimator": None}
        self.metrics = ["Variance", "Brenner", "Spectral Moments", "Psm mean", "Psm std", "Psm meanbin",
                        "Metric comparison"]

    def Variance(self, img):
        res = np.var(img)
        key = "Variance"
        self.variables["Metrics"] = key
        self.variables[key] = res
        self.variables["Img_ID"] = self.num

        return res

    def Brenner(self, img):
        rows = img.shape[0]
        columns = img.shape[1] - 2
        temp = np.zeros((rows, columns))

        temp[:] = ((img[:, 0:-2] - img[:, 2:]) ** 2)
        res = temp.sum()
        key = "Brenner"
        self.variables["Metrics"] = key
        self.variables[key] = res
        self.variables["Img_ID"] = self.num

        return res

    def calculate_summed_power(self, power, x_spacing=(1 / 0.01)):
        """
            Calculate a 1D power spectrum from 2D power spectrum, by summing all rows and
            columns, and then summing negative and positive frequencies, to form a
            N/2+1 long 1D array. This approach is significantly faster to calculate
            than the radial average.
            """

        # Sum rows and columns
        sum_ = np.sum([np.sum(power, axis=i) for i in power.shape])

        # Using 0 center, add the negative Hz to the positive Hz
        zero = np.floor([float(sum_.size) / 2])[0]
        sum_[zero + 1:] = sum_[zero + 1:] + sum_[:zero - 1][::-1]
        sum_ = sum_[zero:]

        f_k = np.linspace(0, 1, sum_.size) * (1.0 / (2 * x_spacing))

        key = "Psw"
        self.variables["Variables"] = key

        self.variables["Total power"] = sum_
        self.variables["Frequency"] = f_k

        self.variables["Img_ID"] = self.num

        return [f_k, sum_]

    def Spectral_moments(self, img):
        """
        Our implementation of the Spectral Moments autofocus metric
        Firestone, L. et al (1991). Comparison of autofocus methods for automated
        microscopy. Cytometry, 12(3), 195–206.
        http://doi.org/10.1002/cyto.990120302
        """

        power = calculate_power_spectrum(img)

        summed_power = self.calculate_summed_power(power, x_spacing=(1 / 0.01))

        percent_spectrum = calculate_percent_spectrum(summed_power)

        bin_index = np.arange(1, percent_spectrum[1].shape[0] + 1)

        res = (percent_spectrum[1] * np.log10(bin_index)).sum()

        key = "Spectral Moments"
        self.variables["Metrics"] = key
        self.variables["Img_ID"] = self.num

        self.variables[key] = res

        return res

    def power_spectrum(self, img, power_threshold=0.02):
        power = calculate_power_spectrum(img)

        summed_power = self.calculate_summed_power(power, x_spacing=(1 / 0.01))

        # Extract the power spectrum tail
        return summed_power[1][summed_power[0] > power_threshold * summed_power[0].max()]

    def Psw_mean(self, img, power_threshold=0.02):
        """
        Run the image quality analysis on the power spectrum
        """

        mean = np.mean(self.power_spectrum(img, power_threshold=power_threshold))
        key = "Psm mean"
        self.variables["Metrics"] = key
        self.variables[key] = mean
        self.variables["Img_ID"] = self.num

    def Psw_std(self, img, power_threshold=0.02):
        """
        Run the image quality analysis on the power spectrum
        """

        mean = np.std(self.power_spectrum(img, power_threshold=power_threshold))
        key = "Psm std"
        self.variables["Metrics"] = key
        self.variables[key] = mean
        self.variables["Img_ID"] = self.num

    def Psw_meanbin(self, img, power_threshold=0.02):
        mean_bin = np.mean(self.power_spectrum(img, power_threshold=power_threshold)[0:5])
        key = "Psm meanbin"
        self.variables["Metrics"] = key
        self.variables[key] = mean_bin
        self.variables["Img_ID"] = self.num

    def combinatorial(self):
        # Combine INvsStd and Entropy for noise and fine detail?

        pass
