import lightkurve as lk
from astropy.coordinates import SkyCoord
import os
import sys
import logging
# Configure logging to write to a file

logging.basicConfig(filename='tess_download.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')


def download_tess_data(tic_id, download_dir="TessData"):
    """
    Downloads TESS light curves or target pixel files for a given TIC ID.

    Parameters:
    - tic_id (str): The TIC ID of the target (e.g., '25155310').
    - download_dir (str): Directory where files will be saved.

    Returns:
    - None
    """
    # Ensure the download directory exists
    Target = f"TIC {tic_id}"
    search_result = lk.search_lightcurve(Target, mission="TESS")
    #search_result = lk.search_lightcurve(Target)
    #print(search_result)
    SaveDirectory = os.path.join(download_dir, Target.replace(" ", ""))

    if not os.path.exists(SaveDirectory):
        os.makedirs(SaveDirectory)
    
    for file2download in search_result:
        try:
            lc = file2download.download(download_dir=SaveDirectory)
        except Exception as e:
            pass
            #print(f"Error downloading {file2download} due to {e}")
        print(lc)

        logging.info(f"Downloaded TESS data for TIC ID {tic_id} to {SaveDirectory}")
# Example Usage
tic_id = "3666880"  # Replace with your desired TIC ID
download_tess_data(tic_id)
