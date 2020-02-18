# Purpose: extract minutiae info, return a datatable

# 1. extract the fingerprint ridges: remove background, binarize image, thin ridges
# 2. extract minutiae coords (x,y), i.e. at ridge endings and bifurcations.
# 3. extract minutiae angle (degree along ridge)

import sys
import numpy as np
import pickle

# Load path to the libs folder. 
path_libs = '/Users/mochen/Desktop/Insight/FingerSecure/src'
path_libs_mc = '/Users/mochen/Desktop/Insight/FingerSecure/src_ext'
sys.path.insert(0, path_libs)
sys.path.insert(1, path_libs_mc)

from libs.enhancing import *
from libs.basics import *
from libs.processing import *
from libs.minutiae import *

import minutiae_angles as mAngle
import pandas as pd
import hashlib


class createOwnersDatabase:
    """ create a database using owners' fingerprint images and PINs. 
    """

    def __init__(self, max_owner, max_case, PINs):
        self.max_owner = max_owner
        self.max_case = max_case
        self.nstep_mangle = 6
        self.PINs = PINs
        self.datatable = pd.DataFrame()
        self.datatable_final = pd.DataFrame()

        # create a dictionary: 
        str_hex = '0123456789abcdef'
        self.hex2dec = {}
        for i in range(len(str_hex)):
            hex_digit = str_hex[i]
            self.hex2dec[hex_digit] = i


    def create_minutiae_datatable(self):
        """ create a pandas datatable with minutiae info
        """

        # ---- extract true minutiae coords and angle.
        coords = []
        angles = []
        i_minutiae = np.array([])
        j_minutiae = np.array([])

        for i in range(1, self.max_owner + 1):
            print("Processing Owner %d's data... " %i)
            j_num = 0
            for j in range(1, self.max_case + 1):
                path_case = '../data/Fingerprints - Set A/10%d_%d.tif' % (i, j)

                # load image
                img = load_image(path_case, True)

                # binarize image
                img_enhanced = enhance_image(img, padding=5)

                # extract minutiae coords
                minutiae_coords = process_minutiae(img_enhanced)
                coords += minutiae_coords

                # calculate minutiae angle
                minutiae_angle_obj = mAngle.CalculateMinutiaeAngles(minutiae_coords, img_enhanced)
                minutiae_angle = minutiae_angle_obj.calculate_minutiae_angles(self.nstep_mangle)
                angles += minutiae_angle

                # number of minutiae
                j_minutiae = np.concatenate([j_minutiae, j*np.ones(len(minutiae_angle))])
                j_num += len(minutiae_angle)

            i_minutiae = np.concatenate([i_minutiae, i*np.ones(j_num)])

        self.datatable['Owner'] = i_minutiae
        self.datatable['Case'] = j_minutiae
        self.datatable['coords'] = coords
        self.datatable['angle_info'] = angles
        self.datatable['x'], self.datatable['y'] = self.datatable.coords.str
        self.datatable['angleType'], self.datatable['angle'] =self. datatable.angle_info.str
        self.datatable['Owner'] = self.datatable['Owner'].astype(int)
        self.datatable['Case'] = self.datatable['Case'].astype(int)
        self.datatable['x'] = self.datatable['x'].astype(int)
        self.datatable['y'] = self.datatable['y'].astype(int)
        self.datatable['angle'] = self.datatable['angle'].astype(float)            


        # ---- change minutiae info, given owner PINs
        # add zone column
        zones = {}
        for i in range(1, 9):
            zones[i] = np.tan(90/8*i*np.pi/180)

        self.datatable['y_over_x'] = self.datatable.y/self.datatable.x

        self.datatable['zone'] = (self.datatable['y_over_x'] > zones[1]).astype(int) + \
                                   (self.datatable['y_over_x'] > zones[2]).astype(int) + \
                                   (self.datatable['y_over_x'] > zones[3]).astype(int) + \
                                   (self.datatable['y_over_x'] > zones[4]).astype(int) + \
                                   (self.datatable['y_over_x'] > zones[5]).astype(int) + \
                                   (self.datatable['y_over_x'] > zones[6]).astype(int) + \
                                   (self.datatable['y_over_x'] > zones[7]).astype(int) + \
                                   (self.datatable['y_over_x'] > zones[8]).astype(int)


        # add alteration values for each owner
        alt_column = []
        for i in range(self.max_owner):
            owner_id = i + 1

            PIN_i = self.PINs[i]
            hash_object_i = hashlib.sha256(b'%d' % PIN_i)
            hash_value_i = hash_object_i.hexdigest()

            dict_zone_alt = {}
            s = 0
            while s < len(hash_value_i)/8: 
                dx_hex, dy_hex, da_hex = hash_value_i[s*8], hash_value_i[s*8+1], hash_value_i[s*8+2]
                dict_zone_alt[s] = (self.hex2dec[dx_hex], self.hex2dec[dy_hex], self.hex2dec[da_hex])
                s += 1

            # create partial "alter" column for owner i+1
            datatable_owner_zone = self.datatable[self.datatable.Owner == owner_id]
            datatable_owner_zone['alt'] = datatable_owner_zone['zone'].map(dict_zone_alt)
            alt_column += datatable_owner_zone['alt'].tolist()

        self.datatable['alter'] = alt_column

        # wrote altered coords and angles
        self.datatable[['dx', 'dy', 'da']] = pd.DataFrame(self.datatable['alter'].tolist(), index=self.datatable.index)
        self.datatable['x_alt'] = self.datatable['x'] + 3 * self.datatable['dx']
        self.datatable['y_alt'] = self.datatable['y'] + 3 * self.datatable['dy']
        self.datatable['a_alt'] = self.datatable['angle'] + 10 * self.datatable['da']

        # make sure recovered angle is in (-180, 180]
        self.datatable['angle_alt'] = self.datatable['a_alt'] \
                                    - (self.datatable['a_alt']//360) * 360 * (self.datatable['a_alt']>180) \
                                    - (self.datatable['a_alt']//360) * 360 * (self.datatable['a_alt']<= -180)

        self.datatable['angle_alt'] -= 360*(self.datatable['angle_alt'] > 180)
        self.datatable['angle_alt'] += 360*(self.datatable['angle_alt']<= -180)

        # create final datatalbe with true data hidden
        self.datatable_final = self.datatable.loc[:,['Owner', 'Case', 'x_alt', 'y_alt', 'angleType', 'angle_alt', 'zone']]



    def save_datatable(self, db_name, db_name_final):
        """ save datatable in binary formatx
        """
        with open(db_name, 'wb') as f:
            pickle.dump(self.datatable, f)

        with open(db_name_final, 'wb') as f2:
            pickle.dump(self.datatable_final, f2)















