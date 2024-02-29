import matplotlib.pyplot as plt
from datetime import datetime
from concurrent.futures import ProcessPoolExecutor
from config import *
from scipy import stats
from extract import centered_images, raw_images, get_tags

sub_graph_dir = f"hist/{camera}"


def __count(xyz_sk: NDArray) -> NDArray:
    """
    Return a frequency table of the integers in an input array
    """
    unique, counts = np.unique(xyz_sk, return_counts=True)
    freq = np.asarray((unique, counts)).T
    return freq

def __check_distribution(data: NDArray, label:str):
    distributions = {
        "Normal": {"func": stats.norm, "params": stats.norm.fit(data)},
        "Beta": {"func": stats.beta, "params": stats.beta.fit(data)},
        "Chi-Squared": {"func": stats.chi2, "params": stats.chi2.fit(data)}
    }

    results = {}
    for dist_name, dist in distributions.items():
        _, p_value = stats.kstest(data, dist["func"].name, args=dist["params"])
        results[dist_name] = p_value

    # Print the results
    print(f"Distribution Test Results - {label}")
    for dist_name, p_value in results.items():
        print(f"{dist_name}: p-value = {p_value:.4f}")

    return results


def __calculate_ratios(image_data: NDArray) -> NDArray:
    """
    Calculate the ratio of blue to red, blue to green, and green to red for each pixel.
    """
    red = image_data[:, 0]
    green = image_data[:, 1]
    blue = image_data[:, 2]

    blue_to_red = blue/red
    blue_to_green = blue/green
    green_to_red = green/red

    return np.column_stack((blue_to_red, blue_to_green, green_to_red))


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
    data_sky = raw_images(sky_folder, colour_index)
    data_cloud = raw_images(cloud_folder, colour_index)
    
    for i in range(3):
        c_data = data_cloud[i]
        s_data = data_sky[i]
        __check_distribution(c_data, f"Cloud {components[i]}")
        debug("\n")
        __check_distribution(s_data, f"Sky {components[i]}")
        debug("\n")

    """
    # Get the ratios
    ratios_sky = __calculate_ratios(data_sky)
    ratios_cloud = __calculate_ratios(data_cloud)

    del data_cloud, data_sky

    btr_cloud_freq = __count(np.array(ratios_cloud[:, 0]))
    btg_cloud_freq = __count(np.array(ratios_cloud[:, 1]))
    gtr_cloud_freq = __count(np.array(ratios_cloud[:, 2]))
    
    btr_sky_freq = __count(np.array(ratios_sky[:, 0]))
    btg_sky_freq = __count(np.array(ratios_sky[:, 1]))
    gtr_sky_freq = __count(np.array(ratios_sky[:, 2]))
    distributionBarGraphGenerator([btr_cloud_freq, btr_sky_freq],
                                [btg_cloud_freq, btg_sky_freq],
                                [gtr_cloud_freq, gtr_sky_freq],
                                [   f"{components[2]} to {components[0]}",
                                    f"{components[2]} to {components[1]}",
                                    f"{components[1]} to {components[0]}"], 
                                colour_tag,
                                f"{root_graph_folder}/{sub_graph_dir}/new_hist_{camera}_{colour_tag}_RATIOS.png")
   
    del btr_cloud_freq, btr_sky_freq
    del btg_cloud_freq, btg_sky_freq
    del gtr_cloud_freq, gtr_sky_freq
    collect()
    """
    

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

    debug(f"\n> Creating {colour_tag} RATIO Histogram ...")
    fig,axes1 = plt.subplots(nrows = 3, ncols = 1)
    axes1 = axes1.flatten()

    axes1[0].set_title(f"{colour_tag} Channel Ratio Frequency", loc='center')
    axes1[0].bar(x_s[:,0], x_s[:,1], color = 'red', alpha= 0.3, label = f'Sky {components[0]}')
    axes1[0].bar(x_c[:,0], x_c[:,1], color = 'green',alpha = 0.3,label = f'Cloud {components[0]}')
    axes1[0].set_xlabel(f'{colour_tag} {components[0]} (0 - 255)')
    axes1[0].set_ylabel('frequency')
    axes1[0].legend(loc="upper left")
    del x_s, x_c

    axes1[1].bar(y_s[:,0], y_s[:,1], color = 'blue', alpha= 0.3, label = f'Cloud {components[1]}')
    axes1[1].bar(y_c[:,0], y_c[:,1], color = 'yellow', alpha = 0.3, label = f'Sky {components[1]}')
    axes1[1].set_xlabel(f'{colour_tag} {components[1]} (0 - 255)')
    axes1[1].set_ylabel('frequency')
    axes1[1].legend(loc="upper left")
    del y_s, y_c

    axes1[2].bar( z_s[:,0], z_s[:,1], color = 'orange', alpha= 0.3, label = f'Cloud {components[2]}')
    axes1[2].bar(z_c[:,0], z_c[:,1], color = 'purple', alpha = 0.3, label = f'Sky {components[2]}')
    axes1[2].set_xlabel(f'{colour_tag} {components[2]} (0 - 255)')
    axes1[2].set_ylabel('frequency')
    axes1[2].legend(loc="upper left")
    del z_s, z_c
    
    fig.tight_layout(pad=1)
    
    plt.savefig(savepath)
    plt.clf()
    collect()
    print(f" └ {colour_tag} Histogram created.")
    
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