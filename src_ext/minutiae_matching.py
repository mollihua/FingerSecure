
from scipy.spatial import distance
import numpy as np


def minutiae_matching(dict_m_tuples, dict_angles, m_tuple_usr, m_angle_usr, verbose=True): 
    # 
    tolr_m_tuple = 0.5 
    tolr_m_angle = 15

    owner_id_max = 9
    img_id_max = 8

    output_str = 'Not Identified'

    owner_id = 1
    while owner_id <= owner_id_max:

        img_id = 1
        count_common_points_list= []

        while img_id <= img_id_max:

            # m-tuple comparison
            m_tuple_case_i = dict_m_tuples[(owner_id, img_id)]
            matching_i = distance.cdist(m_tuple_case_i, m_tuple_usr, 'euclidean')

            binary_mask = matching_i < tolr_m_tuple
            value_mask = np.array([(matching_i[i] == matching_i[i].min()) for i in range(matching_i.shape[0])])

            mask = np.multiply(binary_mask, value_mask)
            num_similar_points = np.count_nonzero(mask)
            
            similar_points_i, similar_points_usr = np.where(mask == True)

            # minutiae angle comparison 
            count_common_points = 0

            if len(similar_points_i) != 0 and len(similar_points_usr) != 0:

                m_angle_case_i = dict_angles[((owner_id, img_id))]

                ma_i = [m_angle_case_i[i][1] for i in similar_points_i]
                ma_usr = [m_angle_usr[j][1] for j in similar_points_usr]
                ma_delta_i_usr = np.array(ma_i) - np.array(ma_usr)

                for t in range(len(ma_delta_i_usr)):
                    id_i = similar_points_i[t]
                    id_usr = similar_points_usr[t]

                    if ((abs(ma_delta_i_usr[t]) < tolr_m_angle) or \
                        (abs(ma_delta_i_usr[t]) > 360 - tolr_m_angle))\
                        and (m_angle_case_i[id_i][0] == m_angle_usr[id_usr][0]):
                        count_common_points += 1

            count_common_points_list.append(count_common_points)


            img_id += 1

        if verbose == True:
            print ("The person and owner %d have " % owner_id, end='')
            print (count_common_points_list, end = '')
            print (" in common.")

        counts_good = len(np.where(np.array(count_common_points_list) >=3)[0])

        # print(counts_good)
        if counts_good >=2:
            output_str = "Identied - owner %d!" % owner_id

        owner_id += 1


    return  output_str

