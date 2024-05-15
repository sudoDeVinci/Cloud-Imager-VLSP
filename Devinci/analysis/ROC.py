from Devinci.config import *
from Devinci.analysis.extract import Colour_Tag, Matlike, np, ChannelBound, get_nonblack_all, count, remove_outliers_iqr
from matplotlib import pyplot as plt
from numba import njit, types, prange
from functools import reduce
from sklearn.metrics import auc
from concurrent.futures import ProcessPoolExecutor, Future


# Taking a matrix of size 5 as the kernel 
KERNEL = np.ones((5, 5), np.uint8) 
Number = TypeVar("Number", float, int, np.uint, intp)
ScoreDict = TypeVar("ScoreDict", Dict[str, List[List[List[ChannelBound]]]], None)


def _scoredict_vis(CAM:Camera, result: ScoreDict) -> None:
    
    debug(f"\n- {CAM.Model.value.upper()} Jaccard Similarities") 
    debug("--------------------------------")
    debug(f"| {'Channel':^18} | {'Score':>7}  |")
    debug("--------------------------------")
    for channel, n_dict in result.items():
        debug(f"| {channel:<18} | {n_dict['score']:5f} |")
    debug("--------------------------------")
    
def _optimaldict_vis(CAM:Camera, optimal_dict: Dict[str, Dict[str, ChannelBound|float]]) -> None:
    debug(f"\n- {CAM.Model.value.upper()} Optimal Channel Boundaries") 
    debug("-------------------------------------------------")
    debug(f"| {'Channel':^18} | {'Lower - Upper':>10} | {'AUC':^8} | {'Accuracy':^8}") 
    debug("-------------------------------------------------")
    for channel, ldict in optimal_dict.items():
        debug(f"| {channel:<18} | {ldict['bound'].lower_bound if ldict['bound'] is not None else "None":<5} - {ldict['bound'].upper_bound if ldict['bound'] is not None else "None":>5} |  {ldict['AUC'] if ldict['AUC'] is not None else "None":.4f}  |  {ldict['Accuracy'] if ldict['Accuracy'] is not None else "None":.4f}")
    debug("-------------------------------------------------")


def _generate_permutations(min_width: int = 2, max_count: Optional[int] = None) -> Tuple[Tuple[int, int]]:
    """
    Generate permutations of lower and upper bounds within a specified range with a minimum width.

    Args:
    - min_width (int): The minimum width between lower and upper bounds.
    - lower_bound (int): The lower bound of the range.
    - upper_bound (int): The upper bound of the range.

    Returns:
    - List[Tuple[int, int]]: A list of tuples representing valid permutations of lower and upper bounds.
    """
    valid_permutations = []

    for lower in range(0, 256):
        for upper in range(lower, 256, 5):  # Adjusted upper bound based on lower and min_width
            if upper - lower >= min_width:
                valid_permutations.append((lower, upper))

    return valid_permutations

def colourspace_similarity_test(cam: Camera, colours: List[Colour_Tag], overwrite: Optional[bool] = False) -> ScoreDict:
    
    """
    Calculates and returns a SORTED dictionary of Jaccard similarity scores between sky and cloud colour channels
    across various colour spaces for a given camera model. 
    A lower score indicates a better distinction between sky and clouds in that colour channel.

    Args:
        cam (Camera): An instance of the Camera class, representing the camera model for which the analysis is performed.
        colours (List[Colour_Tag]): A list of Colour_Tag enums representing the colour spaces to be analyzed.
        overwrite (bool, optional): A flag to determine whether to overwrite existing cached results. If False, the function
                                     will attempt to load and return cached results to save computation time. Defaults to False.

    Returns:
        ScoreDict: A dictionary where keys are strings combining the colour space tag and the channel name, and values are
                   dictionaries containing the 'score' (Jaccard similarity) and 'index' (channel index) for each channel.
                   The dictionary is sorted by the Jaccard similarity scores in ascending order, prioritizing channels with
                   scores below 0.5 to highlight those with better discrimination between sky and cloud distributions.
    """
    cached_file = os.path.join(cam.cache_folder, "jaccard.pkl")

    if not overwrite:
        cached_data = unpickle_file(cached_file)
        if cached_data: return cached_data

    result = {ctag.value["tag"]: {
                        f"{ctag.value['components'][0]}": {
                                                            "score":None,
                                                            "index": 0
                                                            },
                        f"{ctag.value['components'][1]}": {
                                                            "score":None,
                                                            "index": 1
                                                            },
                        f"{ctag.value['components'][2]}": {
                                                            "score":None,
                                                            "index": 2
                                                            }
                            } for ctag in colours}

    for tag in colours:
        cloud = get_nonblack_all(cam.cloud_images_folder, tag)
        sky = get_nonblack_all(cam.sky_images_folder, tag)

        data_cloud = remove_outliers_iqr(cloud)
        data_sky = remove_outliers_iqr(sky)
        
        x_cloud_freq = count(np.array(data_cloud[:, 0]))
        y_cloud_freq = count(np.array(data_cloud[:, 1]))
        z_cloud_freq = count(np.array(data_cloud[:, 2]))
        
        x_sky_freq = count(np.array(data_sky[:, 0]))
        y_sky_freq = count(np.array(data_sky[:, 1]))
        z_sky_freq = count(np.array(data_sky[:, 2]))
        
        x_cloud_set = x_cloud_freq[:, 0]
        y_cloud_set = y_cloud_freq[:, 0]
        z_cloud_set = z_cloud_freq[:, 0]

        x_sky_set = x_sky_freq[:, 0]
        y_sky_set = y_sky_freq[:, 0]
        z_sky_set = z_sky_freq[:, 0]

        # Calculate Jaccard similarity for each component
        x_similarity = _jaccard(x_cloud_set, x_sky_set)
        y_similarity = _jaccard(y_cloud_set, y_sky_set)
        z_similarity = _jaccard(z_cloud_set, z_sky_set)

        tag = tag.value
        result[tag['tag']][f"{tag['components'][0]}"]["score"] = x_similarity
        result[tag['tag']][f"{tag['components'][1]}"]["score"] = y_similarity
        result[tag['tag']][f"{tag['components'][2]}"]["score"] = z_similarity


    # Flatten the nested dictionary and format the keys
    flattened_dict = {
        f'{key1}-{key2}': value2
        for key1, value1 in result.items()
        for key2, value2 in value1.items()
    }


    # Filter dictionary entries with values <= 0.5
    filtered_dict = {key: value for key, value in flattened_dict.items() if value["score"] < 0.4}

    # Sort the filtered dictionary by score
    sorted_data = dict(sorted(filtered_dict.items(), key=lambda item: item[1]['score']))

    pickle_file(cached_file, sorted_data)

    return sorted_data

def _jaccard(array1: Iterable[Number], array2: Iterable[Number]) -> float:
    """
    Calculate the Jaccard similarity index between two arrays.

    The Jaccard similarity index is a measure of similarity between two sets. 

    Args:
        array1 (Iterable[Number]): The first array to compare. It should be an iterable of numbers.
        array2 (Iterable[Number]): The second array to compare. It should be an iterable of numbers.

    Returns:
        float: The Jaccard similarity index between the two arrays. This is a value between 0 and 1,
        where 1 means the arrays are identical(ignoring order and multiplicity),
        and 0 means they have no elements in common.
    """

    set1 = set(array1)
    intersection = len(set1.intersection(array2))
    union = len(set1.union(array2))
    return intersection / union

def _get_freq_dist(image_folder: str, tag: Colour_Tag, index: int) -> NDArray:
    """
    Get the frequency distribution of a channel in a specific colour space.
    """
    data = remove_outliers_iqr(get_nonblack_all(image_folder, tag))
    return count(np.array(data[:, index]))

def _thresh(img: Matlike, index: int, bounds: Tuple[int, int]) -> Matlike:
    """
    Perform a thresholding operation on an image.

    Args:
        img (Matlike): The input image.
        index (int): The index of the color channel to threshold.
        bounds (Tuple[int, int]): A tuple containing the lower and upper bounds for the threshold.

    Returns:
        numpy.ndarray: The thresholded image.
    """
    img = cv2.resize(img,(400, 300))
    ub = [255, 255, 255]
    lb = [0, 0, 0]

    ub[index] = bounds[1]
    lb[index] = bounds[0]
    ub = np.array(ub)
    lb = np.array(lb)

    return cv2.inRange(img, lb, ub)

def _chbound_mean(roclistlist: List[List[ChannelBound]]) -> List[ChannelBound]:
        """
        Takes a list of lists of ChannelBound objects and returns a list of ChannelBound objects with the averages.
        The lists must be the same size.
        Args: 
            roclistlist (List[List[ChannelBound]]): A list of lists of ChannelBound objects.

        Returns:
            List[ChannelBound]: A list of lists of ChannelBound objects with the averages.
        """
        if len(roclistlist) == 0: return []
        if len(roclistlist) == 1: return roclistlist[0]

        og = len(roclistlist[0])
        samples = len(roclistlist) 
        for l in roclistlist:
            if len(l) != og: raise Exception("Lists not the same size")

        out = roclistlist[0]
        for roclist in roclistlist[1:]:
            for index, chbound in enumerate(roclist):
                out[index] += chbound
            
        
        for index in range(og):
            out[index] = out[index] / samples

        return out


def _select_optimal_bounds(DATA: Dict[str, Dict[int, List[ChannelBound]]]) -> Dict[str, Dict[str, Any]]:
    """
    Construct a dictionary of the optimal colour channels for a given camera given ROC curve data.

    Args:
        CAM (Camera): The camera being used.
        DATA (Dict[str, Dict[int, List[ChannelBound]]]): The ROC curve data.

    Returns:
        Dict[str, Dict[str, Any]]: _description_
    """
    def CHMAX(a: ChannelBound, b: ChannelBound) -> ChannelBound:
        ad = a.True_Positive_Rate - a.False_Positive_Rate
        bd = b.True_Positive_Rate - b.False_Positive_Rate
        
        if ad > bd: return a
        
        return b
    
    optimal_dict:Dict[str, Dict[str, ChannelBound|float]] = {}
    
    for channel, LB_DICT in DATA.items():
        
        optimal_dict[channel] = {"bound":None, "AUC": 0.0, "Accuracy": 0.0}
        
        for _, ROCL in LB_DICT.items():
            ROC = sorted(ROCL, key=lambda x: x.False_Positive_Rate)
            
            if len(ROC) == 1: continue
            
            tp_rates = np.array([ch.True_Positive_Rate for ch in ROC])
            fp_rates = np.array([ch.False_Positive_Rate for ch in ROC])

            AUC = auc(fp_rates, tp_rates)
            
            del fp_rates, tp_rates
            
            if AUC < 0.5: continue
            
            maxch = reduce(CHMAX, ROCL)
            maximal = maxch.True_Positive_Rate - maxch.False_Positive_Rate
            
            current = optimal_dict[channel]
            current_max = current['bound']

            if current_max is None or maximal > (current_max.True_Positive_Rate - current_max.False_Positive_Rate):
                optimal_dict[channel] = {"bound":maxch, "AUC": AUC, "Accuracy": maxch.Accuracy}
    
    return optimal_dict

def _bootstrap_indexes(indexes: List[int], stratum_size: Optional[int] = None, n_bootstraps: int = 100) -> List[List[int]]:
    """
    Split the dataset indexes into testing strata using bootstrapping.

    Parameters:
        indexes (List[int]): List of indexes to the dataset of images.
        stratum_size (int, optional): Number of items in each stratum. If None, the size is set to the total number of samples in the dataset.
        n_bootstraps (int, optional): Number of bootstrap iterations.

    Returns:
        List of Lists: List of testing strata.
    """
    testing_strata = []

    for _ in range(n_bootstraps):
        # Randomly sample with replacement for testing set
        n_samples = len(indexes)
        if stratum_size is None:
            stratum_size = n_samples
        test_indices = np.random.choice(n_samples, size=stratum_size, replace=True)
        test_set = [indexes[i] for i in test_indices]

        testing_strata.append(test_set)

    return testing_strata

def _bmpize(string: str) -> str:
    parts = os.path.splitext(string)
    return f"{parts[0]}.bmp"

def _average_scoredict(ROC_DATA: Dict[str, List[List[List[ChannelBound]]]]) -> Dict[str, Dict[int, List[ChannelBound]]]:
    averaged: Dict[str, Dict[int, List[ChannelBound]]] = {channel: {
                                                                    lb: _chbound_mean(roclistlist) for lb, roclistlist in enumerate(i) if len(roclistlist[0]) > 0
                                                                } for channel, i in ROC_DATA.items()
                                                        }
    return averaged

def graph_ROC(CAM:Camera, averaged: Dict[str, Dict[int, List[ChannelBound]]], STRATA_COUNT: Optional[int] = 30, STRATA_SIZE: Optional[int] = 30) -> None:
    """
    Graphsthe Receiver Operating Characteristic (ROC) curves for a given set of colour channels

    Args:
        averaged (Dict[str, List[List[List[ChannelBound]]]]): A dictionary containing the averaged ROC data.
        STRATA_COUNT (int, optional): The number of strata to use for bootstrapping. Defaults to 30.
        STRATA_SIZE (int, optional): The size of each stratum. Defaults to 30.
    """

    fs =  30

    for channel, lb_dict in averaged.items():
        PLOTTED = False
        
        fig, ax0 = plt.subplots(nrows=1, ncols=1)
        plt.xticks(fontsize=fs)
        plt.yticks(fontsize=fs)
        fig.set_figheight(40)
        fig.set_figwidth(40)
        # ax0.set_prop_cycle(color=COLOURS, marker=MARKERS)

        ax0.set_xlabel("\nFalse Positive Rate\n", fontsize=fs*1.25)
        ax0.set_ylabel("\nTrue Positive Rate\n", fontsize=fs*1.25)

        #ax1.set_xlabel("Precision")
        #ax1.set_ylabel("\nRecall\n")
        point_count = 0
        for LB, ROC in lb_dict.items():
            point_count += len(ROC)


        fig.suptitle(f'\n{channel} Colour-Boundary ROC for {CAM.Model.value} dataset\n Points: {point_count} | STRATA: {STRATA_COUNT} | IMAGES PER STRATA: {STRATA_SIZE} \n\n', fontsize=fs*1.5)

        for LB, ROCL in lb_dict.items():
            # Sort ROC array by ChannelBound.False_Positive_Rate in ascending order.
            ROC = sorted(ROCL, key=lambda x: x.False_Positive_Rate)
            if len(ROC) == 1:
                continue
            # precisions = np.array([ch.Precision for ch in ROC])
            tp_rates = np.array([ch.True_Positive_Rate for ch in ROC])
            fp_rates = np.array([ch.False_Positive_Rate for ch in ROC])

            AUC_roc = auc(fp_rates, tp_rates)
            # AUC_pr = auc(precisions, tp_rates)

            if AUC_roc >= 0.5:
                PLOTTED = True
                ax0.plot(fp_rates, tp_rates, linewidth=5, label = f"Lower bound of {str(LB):<3} | AUC: {AUC_roc:.6f}")
            # ax1.plot(precisions, tp_rates, alpha=0.75, label = f"Lower bound of {LB} | AUC: {AUC_pr:.4f}")
        
        if PLOTTED:
            x = [0.0, 1.0]
            y = [0.0, 1.0]
            
            ax0.plot(x, y, linewidth=7, linestyle='dashed', label = f"y = x | AUC: {0.5000:.4f}")
            
            ax0.legend(loc='upper center', bbox_to_anchor=(0.5, -0.1),
            fancybox=True, shadow=True, ncol=4, fontsize=fs)
            # ax1.legend(loc='upper center', bbox_to_anchor=(0.5, -0.05), fancybox=True, shadow=True, ncol=3)
            fig.tight_layout(pad=10)
            plt.savefig(os.path.join(CAM.roc_folder, f"{channel}.png")) 
        else: 
            plt.clf()
        
@njit(types.containers.UniTuple(types.float64, 4)
        (
            types.Array(types.uint8, 3, 'C'),
            types.Array(types.uint8, 3, 'C')
        ),
        parallel=False,
        fastmath = True)
def _runit( GROUND_TRUTH_MASKS: np.ndarray, 
            bound_masks: np.ndarray ) -> Tuple[float, float, float, float]:

    TP, TN, FP, FN = 0, 0, 0, 0

    for i in prange(GROUND_TRUTH_MASKS.shape[0]):
        GROUND_TRUTH_MASK = GROUND_TRUTH_MASKS[i]
        GROUND_TRUTH_MASK_NEG = ~GROUND_TRUTH_MASK
        bound_mask = bound_masks[i]
        bound_mask_neg = ~bound_mask

        TP += np.count_nonzero(GROUND_TRUTH_MASK & bound_mask)
        TN += np.count_nonzero(GROUND_TRUTH_MASK_NEG & bound_mask_neg)
        FP += np.count_nonzero(GROUND_TRUTH_MASK_NEG & bound_mask)
        FN += np.count_nonzero(GROUND_TRUTH_MASK & bound_mask_neg)

    True_Positive_Rate = TP / (TP + FN) if TP != 0 else 0
    False_Positive_Rate = FP / (FP + TN) if FP != 0 else 0
    Precision = TP / (TP + FP) if TP != 0 else 0
    Accuracy = (TP + TN) / (TP + TN + FP + FN) if TP!= 0 else 0
    
    return (True_Positive_Rate, False_Positive_Rate, Precision, Accuracy)

def _runstrata(  channel_index: int,
                channel_label: str,
                cloud_strata: List[List[int]],
                cloud_bound_perms: Tuple[Tuple[int, int]],
                IMAGE_MASKS: NDArray,
                CH_REFERENCES: NDArray) -> List[List[List[ChannelBound]]]:
    
    strat_count = len(cloud_strata)
    bound_count = len(cloud_bound_perms)
    looplist = [[[] for i in range(strat_count)] for _ in range(256)]

    for strat_dex, stratum in enumerate(cloud_strata):
        print(f"\n\n>> Testing {channel_label} Stratum {str(strat_dex+1).zfill(3)} of {str(strat_count).zfill(3)}")
        for bound_dex, bound in enumerate(cloud_bound_perms):
            GROUND_TRUTH_MASKS = np.array([IMAGE_MASKS[i] for i in stratum], dtype=np.uint8)
            BOUND_MASKS = np.array([_thresh(CH_REFERENCES[i], index=channel_index, bounds=bound) for i in stratum], dtype=np.uint8)

            True_Positive_Rate, False_Positive_Rate, Precision, Accuracy = _runit(GROUND_TRUTH_MASKS, BOUND_MASKS)
        
            looplist[bound[0]][strat_dex].append(ChannelBound(  bound[0], bound[1],
                                                                channel = channel_label,
                                                                True_Pos = True_Positive_Rate,
                                                                False_Pos = False_Positive_Rate,
                                                                pres = Precision,
                                                                acc = Accuracy
                                                            )
                                                )
            
            
    return looplist

def ROC(cam: camera_model, jaccard: ScoreDict = None, overwrite: bool = False, STRATA_COUNT: int = 30, STRATA_SIZE: int = 30, SAMPLE_POINTS: int = None) -> Dict[str, Dict[int, List[ChannelBound]]]:
    return _ROC(Camera(cam), jaccard = jaccard, tags = Colour_Tag.members(), overwrite=overwrite, STRATA_COUNT=STRATA_COUNT, SAMPLE_POINTS=SAMPLE_POINTS)

def _Confusion_Matrix_Dual(CAM: Camera, CH1: ChannelBound, CH2: ChannelBound) -> Tuple[float, float, float, float]:
    """"""
    ch1_parts = CH1.channel.split("-")
    ch2_parts = CH2.channel.split("-")
    ch1_label = ch1_parts[1]
    ch2_label = ch2_parts[1]
    ch1_tag = Colour_Tag.match(ch1_parts[0])
    ch2_tag = Colour_Tag.match(ch2_parts[0])

    if ch1_tag is Colour_Tag.UNKNOWN or ch2_tag is Colour_Tag.UNKNOWN: return None

    # Load the images and their masks.
    cloud_image_paths = tuple(os.listdir(CAM.cloud_images_folder))
    cloud_image_indexes = [i for i in range(len(cloud_image_paths))]
    # Partition the ground-truth image indexes into strata.
    # cloud_strata = _bootstrap_indexes(cloud_image_indexes, stratum_size=STRATA_SIZE, n_bootstraps=STRATA_COUNT)
    IMAGE_MASKS = np.array([cv2.cvtColor(cv2.imread(os.path.join(CAM.cloud_masks_folder, _bmpize(p))), cv2.COLOR_BGR2GRAY) for p in cloud_image_paths], dtype=np.uint8)
    REFERENCE_IMAGES = np.array([cv2.imread(os.path.join(CAM.reference_images_folder, p)) for p in cloud_image_paths], dtype=np.uint8)

    # Convert the Images for each channelbound
    CH1_REFERENCES = np.array([cv2.cvtColor(img, ch1_tag.value['converter']) for img in REFERENCE_IMAGES], dtype = np.uint8)
    CH2_REFERENCES = np.array([cv2.cvtColor(img, ch2_tag.value['converter']) for img in REFERENCE_IMAGES], dtype = np.uint8)

    ch1_index:int = ch1_tag.value['components'].index(ch1_label)
    CH1_BOUND_MASKS = np.array([_thresh(i, index=ch1_index, bounds=(CH1.lower_bound, CH1.upper_bound)) for i in CH1_REFERENCES], dtype = np.uint8)
     
    ch2_index:int = ch2_tag.value['components'].index(ch2_label)
    CH2_BOUND_MASKS = np.array([_thresh(i, index=ch2_index, bounds=(CH2.lower_bound, CH2.upper_bound)) for i in CH2_REFERENCES], dtype = np.uint8)
    
    FUSED_MASKS = np.array([ch1mask & ch2mask for ch1mask, ch2mask in zip(CH1_BOUND_MASKS, CH2_BOUND_MASKS)], dtype = np.uint8)

    return _runit(IMAGE_MASKS, FUSED_MASKS)
    


def _ROC(CAM: Camera, tags: List[Colour_Tag], jaccard:ScoreDict = None, overwrite: bool = False, STRATA_COUNT: int = 60, STRATA_SIZE: int = 30, SAMPLE_POINTS: int = None) -> Dict[str, Dict[int, List[ChannelBound]]]:
    """
    Calculates the Receiver Operating Characteristic (ROC) and Precision-Recall curves for a given camera and set of colour tags.

    Args:
        CAM (Camera): The camera used for image acquisition.
        tags (List[Colour_Tag]): The list of colour tags to use for analysis.
        overwrite (bool, optional): A flag to determine whether to overwrite existing cached results.
        STRATA_COUNT (int, optional): The number of strata to use for bootstrapping. Defaults to 30.
        STRATA_SIZE (int, optional): The size of each stratum. Defaults to 30.
        SAMPLE_POINTS (int, optional): The number of sample points to use for each stratum. Defaults to 500.

    Returns:
        Dict[str, Dict[int, List[ChannelBound]]]: A dictionary where keys are strings combining the colour space tag and the channel name, and values are dictionaries containing the 'score' (Jaccard similarity) and 'index' (channel index) for each channel.
        The dictionary is sorted by the Jaccard similarity scores in ascending order, prioritizing channels with scores below 0.5 to highlight those with better discrimination between sky and cloud distributions.
    """

    cloud_image_paths = tuple(os.listdir(CAM.cloud_images_folder))
    cloud_image_indexes = [i for i in range(len(cloud_image_paths))]
    cached_file = os.path.join(CAM.roc_folder, f"cloud({STRATA_COUNT}-{STRATA_SIZE})-{SAMPLE_POINTS}.pkl")

    ROC_DATA: Dict[str, List[List[List[ChannelBound]]]] = None

    if os.path.exists(cached_file) and overwrite is False:
        debug("\n> ROC cache file found.")
        ROC_DATA = unpickle_file(cached_file)
        debug("\n> ROC cache could not be loaded.") if not ROC_DATA else debug("\n> Cached ROC data loaded successfully.")
    else:
        debug("\n> ROC cache file not found.")
    
    if not jaccard:
        jaccard = colourspace_similarity_test(CAM, [Colour_Tag.HSV, Colour_Tag.YCRCB, Colour_Tag.RGB], overwrite=False)

    if ROC_DATA: return _average_scoredict(ROC_DATA)


    ROC_DATA = {key: [] for key, _ in jaccard.items()}
    # Partition the ground-truth image indexes into strata.
    cloud_strata = _bootstrap_indexes(cloud_image_indexes, stratum_size=STRATA_SIZE, n_bootstraps=STRATA_COUNT)

    # Load the images and their masks.
    IMAGE_MASKS = np.array([cv2.cvtColor(cv2.imread(os.path.join(CAM.cloud_masks_folder, _bmpize(p))), cv2.COLOR_BGR2GRAY) for p in cloud_image_paths], dtype=np.uint8)
    REFERENCE_IMAGES = np.array([cv2.imread(os.path.join(CAM.reference_images_folder, p)) for p in cloud_image_paths], dtype=np.uint8)

    with ProcessPoolExecutor() as pool:
        
        jobs:List[Future] = []
        
        for key, value in jaccard.items():
            keyparts = key.split("-")
            ch_label = keyparts[1]

            tag = Colour_Tag.match(keyparts[0])
            if tag is Colour_Tag.UNKNOWN: continue

            debug(f"\n\nCurrent Channel: {ch_label}")

            # Generate the boundaries to test for the given channel.
            cloud_bound_perms = _generate_permutations(max_count=SAMPLE_POINTS)
            debug(f"Points: {len(cloud_bound_perms)}")

            CH_REFERENCES = np.array([cv2.cvtColor(img, tag.value['converter']) for img in REFERENCE_IMAGES], dtype = np.uint8)

            #ROC_DATA[key] =_runstrata(value['index'], ch_label, cloud_strata, cloud_bound_perms, IMAGE_MASKS, CH_REFERENCES)
            jobs.append(pool.submit(_runstrata, value['index'], ch_label, cloud_strata, cloud_bound_perms, IMAGE_MASKS, CH_REFERENCES))
            
        
        for j, (key, value) in zip(jobs, jaccard.items()):
            ROC_DATA[key] = j.result()
    
    pickle_file(cached_file, ROC_DATA)
    return _average_scoredict(ROC_DATA)

if __name__ == "__main__":
    CAM = camera_model.DSLR

    start = datetime.now()
    averaged = ROC(cam = CAM, STRATA_COUNT = 30, STRATA_SIZE = 30, SAMPLE_POINTS =None)
    optimal = _select_optimal_bounds(Camera(CAM), averaged)
    
    debug(f"\n> Analysis finished in {datetime.now()-start}")
    debug("\n> Graphing ROC")
    
    _optimaldict_vis(CAM, optimal)
    graph_ROC(CAM = CAM, averaged=averaged, STRATA_COUNT=60, STRATA_SIZE=30)
    
    end = datetime.now()
    runtime = end-start
    debug(f'\n> Finished in : {runtime} \n')
