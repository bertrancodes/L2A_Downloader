import argparse
import numpy as np
from osgeo import gdal
from pathlib import Path
from numba import njit
from tqdm.auto import tqdm


@njit
def upscale(n2dimage, scale_factor):
    """
    Custom function to upscale an image while preserving original values, 
    dividing the original pixel
    """
    scale_factorInt = int(scale_factor)
    
    if scale_factor/scale_factorInt == 1:
        rows, cols = n2dimage.shape
        scaled_n2dimage = np.zeros((scale_factorInt*rows, scale_factorInt*cols))

        for row in range(rows):
            for col in range(cols):
                value = n2dimage[row, col]
                scaled_n2dimage[row * scale_factorInt: (row+1) * scale_factorInt, col *  scale_factorInt: (col+1) * scale_factorInt] =  value

        return scaled_n2dimage

    else:
        print('Invalid scale factor. Use int or int-like floats')
        return


def jp2_to_tiff(dir_id : str) -> None: 
    """
    Convert all the jp2 images inisde a directory ID into a multiband,
    compressed GeoTIFF. This process reescales all data to 10m spatial
    resolution while preservig original values.
    """
    s2_products = Path(f'../data/{dir_id}')
    total_len = len([s2_product for s2_product in s2_products.iterdir()])

    for s2_product in tqdm(s2_products.iterdir(), ascii = True,
                           position = 0, leave = True, total = total_len,
                           desc = 'Converting .jp2 to multiband compressed GeoTIFF'):

        granule_directory = [granule for granule in (s2_product / 'GRANULE').iterdir()][0]
        tiff_file = s2_product / (granule_directory.name + '.tif')

        if not tiff_file.exists():
            print(f'Reading band data of {granule_directory.name}')

            res10_directory = granule_directory / 'IMG_DATA' / 'R10m'
            res20_directory = granule_directory / 'IMG_DATA' / 'R20m'
            res60_directory = granule_directory / 'IMG_DATA' / 'R60m'
            
            # Let the band festival begin

            b01_jp2 = [band for band in res60_directory.iterdir() if str(band).endswith('B01_60m.jp2')][0]
            
            b02_jp2 = [band for band in res10_directory.iterdir() if str(band).endswith('B02_10m.jp2')][0]
            b03_jp2 = [band for band in res10_directory.iterdir() if str(band).endswith('B03_10m.jp2')][0]
            b04_jp2 = [band for band in res10_directory.iterdir() if str(band).endswith('B04_10m.jp2')][0]
            
            b05_jp2 = [band for band in res20_directory.iterdir() if str(band).endswith('B05_20m.jp2')][0]
            b06_jp2 = [band for band in res20_directory.iterdir() if str(band).endswith('B06_20m.jp2')][0]
            b07_jp2 = [band for band in res20_directory.iterdir() if str(band).endswith('B07_20m.jp2')][0]
            
            b08_jp2 = [band for band in res10_directory.iterdir() if str(band).endswith('B08_10m.jp2')][0]

            b8a_jp2 = [band for band in res20_directory.iterdir() if str(band).endswith('B8A_20m.jp2')][0]

            b09_jp2 = [band for band in res60_directory.iterdir() if str(band).endswith('B09_60m.jp2')][0]

            b11_jp2 = [band for band in res20_directory.iterdir() if str(band).endswith('B11_20m.jp2')][0]
            b12_jp2 = [band for band in res20_directory.iterdir() if str(band).endswith('B12_20m.jp2')][0]
            scl_jp2 = [band for band in res20_directory.iterdir() if str(band).endswith('SCL_20m.jp2')][0]

            # Read band meaningful data
            b01_ds = gdal.Open(str(b01_jp2))
            b01_data = b01_ds.GetRasterBand(1).ReadAsArray()
            b01_ds = None
            
            b02_ds = gdal.Open(str(b02_jp2))
            b02_xsize = b02_ds.RasterXSize
            b02_ysize = b02_ds.RasterYSize
            b02_geotrans = b02_ds.GetGeoTransform()
            b02_crs = b02_ds.GetProjection()
            b02_data = b02_ds.GetRasterBand(1).ReadAsArray()
            b02_ds = None

            b03_ds = gdal.Open(str(b03_jp2))
            b03_data = b03_ds.GetRasterBand(1).ReadAsArray()
            b03_ds = None

            b04_ds = gdal.Open(str(b04_jp2))
            b04_data = b04_ds.GetRasterBand(1).ReadAsArray()
            b04_ds = None

            b05_ds = gdal.Open(str(b05_jp2))
            b05_data = b05_ds.GetRasterBand(1).ReadAsArray()
            b05_ds = None

            b06_ds = gdal.Open(str(b06_jp2))
            b06_data = b06_ds.GetRasterBand(1).ReadAsArray()
            b06_ds = None

            b07_ds = gdal.Open(str(b07_jp2))
            b07_data = b07_ds.GetRasterBand(1).ReadAsArray()
            b07_ds = None

            b08_ds = gdal.Open(str(b08_jp2))
            b08_data = b08_ds.GetRasterBand(1).ReadAsArray()
            b08_ds = None

            b8a_ds = gdal.Open(str(b8a_jp2))
            b8a_data = b8a_ds.GetRasterBand(1).ReadAsArray()
            b8a_ds = None

            b09_ds = gdal.Open(str(b09_jp2))
            b09_data = b09_ds.GetRasterBand(1).ReadAsArray()
            b09_ds = None

            b11_ds = gdal.Open(str(b11_jp2))
            b11_data = b11_ds.GetRasterBand(1).ReadAsArray()
            b11_ds = None

            b12_ds = gdal.Open(str(b12_jp2))
            b12_data = b12_ds.GetRasterBand(1).ReadAsArray()
            b12_ds = None

            scl_ds = gdal.Open(str(scl_jp2))
            scl_data = scl_ds.GetRasterBand(1).ReadAsArray()
            scl_ds = None

            # Scale bands to 10m while preserving values
            # tqdm.set_description('Upscaling bands to 10m...')
            b01_data = upscale(b01_data, scale_factor = 6)
            
            b05_data = upscale(b05_data, scale_factor = 2)
            b06_data = upscale(b06_data, scale_factor = 2)
            b07_data = upscale(b07_data, scale_factor = 2)
            b8a_data = upscale(b8a_data, scale_factor = 2)
            
            b09_data = upscale(b09_data, scale_factor = 6)
            
            b11_data = upscale(b11_data, scale_factor = 2)
            b12_data = upscale(b12_data, scale_factor = 2)
            scl_data = upscale(scl_data, scale_factor = 2)

            
            # Create the tif file
            # tqdm.set_description('Writting to compressed GeoTIFF...')
            opts = ['COMPRESS=DEFLATE', 'NUM_THREADS=ALL_CPUS']
            datatype = gdal.GDT_Int16
            driver = gdal.GetDriverByName('GTiff')
            res10_xsize = b02_xsize
            res10_ysize = b02_ysize
            total_bands = 13
            
            # Set tif metadata
            tiff_ds = driver.Create(str(tiff_file), res10_xsize, res10_ysize, total_bands, datatype, options = opts)
            tiff_ds.SetGeoTransform(b02_geotrans)
            tiff_ds.SetProjection(b02_crs)
            
            # Write bands to tif
            b01_tiff = tiff_ds.GetRasterBand(1)
            b01_tiff.WriteArray(b01_data)
            b01_tiff.SetDescription('B01: Coastal aerosol')

            b02_tiff = tiff_ds.GetRasterBand(2)
            b02_tiff.WriteArray(b02_data)
            b02_tiff.SetDescription('B02: Blue')

            b03_tiff = tiff_ds.GetRasterBand(3)
            b03_tiff.WriteArray(b03_data)
            b03_tiff.SetDescription('B03: Green')

            b04_tiff = tiff_ds.GetRasterBand(4)
            b04_tiff.WriteArray(b04_data)
            b04_tiff.SetDescription('B04: Red')

            b05_tiff = tiff_ds.GetRasterBand(5)
            b05_tiff.WriteArray(b05_data)
            b05_tiff.SetDescription('B05: Vegetation red-edge 1')

            b06_tiff = tiff_ds.GetRasterBand(6)
            b06_tiff.WriteArray(b06_data)
            b06_tiff.SetDescription('B06: Vegetation red-edge 2')

            b07_tiff = tiff_ds.GetRasterBand(7)
            b07_tiff.WriteArray(b07_data)
            b07_tiff.SetDescription('B07: Vegetation red-edge 3')

            b08_tiff = tiff_ds.GetRasterBand(8)
            b08_tiff.WriteArray(b08_data)
            b08_tiff.SetDescription('B08: NIR')

            b8a_tiff = tiff_ds.GetRasterBand(9)
            b8a_tiff.WriteArray(b8a_data)
            b8a_tiff.SetDescription('B8A: Vegetation red-edge 4')

            b09_tiff = tiff_ds.GetRasterBand(10)
            b09_tiff.WriteArray(b09_data)
            b09_tiff.SetDescription('B09: Water vapour')

            b11_tiff = tiff_ds.GetRasterBand(11)
            b11_tiff.WriteArray(b11_data)
            b11_tiff.SetDescription('B11: SWIR 1')

            b12_tiff = tiff_ds.GetRasterBand(12)
            b12_tiff.WriteArray(b12_data)
            b12_tiff.SetDescription('B12: SWIR 2')

            scl_tiff = tiff_ds.GetRasterBand(13)
            scl_tiff.WriteArray(scl_data)
            scl_tiff.SetDescription('SCL: Scene classification')

            tiff_ds = None

            # tqdm.set_description('Done!')

        else:
            print(f'WARNING: GeoTIFF file for image {s2_product} already exists. Skipping to next image...')

    return


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description = "Convert Sentinel-2 Level 2A .jp2 \
                                     single band images to a multiband compressed GeoTIFF",
                                 formatter_class= argparse.MetavarTypeHelpFormatter)
    
    parser.add_argument("-ID", "--dir-id", required = True, 
                        help = "Directory name to convert", type = str)


    args = parser.parse_args()
    config = vars(args)
    print(config)

    dir_id = config['dir_id']

    jp2_to_tiff(dir_id)
