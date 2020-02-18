# Calculate minutiae angles
# ending mninutia: angle is between curve direction and x-axis
# bifurcation minutia: angle is between ending curve (prior to bifurcation) direction and x-axis
import numpy as np


class CalculateMinutiaeAngles():
    """ purpose: calculate minutiae angles from minutiae coords.
        input: all minutiae coords from processing one fingerprint image;
               the preprocessed fingerprint image.
        output: all minutiae tuples, each containing x, y, and angle 
    """

    x_delta = 1
    
    def __init__(self, minutiae_data, img_enhanced):
        self.minutiae_data = minutiae_data
        self.img_enhanced = img_enhanced
        self.img_ymax = img_enhanced.shape[1]
    
    
    def calculate_minutiae_angles(self, nstep):
        """ input:
                nstep: the number of translational steps from minutiae point
            output: the list of minutiae angles
        """
        angles = []

        for eachpoint in self.minutiae_data:
            minutiae_class, neighbors = self.bifurcation_or_end(eachpoint)
            center = eachpoint

            if minutiae_class == "end":
                curve_points = self.calculate_traj(center, neighbors[0], nstep)
                angle = self.calculate_angle(curve_points)
                angles.append((minutiae_class, angle))

            elif minutiae_class == "bifurcation":
                curve_points_last = []

                for neighbor in neighbors:
                    curve_points = self.calculate_traj(center, neighbor, nstep)
                    curve_points_last.append(curve_points[-1])
                
                if len(curve_points_last) !=0:
                    last_point_curve_sel = self.pick_curve(center, curve_points_last)
                    curve_points_sel = [center,  last_point_curve_sel]
                    angle = self.calculate_angle(curve_points_sel)
                angles.append((minutiae_class, round(angle,1))) 
            
            else:
                angles.append((minutiae_class, 0))

        return angles
                
        
    def calculate_traj(self, center, neighbor, nstep):
        curve = []
        curve.append(center)
        for i in range(nstep):
            tmp = self.calculate_neighbor_xy(center, neighbor)
            center = neighbor
            neighbor = tmp
            curve.append(center)
        return curve 


    def calculate_neighbor_xy(self, first, second):
        """ purpose: find the third along first-second curve
            input: 
                first: 1st point
                second: 2nd point 
            output:
                third: 3rd point
        """
        x2, y2 = second
        
        third_sel = (0,0) # dummy
        third_list = []
        cnt_tups = []

        for i in range(x2 - 1, x2 + 2):
            for j in range(y2 - 1, y2 + 2):
                if (self.img_enhanced[i][j] == 1) and (sum(abs(np.array((i,j)) - np.array(first))) > 1) and ((i,j) != second):
                    third = (i,j)
                    
                    # count the number of neighbors in this third point
                    third_lay1 = self.img_enhanced[i-1 : i+2, j-1 : j+2]
                    cnt = np.count_nonzero(third_lay1)
                    cnt_tup = (i, j, cnt)
                    cnt_tups.append(cnt_tup)
        
        # keep the third that has the largest num of other white pixels
        if len(cnt_tups) !=0 :
            cnt_tups_sorted = sorted(cnt_tups, key=lambda elem: elem[2])
            third_sel = (cnt_tups_sorted[-1][0], cnt_tups_sorted[-1][1])
        
        return third_sel


    def pick_curve(self, center, curve_points_last): 
        """ input: 
                curve_points_last: should contain 3 coords 
            output: coords of the last point on selected curve
        """
        vectors = []
        for point in curve_points_last:
            vector = np.array(point) - np.array(center)
            vectors.append(vector)
        
        # min theta -- max cos_theta
        tups = []
        i = 0
        while i < (len(vectors) - 1):
            j = i + 1
            while j < len(vectors):
                vec1 = vectors[i]
                vec2 = vectors[j]
                cos_theta = sum(np.multiply(vec1, vec2))/(np.linalg.norm(vec1) * np.linalg.norm(vec2))
                tup = (i, j, cos_theta) 
                tups.append(tup)
                j += 1
            i += 1

        tups_sorted = sorted(tups, key= lambda elem: elem[2])
        
        if len(tups_sorted) !=0:
            (i_sel, j_sel, cos_theta_sel) = tups_sorted[-1]
            for p in range(len(curve_points_last)):
                if p==i_sel or p==j_sel:
                    pass
                else:
                    index_sel = p
        else:
            index_sel = 0
                
        return curve_points_last[index_sel]
        

    def bifurcation_or_end(self, eachpoint):
        """ search surrounding 8 pixels of a minutiae point.
            if there is 1 white pixel, it is an end point.
            if there are 3 white pixels, it is a bifurcation point.
            input: eachpoint is a tuple containing x, y.
            output: minutiae_type and the neighboring white pixels' coords.
        """
        x, y = eachpoint
        count_whitePixel = 0
        xy_neighbors = []
        for i in range(x-1, x+2):
            for j in range(y-1, y+2):
                if self.img_enhanced[i][j] == 1 and (i,j)!=eachpoint:
                    xy_neighbors.append((i, j))
                    count_whitePixel += 1
        
        if count_whitePixel == 1:
            minutiae_type = "end"
        elif count_whitePixel >= 3:
            minutiae_type = "bifurcation"
        else:
            # print ("strange: ", count_whitePixel)
            minutiae_type = "error"
        return (minutiae_type, xy_neighbors)


    def get_ending_minutiae(self):
        ending_points = []

        for eachpoint in self.minutiae_data:
            minutiae_type, _ = self.bifurcation_or_end(eachpoint)
            if minutiae_type == "end":
                ending_points.append(eachpoint)

        return ending_points


    def get_bifurcation_minutiae(self):
        bifurcation_points = []

        for eachpoint in self.minutiae_data:
            minutiae_type, _ = self.bifurcation_or_end(eachpoint)
            if minutiae_type == "bifurcation":
                bifurcation_points.append(eachpoint)

        return bifurcation_points 
    
    
    def calculate_angle(self, curvepoints):
        """ input:  
                curveurvepoints: (x,y) coords of all points on the curve
            output: 
                theta: angle in degree, range is (-180, 180]
        """
        xy_start = np.array(curvepoints[0])
        xy_end = np.array(curvepoints[-1])
        xy_delta = xy_end - xy_start
        dx, dy = xy_delta[0], xy_delta[1]

        if dx == 0:
            if dy > 0:
                theta = 90
            else:
                theta = -90
        else:
            tg_theta = dy/dx
            theta = np.arctan(tg_theta)/np.pi*180
            if dx < 0:
                if dy > 0:
                    theta += 180
                else: 
                    theta -= 180

        return theta
