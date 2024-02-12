from config import *
import glob
import pickle
import toml

"""
Code from:
https://github.com/jeongwhanchoi/find-chessboard-corners/blob/master/calibrating_a_camera.ipynb

calibrateCamera() outputs a number of points
   - return value
   - camera matrix
   - distant coefficients
   - r-vectors
   - t-vectors
"""

def __load_pkl_resource(folder:str, name:str) -> Mat:
    """
    Attempt to load pickled resource <name> from <folder>.
    """
    with open(f"{folder}/{name}", "rb" ) as file:
        out = pickle.load(file)
    return out

def __load_matrix(name:str) -> Mat:
    """
    Load  camera matrix from folder of matrices.
    """
    return __load_pkl_resource(camera_matrices, name)

def __load_dist(name: str) -> Mat:
    """
    Load distance coefficients from folder of coefficients.
    """
    return __load_pkl_resource(camera_distance_coefficients, name)

def __load_config(file_path: str) -> dict | None:
    """
    Attempt to load the calibration config
    """
    toml_data = None
    try:
        with open(file_path, 'r') as file:
            toml_data = toml.load(file)
            if not toml_data: return None
    except FileNotFoundError:
        debug(f"Error: File '{file_path}' not found.")
        return None
    except toml.TomlDecodeError as e:
        debug(f"Error decoding TOML file: {e}")
        return None

    board_config = toml_data.get('CHESSBOARD', {})
    frame_config = toml_data.get('FRAME', {})

    return {'chessboard' : {
                            'vertical' : board_config.get('vertical'),
                            'horizontal' : board_config.get('horizontal'),
                            'sqmm' : board_config.get('sqmm')
                            },
            'frame' : {
                            'vertical' : frame_config.get('vertical'),
                            'width' : frame_config.get('width')
                            }
            }


def calibrate() -> None:
    pass
