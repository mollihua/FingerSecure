import sys
# Load path to the libs folder. 
path_libs = '/Users/mochen/Desktop/Insight/FingerSecure/src'
path_libs_ext = '/Users/mochen/Desktop/Insight/FingerSecure/src_ext'
sys.path.insert(0, path_libs)
sys.path.insert(1, path_libs_ext)

import minutiae_angles as mAngle
import minutiae_mtuples as mMtuple
import minutiae_matching as mMatch

from libs.enhancing import *
from libs.basics import *
from libs.processing import *
from libs.minutiae import *



def extract_features (datatable_rc, max_owner, max_case):
    """ extract features for all owners 
    """

    dict_m_tuples_all = {}
    dict_angles_all = {}

    for owner in range(1, max_owner + 1):
        db_oneowner = datatable_rc[datatable_rc['Owner'] == owner] 

        for case in range(1, max_case + 1):
            db_oneimage = db_oneowner[db_oneowner['Case'] == case]
            x_rc = db_oneimage['x_rc'] 
            y_rc = db_oneimage['y_rc'] 

            coords_rc = list(zip(x_rc, y_rc))
            m_tuple_case = mMtuple.CalculateMTuple(coords_rc)
            m_tuple_case_result = m_tuple_case.findMTuple()

            # recovered angle
            angle_rc = list((zip(db_oneimage['angleType'], db_oneimage['angle_rc_adj']))) 

            # appending
            dict_m_tuples_all[(owner, case)] = m_tuple_case_result
            dict_angles_all[(owner, case)] = angle_rc
        
    return (dict_m_tuples_all, dict_angles_all)



def process_one_user (img_path_usr, plot=False):
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

    # plot enhanced image and end/bifurcation minutia
    if plot == True:
        plot_minutiae(img_enhanced_usr, minutiae_angle_usr_obj.get_ending_minutiae(), minutiae_angle_usr_obj.get_bifurcation_minutiae(), size=8)

    return (m_tuple_usr, minutiae_angle_usr)