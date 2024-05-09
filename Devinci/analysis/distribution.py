from Devinci.config import *
from Devinci.analysis.extract import get_nonblack_all, remove_outliers_iqr, Colour_Tag, count

import matplotlib.pyplot as plt
from concurrent.futures import ProcessPoolExecutor


def _distributionGenerator(cam: Camera, tag: Colour_Tag, data_cloud: NDArray, data_sky: NDArray):
    """
    Generate a histogram of the distribution of colours in the sky and cloud images for a given camera and colourspace.

    Args:
        cam (Camera): The camera for which the histogram is to be generated.
        tag (Colour_Tag): The colourspace in which the histogram is to be generated.
        data_cloud (NDArray): The array of cloud image data.
        data_sky (NDArray): The array of sky image data.
    """
    
    bg_color = '#f0f0f0'
    line_color = "#202330"

    fs = 30
    # Decompose into components channels and create frequency dist. for each
    x_cloud_freq = count(np.array(data_cloud[:, 0], dtype=np.uint8))
    y_cloud_freq = count(np.array(data_cloud[:, 1], dtype=np.uint8))
    z_cloud_freq = count(np.array(data_cloud[:, 2], dtype=np.uint8))

    x_sky_freq = count(np.array(data_sky[:, 0], dtype=np.uint8))    
    y_sky_freq = count(np.array(data_sky[:, 1], dtype=np.uint8))
    z_sky_freq = count(np.array(data_sky[:, 2], dtype=np.uint8))

    debug(f"\n> Creating {tag.value['tag']} Histogram ...")
    
    fig, (ax0, ax1, ax2) = plt.subplots(nrows = 3, ncols = 1)
    
    
    ax0.spines['top'].set_linewidth(0)
    ax0.spines['left'].set_linewidth(5)
    ax0.spines['right'].set_linewidth(0)
    ax0.spines['bottom'].set_linewidth(5)
    
    ax1.spines['top'].set_linewidth(0)
    ax1.spines['left'].set_linewidth(5)
    ax1.spines['right'].set_linewidth(0)
    ax1.spines['bottom'].set_linewidth(5)
    
    ax2.spines['top'].set_linewidth(0)
    ax2.spines['left'].set_linewidth(5)
    ax2.spines['right'].set_linewidth(0)
    ax2.spines['bottom'].set_linewidth(5)
    
    
    fig.set_figheight(40)
    fig.set_figwidth(40)
    fig.set_facecolor(bg_color)
    ax0.set_facecolor(bg_color)
    ax1.set_facecolor(bg_color)
    ax2.set_facecolor(bg_color)

    ax0.set_title(f"\n{tag.value['components'][0]} Colour Frequency\n", loc='center', fontsize = fs*1.25)
    ax0.bar(x_sky_freq[:,0], x_sky_freq[:,1], color="#dc267f", alpha=0.5, label = f'Sky {tag.value["components"][0]}')
    ax0.bar(x_cloud_freq[:,0], x_cloud_freq[:,1], color="green", alpha=0.5, label = f'Cloud {tag.value["components"][0]}')
    ax0.set_xlabel(f"\n{tag.value['tag']} {tag.value['components'][0]} (0 - 255)\n", loc='center', fontsize = fs)
    ax0.set_ylabel(f"\nFrequency\n", loc='center', fontsize = fs)
    ax0.legend(loc='upper left', fancybox=True, shadow=True, ncol=1, facecolor = "#f3dec3", edgecolor = "#202330", labelcolor = "#202330", framealpha = 0.8, prop = {'weight':'bold', 'size':fs})
    ax0.tick_params(axis='both', which='major', labelsize=fs, width = 10)

    ax1.set_title(f"\n{tag.value['components'][1]} Colour Frequency\n", loc='center', fontsize = fs*1.25)
    ax1.bar(y_sky_freq[:,0], y_sky_freq[:,1], color="#ec3440", alpha=0.5, label = f'Sky {tag.value["components"][1]}')
    ax1.bar(y_cloud_freq[:,0], y_cloud_freq[:,1], color="#02afd7", alpha=0.5, label = f'Cloud {tag.value["components"][1]}')
    ax1.set_xlabel(f"\n{tag.value['tag']} {tag.value['components'][1]} (0 - 255)\n", loc='center', fontsize = fs)
    ax1.set_ylabel(f"\nFrequency\n", loc='center', fontsize = fs)
    ax1.legend(loc='upper left', fancybox=True, shadow=True, ncol=1, facecolor = "#f3dec3", edgecolor = "#202330", labelcolor = "#202330", framealpha = 0.8, prop = {'weight':'bold', 'size':fs})
    ax1.tick_params(axis='both', which='major', labelsize=fs, width = 10)

    ax2.set_title(f"\n{tag.value['components'][2]} Colour Frequency\n", loc='center', fontsize = fs*1.25)
    ax2.bar(z_sky_freq[:,0], z_sky_freq[:,1], color="#fe6100", alpha=0.5, label = f'Sky {tag.value["components"][2]}')
    ax2.bar(z_cloud_freq[:,0], z_cloud_freq[:,1], color="#6227ae", alpha=0.5, label = f'Cloud {tag.value["components"][2]}')
    ax2.set_xlabel(f"\n{tag.value['tag']} {tag.value['components'][2]} (0 - 255)\n", loc='center', fontsize = fs)
    ax2.set_ylabel(f"\nFrequency\n", loc='center', fontsize = fs)
    ax2.legend(loc='upper left', fancybox=True, shadow=True, ncol=1, facecolor = "#f3dec3", edgecolor = "#202330", labelcolor = "#202330", framealpha = 0.8, prop = {'weight':'bold', 'size':fs})
    ax2.tick_params(axis='both', which='major', labelsize=fs, width = 10)

    fig.tight_layout(pad = 10)
    plt.savefig(os.path.join(cam.histogram_folder, f"{tag.value['tag']}.png"), edgecolor='none')
    plt.clf()

def _plot(cam: Camera, tag: Colour_Tag):
    """
    Plot the distribution of colours in the sky and cloud images for a given camera and colour tag.

    Retreives non-black pixel data from sky and cloud images, applies outlier removal via IQR filtering,
    and then generates a distribution histogram of the colours in the specified colour space.

    Args:
        cam (Camera): Camera object.
        tag (Colour_Tag): Colour space tag indicating the colour space.

    """
    # Get the sky and cloud data for a given camera in a tagged colourspace.
    sky = get_nonblack_all(cam.sky_images_folder, tag)
    cloud = get_nonblack_all(cam.cloud_images_folder, tag)

    # Remove outliers via simple IQR filtering.
    data_cloud = remove_outliers_iqr(cloud)
    data_sky = remove_outliers_iqr(sky)

    # Free up memory by deleting the original cloud and sky data arrays
    del cloud, sky

    # Generate and plot the distribution of colours in the sky and cloud data
    _distributionGenerator(cam, tag, data_cloud=data_cloud, data_sky=data_sky)

def _main(args: Tuple[Camera, Colour_Tag]) -> None:
    camera, tag = args
    if tag is Colour_Tag.UNKNOWN: return None
    try:
        _plot(cam = camera, tag = tag)
    except Exception as e:
        debug(f"Error plotting {tag.value['tag']}: {e}")

def create(camera: Camera, tags: List[Colour_Tag]) -> None:
    start = datetime.now()

    args = tuple((camera, t) for t in tags)
    workers = len(tags)

    # create a process pool
    with ProcessPoolExecutor(max_workers=workers) as executor:
        _ = executor.map(_main, args)


    end = datetime.now()
    runtime = end-start
    debug(f'\n> Runtime : {runtime} \n')

if __name__ == '__main__':

    camera = Camera(camera_model.DSLR)
    tags = [Colour_Tag.HSV, Colour_Tag.YCRCB, Colour_Tag.RGB]
    create(camera, tags)