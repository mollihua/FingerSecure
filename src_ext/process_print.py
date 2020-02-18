from libs.enhancing import *
from libs.processing import *

# Load path to the libs folder. 
path_libs = '/Users/mochen/Desktop/Insight/FingerSecure/src'
path_libs_ext = '/Users/mochen/Desktop/Insight/FingerSecure/src_ext'
sys.path.insert(0, path_libs)
sys.path.insert(1, path_libs_ext)

import minutiae_angles as mAngle
import minutiae_mtuples as mMtuple


def process_one_user(img_path_usr):
	""" process a fingerprint image of one user at identification step
	"""

    # image loading
    img_usr = load_image(img_path_usr, True)

    # image enhancement
    img_enhanced_usr = enhance_image(img_usr, padding=5)

    # extract minutiae coords
    minutiae_coords_usr = process_minutiae(img_enhanced_usr)

    # calculate m-tuples
    m_tuple_usr_obj = mMtuple.CalculateMTuple(minutiae_coords_usr)
    m_tuple_usr = m_tuple_usr_obj.findMTuple()

    # extract minutiae angles
    minutiae_angle_usr_obj = mAngle.CalculateMinutiaeAngles(minutiae_coords_usr, img_enhanced_usr)
    minutiae_angle_usr = minutiae_angle_usr_obj.calculate_minutiae_angles(6)

    return (m_tuple_usr, minutiae_angle_usr)