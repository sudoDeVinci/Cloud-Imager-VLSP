import matplotlib.pyplot as plt
from datetime import datetime
from concurrent.futures import ProcessPoolExecutor
from config import *
from extract import centered_images, raw_images, get_tags
from scipy import stats


sub_graph_dir = f"hist/{camera}"



def __count(xyz_sk: NDArray) -> NDArray:
    """
    Return a frequency table of the integers in an input array
    """
    unique, counts = np.unique(xyz_sk, return_counts=True)
    freq = np.asarray((unique, counts)).T
    return freq


def remove_outliers_z_score(data: NDArray, threshold: float = 3.0) -> NDArray:
    """
    Remove outliers from data using the Z-score method.
    Data points with a Z-score greater than the threshold will be considered as outliers.
    """
    z_scores = np.abs(stats.zscore(data))
    return data[(z_scores < threshold).all(axis=1)]


def __plot(sky_folder:str, cloud_folder:str, colour_index: int) -> None:
    """
    Plot
    """
    # The colour tag is a tag used to show the corresponding graphs which channels were used.
    #debug("getting tags")

    temp = get_tags(colour_index)

    #debug(temp)

    components = temp[0] 
    colour_tag = temp[1]
    del temp

    #debug(colour_tag)

    # Process images
    sky = raw_images(sky_folder, colour_index)
    cloud = raw_images(cloud_folder, colour_index)

    # Approximate to normal and remove outliers via z-score using p = 3.0.
    data_cloud = remove_outliers_z_score(cloud)
    data_sky = remove_outliers_z_score(sky)

    del cloud, sky
    
    x_cloud_freq = __count(np.array(data_cloud[:, 0]))
    y_cloud_freq = __count(np.array(data_cloud[:, 1]))
    z_cloud_freq = __count(np.array(data_cloud[:, 2]))

    del data_cloud
    
    x_sky_freq = __count(np.array(data_sky[:, 0]))
    y_sky_freq = __count(np.array(data_sky[:, 1]))
    z_sky_freq = __count(np.array(data_sky[:, 2]))
    
    del data_sky
    
    debug(">> " + str(x_cloud_freq[0]))
    
    distributionBarGraphGenerator([x_cloud_freq, x_sky_freq], [y_cloud_freq, y_sky_freq], [z_cloud_freq, z_sky_freq], components, colour_tag, f"{root_graph_folder}/{sub_graph_dir}/new_hist_{camera}_{colour_tag}.png")
    del x_cloud_freq, y_cloud_freq, z_cloud_freq
    del x_sky_freq, y_sky_freq, z_sky_freq
    collect()


    # Process images
    data_sky = centered_images(sky_folder, colour_index)
    data_cloud = centered_images(cloud_folder, colour_index)

    
    x_cloud_freq = __count(np.array(data_cloud[:, 0]))
    y_cloud_freq = __count(np.array(data_cloud[:, 1]))
    z_cloud_freq = __count(np.array(data_cloud[:, 2]))

    del data_cloud
    
    x_sky_freq = __count(np.array(data_sky[:, 0]))
    y_sky_freq = __count(np.array(data_sky[:, 1]))
    z_sky_freq = __count(np.array(data_sky[:, 2]))
    
    del data_sky
    
    debug(">> " + str(x_cloud_freq[0]))
    
    distributionBarGraphGenerator([x_cloud_freq, x_sky_freq], [y_cloud_freq, y_sky_freq], [z_cloud_freq, z_sky_freq], components, colour_tag, f"{root_graph_folder}/{sub_graph_dir}/new_hist_{camera}_{colour_tag}_centered.png")
    del x_cloud_freq, y_cloud_freq, z_cloud_freq
    del x_sky_freq, y_sky_freq, z_sky_freq
    collect()





def distributionBarGraphGenerator(x, y, z, components: list[str,str,str], colour_tag: str, savepath:str) -> None:
    """
    Generate a Histogram Showing the distribution of Cloud versus sky pixels as it pertains to 
    their (3) colour channels.
    """
    
    x_c = x[0]
    x_s = x[1]
    y_c = y[0]
    y_s = y[1]
    z_c = z[0]
    z_s = z[1]
    
    #bins = [*range(0,256,1)]

    #print(f"> There are: \n └  {sum(cloudBlues)} cloud datapoints\n └  {sum(skyBlues)} sky datapoints")

    debug(f"\n> Creating {colour_tag} Histogram ...")
    fig,axes1 = plt.subplots(nrows = 3, ncols = 1)
    axes1 = axes1.flatten()

    axes1[0].set_title(f"{colour_tag} Colour Frequency", loc='center')
    axes1[0].bar(x_s[:,0], x_s[:,1], color = 'red', alpha= 0.3, label = f'Sky {components[0]}')
    axes1[0].bar(x_c[:,0], x_c[:,1], color = 'orange',alpha = 0.3,label = f'Cloud {components[0]}')
    axes1[0].set_xlabel(f'{colour_tag} {components[0]} (0 - 255)')
    axes1[0].set_ylabel('frequency')
    axes1[0].legend(loc="upper left")
    del x_s, x_c

    axes1[1].bar(y_s[:,0], y_s[:,1], color = 'green', alpha= 0.3, label = f'Cloud {components[1]}')
    axes1[1].bar(y_c[:,0], y_c[:,1], color = 'yellow', alpha = 0.3, label = f'Sky {components[1]}')
    axes1[1].set_xlabel(f'{colour_tag} {components[1]} (0 - 255)')
    axes1[1].set_ylabel('frequency')
    axes1[1].legend(loc="upper left")
    del y_s, y_c

    axes1[2].bar( z_s[:,0], z_s[:,1], color = 'blue', alpha= 0.3, label = f'Cloud {components[2]}')
    axes1[2].bar(z_c[:,0], z_c[:,1], color = 'purple', alpha = 0.3, label = f'Sky {components[2]}')
    axes1[2].set_xlabel(f'{colour_tag} {components[2]} (0 - 255)')
    axes1[2].set_ylabel('frequency')
    axes1[2].legend(loc="upper left")
    del z_s, z_c
    
    fig.tight_layout(pad=1)
    
    plt.savefig(savepath)
    plt.clf()
    collect()
    print(f" └ {colour_tag} Bar Graph created.")
    
    
def __main(colour_index: int) -> None:
    # PCA performed for RGB, HSV or YCbCr.
    try:
        __plot(sky_images_folder, cloud_images_folder, colour_index)
    except Exception as e:
        debug(e)

    debug(f"Process {colour_index} done.")
    

if __name__ == '__main__':
    start = datetime.now()
    mkdir(f"{root_graph_folder}/{sub_graph_dir}")

    workers = 3
    
    # create a process pool
    with ProcessPoolExecutor(max_workers=workers) as executor:
        _ = executor.map(__main, range(workers))
    end = datetime.now()
    runtime = end-start
    debug(f'\n> Runtime : {runtime} \n')