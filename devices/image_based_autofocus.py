""" All methods gotten from:
Koho, S., Fazeli, E., Eriksson, J. et al. Image Quality Ranking Method for Microscopy.
Sci Rep 6, 28962 (2016). https://doi.org/10.1038/srep28962"""

import numpy as np

variables = {"Time to execute": None, "Memory requirement": None, "Accuracy estimator": None}


def maximum_variance(img):
    res = np.var(img)

    variables["Variance"] = res

    return res

def brenner(img):
    rows = img.shape[0]
    columns = img.shape[1] - 2
    temp = np.zeros((rows, columns))

    temp[:] = ((img[:, 0:-2] - img[:, 2:]) ** 2)
    res = temp.sum()

    variables["Brenner"] = res

    return res


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


def calculate_summed_power(power, x_spacing=(1 / 0.01)):
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

    variables["Total power"] = sum_
    variables["Frequency"] = f_k

    return [f_k, sum_]


def calculate_percent_spectrum(simple_power):
    simple_power[1] /= (simple_power[1].sum() / 100)
    return simple_power[1]


def spectral_moments(img):
    """
    Our implementation of the Spectral Moments autofocus metric
    Firestone, L. et al (1991). Comparison of autofocus methods for automated
    microscopy. Cytometry, 12(3), 195–206.
    http://doi.org/10.1002/cyto.990120302
    """

    power = calculate_power_spectrum(img)

    summed_power = calculate_summed_power(power, x_spacing=(1 / 0.01))

    percent_spectrum = calculate_percent_spectrum(summed_power)

    bin_index = np.arange(1, percent_spectrum[1].shape[0] + 1)

    res = (percent_spectrum[1] * np.log10(bin_index)).sum()

    variables["Spectral Moments"] = res

    return res


def analyze_power_spectrum(img, power_threshold=0.02):
    """
    Run the image quality analysis on the power spectrum
    """

    power = calculate_power_spectrum(img)

    summed_power = calculate_summed_power(power, x_spacing=(1 / 0.01))

    # Extract the power spectrum tail
    hf_sum = summed_power[1][summed_power[0] > power_threshold * summed_power[0].max()]

    mean = np.mean(hf_sum)
    std = np.std(hf_sum)
    mean_bin = np.mean(hf_sum[0:5])

    variables["Psm mean"] = mean
    variables["Psm std"] = std
    variables["Psm meanbin"] = mean_bin

    return [mean, std, mean_bin]
