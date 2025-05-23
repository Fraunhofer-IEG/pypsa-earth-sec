# -*- coding: utf-8 -*-
"""Build industrial energy demand per node."""

import os
from itertools import product

import numpy as np
import pandas as pd

# map JRC/our sectors to hotmaps sector, where mapping exist
sector_mapping = {
    "Cement": "Cement",
}


def build_nodal_industrial_energy_demand():

    fn = snakemake.input.industrial_energy_demand_per_country_today
    industrial_demand = pd.read_csv(fn, header=[0, 1], index_col=0)

    fn = snakemake.input.industrial_distribution_key
    keys = pd.read_csv(fn, index_col=0)
    keys["country"] = keys.index.str[:2]

    nodal_demand = pd.DataFrame(
        0.0, dtype=float, index=keys.index, columns=industrial_demand.index
    )

    countries = keys.country.unique()
    sectors = industrial_demand.columns.levels[1]

    for country, sector in product(countries, sectors):

        buses = keys.index[keys.country == country]
        mapping = sector_mapping.get(sector, "population")

        key = keys.loc[buses, mapping]
        demand = industrial_demand[country, sector]

        outer = pd.DataFrame(
            np.outer(key, demand), index=key.index, columns=demand.index
        )

        nodal_demand.loc[buses] += outer

    nodal_demand.index.name = "TWh/a"

    nodal_demand.to_csv(snakemake.output.industrial_energy_demand_per_node_today)


if __name__ == "__main__":
    if "snakemake" not in globals():
        from helpers import mock_snakemake

        os.chdir(os.path.dirname(os.path.abspath(__file__)))

        snakemake = mock_snakemake(
            "build_industrial_energy_demand_per_node_today",
            simpl="",
            clusters=4,
        )

    build_nodal_industrial_energy_demand()
