from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
import matplotlib.pyplot as plt
from concurrent.futures import ProcessPoolExecutor

from config import *
from extract import *

sub_graph_dir = f"PCA/{camera}"


def pca(sky_folder:str, cloud_folder:str, colour_index: int) -> None:
    """
    Graph the Principle components. 
    The principle components depend on the color channels used.
    """
    tags = get_tags(colour_index)
    components = tags[0]
    colour_tag = tags[1]
    del tags

    # Process images
    data_sky = process_images(sky_folder, colour_index)
    data_cloud = process_images(cloud_folder, colour_index)
    
    # Standardize the data
    scaler = StandardScaler()
    data_sky_standardized = scaler.fit_transform(data_sky)
    data_cloud_standardized = scaler.fit_transform(data_cloud)
    
    # Perform PCA
    pca_sky = PCA(n_components = 3)
    pca_cloud = PCA(n_components = 3)

    pca_result_sky = pca_sky.fit_transform(data_sky_standardized)
    pca_result_cloud = pca_cloud.fit_transform(data_cloud_standardized)

    # Get the eigenvectors (principal components)
    eigenvectors_sky = pca_sky.components_
    eigenvectors_cloud = pca_cloud.components_

    # Get the explained variance ratios
    explained_variance_sky = pca_sky.explained_variance_ratio_
    explained_variance_cloud = pca_cloud.explained_variance_ratio_
    
    # Create Scree Plot for both datasets in a single plot.
    plot_scree([explained_variance_sky, explained_variance_cloud], [f"Sky - {colour_tag}", f"Cloud - {colour_tag}"], colour_tag)
    del data_cloud, data_sky, pca_cloud, pca_sky, data_sky_standardized, data_cloud_standardized
    collect()

    # Print the Eigenvectors
    debug(f"\nEigenvectors {colour_tag} - Sky:")
    for i in range(len(components)):
        debug(f"{components[i]}: {eigenvectors_sky[0, i]:.4f}")


    debug(f"\nPrincipal Component {colour_tag} - Cloud:")
    for i in range(len(components)):
        debug(f"{components[i]}: {eigenvectors_cloud[0, i]:.4f}")
    
    
    # Print the Variance ratios
    debug(f"\nVariance ratios {colour_tag} - Sky:")
    for i, ratio in enumerate(explained_variance_sky):
        debug(f"Component {i+1}: {ratio:.4f}")


    debug(f"\nVariance ratios {colour_tag} - Cloud:")
    for i, ratio in enumerate(explained_variance_cloud):
        debug(f"Component {i+1}: {ratio:.4f}")

    del eigenvectors_cloud, eigenvectors_sky, explained_variance_cloud, explained_variance_sky

    # Plot the PCA graph
    # debug(pca_result_cloud[:, 0])
    plot_pca(colour_tag, pca_result_cloud, pca_result_sky)
    collect()      
    
    
def plot_pca(colour_tag: str, pca_result_cloud: np.array, pca_result_sky: np.array) -> None:
    """"
    Plot PCA Scatterplot 
    """
    debug(f"\nCreating {colour_tag} PCA ScatterPlot ...")
    _,ax = plt.subplots(figsize=(10,6))
    ax.scatter(pca_result_sky[:, 0], pca_result_sky[:, 1], c='b', alpha = 0.1, marker = 'X', label = 'sky value')
    ax.scatter(pca_result_cloud[:, 0], pca_result_cloud[:, 1], c='r', alpha = 0.1, marker = 'X', label = 'cloud value')
    plt.legend(loc="upper left")
    plt.title('PCA')
    plt.xlabel('PC1')
    plt.ylabel('PC2')
    plt.savefig(f"{root_graph_folder}/{sub_graph_dir}/new_pca_{camera}_{colour_tag}.png")
    plt.clf  
    
    
def plot_scree(explained_variance_list: list[list[float]], labels: list[str], colour_tag: str) -> None:
    """
    Plot Scree Plot based on explained variance ratios for multiple datasets.
    """
    fig, ax = plt.subplots(nrows = 2, ncols = 1)
    ax = ax.flatten()
    
    explained_variance_sky = explained_variance_list[0]
    explained_variance_cloud = explained_variance_list[1]

    ax[0].bar(range(1, len(explained_variance_sky) + 1), explained_variance_sky, label=labels[0])
    ax[0].set_title("Scree Plot - Sky")
    ax[0].set_xlabel('Principal Component')
    ax[0].set_ylabel('Explained Variance Ratio')
    ax[0].legend(loc = "upper right")
    
    ax[1].bar(range(1, len(explained_variance_cloud) + 1), explained_variance_cloud, label=labels[1])
    ax[1].set_title("Scree Plot - Cloud")
    ax[1].set_xlabel('Principal Component')
    ax[1].set_ylabel('Explained Variance Ratio')
    ax[1].legend(loc = "upper right")
    
    fig.tight_layout()
    plt.legend()
    plt.savefig(f"{root_graph_folder}/{sub_graph_dir}/new_scree_{camera}_{colour_tag}.png")
    plt.clf()
    
    


def main(colour_index: int) -> None:
    
    # PCA performed for RGB, HSV or YCbCr.
    try:
        pca(sky_images_folder, cloud_images_folder, colour_index)
    except Exception as e:
        debug(e)
    debug(f"Process {colour_index} done.")


if __name__ == '__main__':
    start = datetime.now()
    mkdir(f"{root_graph_folder}/{sub_graph_dir}")
    workers = 3
    
    # create a process pool
    with ProcessPoolExecutor(max_workers=workers) as executor:
        _ = executor.map(main, range(workers))
    end = datetime.now()
    runtime = end-start
    debug(f'\n> Runtime : {runtime} \n')