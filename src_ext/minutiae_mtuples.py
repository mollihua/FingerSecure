
# Calculate M(i) - tuple for each fingerprint's minutiae
# algorithm: Ratio of Relational Distance Matching
# ref: http://pubs.sciepub.com/jcsa/1/4/1

# the m-tuple of each point contains 10 ratios and 10 cosines.

from scipy.spatial import distance
import numpy as np

class CalculateMTuple:
    
    def __init__(self, minutiae_data):
        self.minutiae_data = minutiae_data
    
    
    def findMTuple(self):
        num_minutiae = len(self.minutiae_data)
        m_tuple_list = []
        
        for i in range(num_minutiae):
            nearest5_i = self.find_nearest5(i)
            m_tuple_i = self.calculate_m_tuple(i)
            m_tuple_list.append(m_tuple_i)
            
        return m_tuple_list

    
    def find_nearest5(self, refpoint_index):
        """ 
        input:
            refpoint_index: the index of reference point.
        
        output:
            nearest5: a tuple list, with each tuple containing index and distance to reference point.
        """
        num_minutiae = len(self.minutiae_data)
        minutiae_i = [self.minutiae_data[refpoint_index]]
        distances = distance.cdist(minutiae_i, self.minutiae_data, 'euclidean')[0]
        dtuple = [(j, distances[j]) for j in range(len(distances))]
        dtuple_sorted = sorted(dtuple, key = lambda x:x[1])
        nearest5 = dtuple_sorted[1:6]
        
        return nearest5
 

    def calculate_m_tuple(self, refpoint_index):
        """
        purpose:
            calcuate m-tuple of a minutiae point
        input: 
            refpoint_index: the index of reference point
            nearest5: a list contains binary tuple - index of point, distance to reference point
        output: 
            m-tuple: contains 10 ratios of relational distance, and 5 values of cosine angles.
        note: 
            all values in output ranges from 0 to 1.
        """
        
        m_tuple = []
        nearest5 = self.find_nearest5(refpoint_index)
        
        # calculate Ratio of relational distance
        i = 0
        while i < 5:
            distance_i_to_ref = nearest5[i][1]
            j = i + 1
            while j < 5:
                distance_j_to_ref = nearest5[j][1]
                ratio_ij = distance_i_to_ref/distance_j_to_ref
                m_tuple.append(ratio_ij)
                j += 1
            i += 1
                
        # calculate angles between nearest_i -- reference point -- nearest_j   
        i = 0
        while i < 4:
            index_i = nearest5[i][0]
            distance_i_to_ref = nearest5[i][1]
            j = i + 1
            index_j = nearest5[j][0]
            distance_j_to_ref = nearest5[j][1]
            costheta_ij_to_ref = self.calculate_costheta(refpoint_index, index_i, distance_i_to_ref, index_j, distance_j_to_ref)
            m_tuple.append(costheta_ij_to_ref)
            i += 1

        index_i = nearest5[4][0]
        distance_i_to_ref = nearest5[i][1]
        index_j = nearest5[0][0]
        distance_j_to_ref = nearest5[j][1]
        costheta_ij_to_ref = self.calculate_costheta(refpoint_index, index_i, distance_i_to_ref, index_j, distance_j_to_ref)
        m_tuple.append(costheta_ij_to_ref)        
        
        #print(len(m_tuple))
        return tuple(m_tuple)
        
    
    def calculate_costheta(self, refpoint_index, index_i, distance_i_to_ref, index_j, distance_j_to_ref):
        coords_ref = self.minutiae_data[refpoint_index]
        coords_i = self.minutiae_data[index_i]
        coords_j = self.minutiae_data[index_j]
        
        vec_i_ref = np.subtract(coords_i, coords_ref)
        vec_j_ref = np.subtract(coords_j, coords_ref)
        iref_dot_jref = vec_i_ref[0]*vec_j_ref[0] + vec_i_ref[1]*vec_j_ref[1]
        
        cos_theta = iref_dot_jref/(distance_i_to_ref*distance_j_to_ref)
        return cos_theta
        