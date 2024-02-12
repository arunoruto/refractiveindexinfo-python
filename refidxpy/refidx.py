REF_IDX_URL = "https://refractiveindex.info/database/data-nk/{shelf}/{book}/{page}.yml"
GH_DB_URL = "https://raw.githubusercontent.com/polyanskiy/refractiveindex.info-database/master/database/data-nk/{shelf}/{book}/{page}.yml"

import yaml
import requests as req
import numpy as np
import pandas as pd
from io import StringIO

from refidxpy.formulas import formula_picker


class RefIdx:
    def __init__(self, url=None, shelf=None, book=None, page=None):
        if (url is None) and ((shelf is None) or (book is None) or (page is None)):
            raise ValueError("Either url or shelf, book, and page must be provided")

        if url is not None:
            self.url = url
            self.shelf = None
            self.book = None
            self.page = None
        else:
            self.url = REF_IDX_URL.format(shelf=shelf, book=book, page=page)
            self.url_gh = GH_DB_URL.format(shelf=shelf, book=book, page=page)
            self.shelf = shelf
            self.book = book
            self.page = page

        self._fetch_data()

    def _fetch_data(self):
        resp = req.get(self.url)
        if resp.status_code != 200:
            raise ValueError(f"Invalid URL {self.url}")
        tabulated_data = pd.DataFrame(columns=["wavelength", "n", "k"])
        formula_data = []
        ref_data = yaml.safe_load(resp.text)

        for line in ref_data["DATA"]:
            df = None
            if "tabulated" in line["type"].lower():
                header_yml = ["wavelength", "n", "k"]
                if line["type"].lower()[-2:] == " k":
                    header_yml = ["wavelength", "k", "n"]
                df = pd.read_csv(
                    StringIO(line["data"]), sep=r"\s+", header=None, names=header_yml
                )
                df = df.fillna(0)
                if tabulated_data.empty:
                    tabulated_data = df
                else:
                    tabulated_data = pd.concat([tabulated_data, df])
            elif "formula" in line["type"].lower():
                wavelength_limits = [float(c) for c in line["wavelength_range"].split()]
                coefficients = np.array(
                    [float(c) for c in line["coefficients"].split()]
                )
                formula_number = int(line["type"].split()[-1])
                formula = formula_picker(formula_number)
                formula_data.append(
                    dict(
                        function=lambda x: formula(
                            coefficients, x, wavelength_limits[0], wavelength_limits[1]
                        ),
                        wavelength_limits=wavelength_limits,
                        coefficients=coefficients,
                    )
                )

        self.tabulated = tabulated_data
        self.formula = formula_data

    def wavelength(self, wavelength):
        return 1.0
