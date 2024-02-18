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

def __load_config() -> dict:
    """
    Attempt to load the calibration config
    """
    return load_toml(calibration_config)


def __calibrate() -> None:
    """
    Calculate camera matrix data via calibration with chessboard images.
    Return camera matrix data.
    """
    confdict:dict = __load_config(calibration_config)
    board_conf = confdict["chessboard"]
    frame_conf = confdict["frame"]
    chessboard = (board_conf["vertical"], board_conf["horizontal"])
    frame = (frame_conf["width"], frame_conf["height"])


    # termination criteria
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)

    # prepare object points, like (0,0,0), (1,0,0), (2,0,0) ....,(6,5,0)56v 
    objp = np.zeros((chessboard[0] * chessboard[1], 3), np.float32)
    objp[:,:2] = np.mgrid[0:chessboard[0],0:chessboard[1]].T.reshape(-1,2)

    size_of_chessboard_squares_mm = board_conf["sqmm"]
    objp = objp * size_of_chessboard_squares_mm

    # Arrays to store object points and image points from all the images.
    objpoints:List[Mat] = [] # 3d point in real world space
    imgpoints = [] # 2d points in image plane.
    
    images = glob.glob(f'{calibration_images}/*.jpg')

    for image in images:

        img = cv2.imread(image)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # Find the chess board corners
        ret, corners = cv2.findChessboardCorners(gray, chessboard, None)

        # If found, add object points, image points (after refining them)
        if ret == True:
            objpoints.append(objp)
            corners2 = cv2.cornerSubPix(gray, corners, (11,11), (-1,-1), criteria)
            imgpoints.append(corners)
    
    ret, cameraMatrix, dist, rvecs, tvecs = cv2.calibrateCamera(objpoints, imgpoints, frame, None, None)

    return (cameraMatrix, dist, rvecs, tvecs)


def __write_calibration_data(cameraMatrix, dist, rvecs = None, tvecs = None):
    """
    Write camera calibration data to toml file.
    """
    data = {'matrix': np.asarray(cameraMatrix).tolist(),
            'distCoeff': np.asarray(dist).tolist()}

    __write_toml(f"{camera_matrices}/{camera}.toml")


def undistort(cameraMatrix, dist, rvecs = None, tvecs = None):
    