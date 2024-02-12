import unittest
import io
import requests as req
import numpy as np
import pandas as pd

from refidxpy.refidx import RefIdx

CSV_URL = "https://refractiveindex.info/data_csv.php?datafile=database/data-nk/{shelf}/{book}/{page}.yml"
def _help_csv(url):
    resp = req.get(url)
    if resp.status_code != 200:
        raise ValueError(f"Invalid URL {url}. Please fix it for the test to pass.")
    pure_data = resp.text.replace("\r\n", "\n").split("\n\n")
    n_data = pd.read_csv(io.StringIO(pure_data[0]))
    if len(pure_data) > 1:
        k_data = pd.read_csv(io.StringIO(pure_data[1]))
    else:
        return n_data, None

    return n_data, k_data

class TestRefIdxInit(unittest.TestCase):
    # @classmethod
    # def setUpClass(cls):
    #     cls.data = {}

    def test_tabulated(self):
        tol = 1e-18

        shelf = "main"
        book = "Fe"
        page = "Querry"

        url = CSV_URL.format(shelf=shelf, book=book, page=page)
        n_data, k_data = _help_csv(url)

        material = RefIdx(shelf=shelf, book=book, page=page)

        np.testing.assert_allclose(material.tabulated[['wavelength', 'n']].values, n_data.values, rtol=tol)
        np.testing.assert_allclose(material.tabulated[['wavelength', 'k']].values, k_data.values, rtol=tol)

    def test_formula_1(self):
        shelf = "main"
        book = "GaAs"
        page = "Kachare"

        url = CSV_URL.format(shelf=shelf, book=book, page=page)
        n_data, _ = _help_csv(url)

        material = RefIdx(shelf=shelf, book=book, page=page)
        n_formula = material.formula[0]['function'](n_data['wl'].to_numpy())

        np.testing.assert_allclose(n_formula, n_data['n'].to_numpy(), rtol=1e-3)

    def test_formula_2(self):
        shelf = "glass"
        book = "schott"
        page = "N-BK7"

        url = CSV_URL.format(shelf=shelf, book=book, page=page)
        n_data, k_data = _help_csv(url)

        material = RefIdx(shelf=shelf, book=book, page=page)
        k_table = material.tabulated['k'].to_numpy()
        n_formula = material.formula[0]['function'](n_data['wl'].to_numpy())

        np.testing.assert_allclose(k_table,   k_data['k'].to_numpy(), rtol=1e-3)
        np.testing.assert_allclose(n_formula, n_data['n'].to_numpy(), rtol=1e-3)
