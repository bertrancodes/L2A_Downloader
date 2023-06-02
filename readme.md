## Sentinel-2 L2A Downloader
Download Sentinel-2 L2A imagery given a pair of latitude, longitude coordinates, a directory ID and a date range. Convert the single band JP2 images to a multiband compressed GeoTIFF.

### Requirements
* polars >= 0.16.4
* tqdm >= 6.2
* geopandas >= 0.12.2
* shapely >= 2.0.1
* gsutil >= 5.13
* numba >= 0.57
* numpy >= 1.24
* gdal >= 3.6.2


### Before running the downloader
You need to authenticate **gsutil** the very first time before you run this code. 
In order to do this, in the enviroment of your choice, run:

> gcloud auth login

and follow the instructions that appear in the terminal.

### Usage
#### Downloader
Run in the terminal:
    
> python3 path/to/main.py -lat=your_latitude -lon=your_longitude -ID=a_super_cool_id -sd=your_start_date -ed=your_end_date

For additional input info just type:

> python3 path/to/main.py -h

#### JP2 to GeoTIFF converter
Run in the terminal:

> python3 path/to/jp2_to_tiff.py -ID=a_super_cool_id

For additional input info just type:

> python3 path/to/jp2_to_tiff.py -ID=a_super_cool_id