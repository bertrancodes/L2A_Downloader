import os
import requests
import argparse
import gzip
import shutil
import polars as pl
import geopandas as gpd

from tqdm import tqdm
from glob import iglob
from pathlib import Path
from datetime import datetime
from shapely.geometry import Point


def upadte_index_metadata(url:str):

    response = requests.get(url, stream = True)
    total_length = response.headers.get('content-length', 0)

    if response.status_code == 200: # no content length header
        print('Status OK. Downloading... ')
        total_length = int(total_length)
    
        with open(f'../conf/{Path(url).name}', 'wb') as f, tqdm(
            desc = Path(url).name,
            total = total_length,
            unit = 'iB',
            unit_scale = True,
            unit_divisor = 1024,
            position = 1,
            leave = True
        ) as bar:
            for chunk in response.iter_content(chunk_size=8192):
                size = f.write(chunk)
                bar.update(size)
    
    else:
        print(f'Something is wrong. Error code {response.status_code}')

    print(f'Decompressing {Path(url).name} ...')
    
    with gzip.open(f'../conf/index.csv.gz') as f_gzip:
        with open(f'../conf/index.csv', 'wb') as f_csv:
            shutil.copyfileobj(f_gzip, f_csv)
    
    print(f'Decompression successful!')

    return

def get_S2_tileID(file, lat, lon):
    
    s2_grid = gpd.read_file(file)

    point = Point(lon, lat)
 
    tile_id = s2_grid.loc[s2_grid.contains(point)].Name.values[0]

    return tile_id

def download_L2A_products(id, tile, start_date, end_date):


    print('Reading index metadata...')
    lf = pl.scan_csv(f'../conf/index.csv')

    lf = lf.with_columns(
        pl.col('SENSING_TIME').str.strptime(
        datatype = pl.Datetime, 
        fmt = '%Y-%m-%dT%H:%M:%S%.fZ')) # Equivalent to "%+", see: https://docs.rs/chrono/latest/chrono/format/strftime/index.html
    

    lf = lf.filter(pl.col('SENSING_TIME') 
          .is_between(datetime.strptime(start_date, '%Y-%m-%d'),
                        datetime.strptime(end_date, '%Y-%m-%d'),
                        closed = 'both'))
    
    lf = lf.filter(pl.col('MGRS_TILE') == tile)

    lf = lf.filter(pl.col('CLOUD_COVER') <= 60)

    urls = lf.select(pl.col('BASE_URL'))

    urls = urls.collect()
    print(f'Found {len(urls)} L2A products')
    
    # Check if file has already been downloaded

    print('Cheking for redundancies in downloaded files...')
    local_L2A_files = [Path(local_L2A_file).name for local_L2A_file in iglob('../data/**/*.SAFE')]
    
    urls_to_download = [url for url in urls.to_numpy().squeeze() if Path(url).name not in local_L2A_files]

    print(f'Found {len(urls)-len(urls_to_download)} files already downloaded')
    print(f'Downloading {len(urls_to_download)} files')


    Path(f'../data/{id}').mkdir(parents = True, exist_ok = True)
    
    for url in urls_to_download:
        os.system(f'gsutil -m cp -r {url[0]} ../data/{id}/.')

    return


if __name__ == '__main__':
    

    parser = argparse.ArgumentParser(description = "Download Sentinel-2 Level 2A products based on lat long coordinates and date range",
                                 formatter_class= argparse.MetavarTypeHelpFormatter)
    
    parser.add_argument("-lat", "--latitude", required = True,
                        help = "Latitude in decimal values ", type = float)
    
    parser.add_argument("-lon", "--longitude", required = True, 
                        help = "Longitude in decimal values ", type = float)
    
    parser.add_argument("-ID", "--dir-id", required = True, 
                        help = "Directory name to store", type = str)
    
    parser.add_argument("-sd", "--start-date", required = True, 
                        help = "Start date for date range (aaaa-mm-dd). Inclusive", type = str)
    
    parser.add_argument("-ed", "--end-date", required = True, 
                        help = "End date for date range (aaaa-mm-dd). Inclusive", type = str)
    
    args = parser.parse_args()
    config = vars(args)
    print(config)


    yes_choices = ['yes', 'y']
    no_choices = ['no', 'n']

    lat = config['latitude']
    lon = config['longitude']
    id = config['dir_id']
    start_date = config['start_date']
    end_date = config['end_date']
    

    print(f'Getting tile ID for coordinates {lat} LAT, {lon} LON ...')
    tile_id = get_S2_tileID(f'../conf/S2_Grid.geojson', lat, lon)
    

    time_since_update = Path(f'../conf/index.csv.gz').stat().st_mtime
    print(f'Last time index was updated was {datetime.fromtimestamp(time_since_update)}')
    
    while True:
        
        update_metadata = input('Do you want to update the index metadata? [Yes/No]: ')

        if update_metadata.lower() in yes_choices:
            url = 'https://storage.googleapis.com/gcp-public-data-sentinel-2/L2/index.csv.gz'
            upadte_index_metadata(url)
            break
        
        elif update_metadata.lower() in no_choices:
            print('Skipping index metadata update')
            break
        
        else:
            print('Wrong input')
            continue

    download_L2A_products(id, tile_id, start_date, end_date)
