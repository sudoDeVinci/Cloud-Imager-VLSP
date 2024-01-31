import matplotlib.pyplot as plt
from sklearn.preprocessing import MinMaxScaler
from sklearn.discriminant_analysis import QuadraticDiscriminantAnalysis
from mlxtend.plotting import plot_decision_regions

from concurrent.futures import ProcessPoolExecutor

from config import *
from extract import raw_images, get_tags


sub_dir = f"QDA/{camera}"


def __plot(sky_folder:str, cloud_folder:str, colour_index: int) -> None:
  pass

def __main(colour_index: int) -> None:
    
    # PCA performed for RGB, HSV or YCbCr.
    try:
        __plot(sky_images_folder, cloud_images_folder, colour_index)
    except Exception as e:
        debug(e)

    debug(f"Process {colour_index} done.")
    

if __name__ == '__main__':
    start = datetime.now()
    mkdir(f"{root_graph_folder}/{sub_dir}")

    workers = 3
    
    # create a process pool
    with ProcessPoolExecutor(max_workers=workers) as executor:
        _ = executor.map(__main, range(workers))
    end = datetime.now()
    runtime = end-start
    debug(f'\n> Runtime : {runtime} \n')