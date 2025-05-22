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
    output_file_path = (Path(__file__).parent / "data/subset_1_output.txt").resolve()
    with (data_file_path.open('r', encoding='utf-8') as data_file,
          output_file_path.open('w', encoding='utf-8') as output_file):
        pbar = tqdm(total=len(data_file.readlines()) - 1)
        data_file.seek(0)

        column_names_line = data_file.readline().strip()
        column_names: list[str] = column_names_line.split(',')

        ra_index: int = column_names.index('ra')
        dec_index: int = column_names.index('dec')

        tess_column_names = 'GAIA,Tess Gmag,Tess Tmag,Tess Bmag,Tess Vmag'
        nomad_column_names = 'Nomad Bmag,Nomad Vmag,Nomad Rmag,Nomad Jmag,Nomad Hmag,Nomad Kmag'
        aavso_column_names = 'Aavso Bmag,Aavso Vmag'
        mass_column_names = 'Mass Jmag,Mass Hmag,Mass Kmag'
        column_names_line = f'{column_names_line},{tess_column_names},{nomad_column_names},{aavso_column_names},{mass_column_names}\n'
        output_file.write(column_names_line)

        for line in data_file:
            output_line = line.strip()
            line_elements_arr: list[float] = list(map(float, output_line.split(',')))
            object_ra, object_dec = line_elements_arr[ra_index], line_elements_arr[dec_index]
            object_coord = coordinates.SkyCoord(object_ra, object_dec, unit='deg')

            tess_columns: dict[str, str] = {
                'GAIA': 'nan', 'Gmag': 'nan', 'Tmag': 'nan', 'Bmag': 'nan', 'Vmag': 'nan'}
            nomad_columns: dict[str, str] = {
                'Bmag': 'nan', 'Vmag': 'nan', 'Rmag': 'nan', 'Jmag': 'nan', 'Hmag': 'nan', 'Kmag': 'nan'}
            aavso_columns: dict[str, str] = {'Bmag': 'nan', 'Vmag': 'nan'}
            mass_columns: dict[str, str] = {'Jmag': 'nan', 'Hmag': 'nan', 'Kmag': 'nan'}

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

            output_line += ','
            for value in tess_columns.values():
                output_line += value + ','
            for value in nomad_columns.values():
                output_line += value + ','
            for value in aavso_columns.values():
                output_line += value + ','
            for value in mass_columns.values():
                output_line += value + ','
            output_line = output_line[:-1]
            output_line += '\n'
            output_file.write(output_line)

            pbar.update(1)


if __name__ == "__main__":
    main()
