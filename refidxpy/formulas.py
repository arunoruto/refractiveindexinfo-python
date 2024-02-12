# Formular available at https://github.com/polyanskiy/refractiveindex.info-database/tree/master/database/doc

import numpy as np

def formula_picker(num):
    """
    Choose the right formula based on the number
    """
    match num:
        case 1:
            return sellmeier
        case 2:
            return sellmeier2
        case _:
            raise ValueError("Invalid formula number")

def sellmeier2(coefficients, wavelength, min_wl=-np.inf, max_wl=np.inf):
    """
    Sellmeier formula for the refractive index
    """
    mask = (wavelength < min_wl) & (max_wl < wavelength)
    n =  np.array(np.sqrt(
            1 + coefficients[0]
            + np.sum(
                [
                    coefficients[i]
                    * np.power(wavelength, 2)
                    / (np.power(wavelength, 2) - coefficients[i + 1])
                    for i in range(1, len(coefficients), 2)
                ],
                axis=0,
            )
        ))
    n[mask] = np.nan
    return n

def sellmeier(coefficients, wavelength, min_wl=-np.inf, max_wl=np.inf):
    """
    Sellmeier formula for the refractive index
    """
    coefficients = [c**2 if (i > 0 and i % 2 == 0) else c for i, c in enumerate(coefficients)]
    return sellmeier2(coefficients, wavelength, min_wl, max_wl)