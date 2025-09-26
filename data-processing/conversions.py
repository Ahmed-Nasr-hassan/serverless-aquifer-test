class ParametersConversions:
    _theta = 2 * 3.14    # constant
    _distance = []          # distances from the origin
    _columns_widths = []     # column widths
    _layers_heights = []     # layer heights

    # original parameters
    _original_hk = 0
    _original_sy = 0
    _original_ss = 0

    # converted parameters
    _converted_hk = []
    _converted_sy = []
    _converted_ss = []

    # constructor for setting the distances and grid
    def __init__(self, distance, columnsWidths, layersHeights):
        self._distance = distance
        self._columns_widths = columnsWidths
        self._layers_heights = layersHeights
        self._original_hk = []


    # setters for all the original parameters
    def set_original_parameters(self, hk, sy, ss):
        self._original_hk = hk
        self._original_sy = sy
        self._original_ss = ss

    # setters for each original parameter
    def set_original_hk(self, hk):
        self._original_hk = hk

    def set_original_sy(self, sy):
        self._original_sy = sy

    def set_original_s(self, ss):
        self._original_ss = ss

    # getters for all the original parameters
    def get_original_parameters(self):
        return self._original_hk, self._original_sy, self._original_ss


    # setters for all the converted parameters
    def set_converted_parameters(self, hk, sy, ss):
        self._converted_hk = hk
        self._converted_sy = sy
        self._converted_ss = ss

    # setters for each converted parameter
    def set_converted_hk(self, hk):
        self._converted_hk = hk

    def set_converted_sy(self, sy):
        self._converted_sy = sy

    def set_converted_ss(self, ss):
        self._converted_ss = ss

    # getters for all the converted parameters
    def get_converted_parameters(self):
        return self._converted_hk, self._converted_sy, self._converted_ss


    # Calculate the converted value for one cell
    def _calculate_converted_value_for_one_cell(self, original_value, distance):
        return original_value * self._theta * distance
    
    # calculate areas of the grid
    def calculate_areas_of_the_grid(self):
        areas = [
            [self._layers_heights[layer] * self._columns_widths[column] 
            for column in range(len(self._columns_widths))]
            for layer in range(len(self._layers_heights))
        ]
        return areas

    # # Calculate each converted parameter
    # def calculate_converted_hk(self):
    #     return [self._calculate_converted_value_for_one_cell(self._original_hk, distance) for distance in self._distance]
    def calculate_converted_hk(self):
        converted_hk = []  # Initialize an empty list to hold the converted hk values for all layers
        for hk_value in self._original_hk:  # Iterate over each vertical hk value
            # For each hk value, calculate the converted value for each distance
            layer_converted_hk = [self._calculate_converted_value_for_one_cell(hk_value, distance) for distance in self._distance]
            converted_hk.append(layer_converted_hk)  # Append the list of converted values for this layer to the main list
        return converted_hk



    def calculate_converted_sy(self):
        return [self._calculate_converted_value_for_one_cell(self._original_sy, distance) for distance in self._distance]
    
    def calculate_converted_ss(self):
        distances = [self._distance for _ in self._layers_heights]
        areas = self.calculate_areas_of_the_grid()
        converted_ss=[]
        for row in range(len(distances)):
            sss = []
            for column in range(len(distances[row])):
                sss.append(self._original_ss * distances[row][column] * self._theta * areas[row][column])
            converted_ss.append(sss)
        return converted_ss
    
    def calculate_converted_parameters(self):
        return self.calculate_converted_hk(), self.calculate_converted_sy(), self.calculate_converted_ss()
    
    # calculate each original parameter
    def calculate_original_hk(self):
        return self._converted_hk[0] / (self._theta * self._distance[0])
    
    def calculate_original_sy(self):
        return self._converted_sy[0] / (self._theta * self._distance[0])
    
    def calculate_original_ss(self):
        area = self._columns_widths[0] * self._layers_heights[0]
        return self._converted_ss[0][0] / (self._distance[0] * area * self._theta)
    
    def calculate_original_parameters(self):
        return self.calculate_original_hk(), self.calculate_original_sy(), self.calculate_original_ss()
    