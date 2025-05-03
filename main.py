import warnings

import astropy.units as u
from astropy import coordinates
from astroquery.vizier import Vizier
from tqdm import tqdm

warnings.filterwarnings('ignore')

SEARCH_RADIUS = 3 * u.arcsecond
TESS_NAME = 'IV/39/'
NOMAD_NAME = 'I/297/'
AAVSO_NAME = 'II/336/'
MASS_NAME = 'II/246/'


def main() -> None:
    from pathlib import Path

    # Vizier.clear_cache()

    data_file_path = (Path(__file__).parent / "data/subset_1.txt").resolve()
    with data_file_path.open('r', encoding='utf-8') as data_file:
        pbar = tqdm(total=len(data_file.readlines()) - 1)
        data_file.seek(0)

        column_names: list[str] = data_file.readline().strip().split(',')
        ra_index: int = column_names.index('ra')
        dec_index: int = column_names.index('dec')

        for line in data_file:
            line_elements_arr: list[float] = list(map(float, line.strip().split(',')))
            object_ra, object_dec = line_elements_arr[ra_index], line_elements_arr[dec_index]
            object_coord = coordinates.SkyCoord(object_ra, object_dec, unit='deg')

            tess_columns: dict[str, str] = {
                'GAIA': '-', 'Gmag': '-', 'Tmag': '-', 'Bmag': '-', 'Vmag': '-'}
            nomad_columns: dict[str, str] = {
                'Bmag': '-', 'Vmag': '-', 'Rmag': '-', 'Jmag': '-', 'Hmag': '-', 'Kmag': '-'}
            aavso_columns: dict[str, str] = {'Bmag': '-', 'Vmag': '-'}
            mass_columns: dict[str, str] = {'Jmag': '-', 'Hmag': '-', 'Kmag': '-'}

            object_table = Vizier.query_region(object_coord, radius=SEARCH_RADIUS)
            for catalog_name in object_table.keys():
                if TESS_NAME in catalog_name:
                    tess_catalog = object_table[catalog_name]
                    for key in tess_columns.keys():
                        if key not in tess_catalog.keys():
                            continue
                        tess_columns[key] = str(tess_catalog[key].value.data[0])
                elif NOMAD_NAME in catalog_name:
                    nomad_catalog = object_table[catalog_name]
                    for key in nomad_columns.keys():
                        if key not in nomad_catalog.keys():
                            continue
                        nomad_columns[key] = str(nomad_catalog[key].value.data[0])
                elif AAVSO_NAME in catalog_name:
                    aavso_catalog = object_table[catalog_name]
                    for key in aavso_columns.keys():
                        if key not in aavso_catalog.keys():
                            continue
                        aavso_columns[key] = str(aavso_catalog[key].value.data[0])
                elif MASS_NAME in catalog_name:
                    mass_catalog = object_table[catalog_name]
                    for key in mass_columns.keys():
                        if key not in mass_catalog.keys():
                            continue
                        mass_columns[key] = str(mass_catalog[key].value.data[0])

            pbar.update(1)


if __name__ == "__main__":
    main()
