# -*- coding: utf-8 -*-
"""
Created on Thu Apr  4 16:06:45 2024

@author: Admin
"""

class HydraulicConductivityProfile:
    def __init__(self, depth_hk_map):
        # depth_hk_map is a dictionary mapping depth ranges to Hk values
        self.depth_hk_map = depth_hk_map

    def get_hk_for_depth(self, depth):
        # Iterate over depth ranges to find where the input depth falls
        for depth_range, hk in self.depth_hk_map.items():
            if depth_range[0] <= depth < depth_range[1]:
                return hk
        # Return a default value or raise an error if depth is not in any range
        return None  # Or raise ValueError("Depth out of range.")


    def assign_hk_values(self, top, bottom, ncol):
        """
        Assign Hk values to each layer based on its depth.
        
        Parameters:
        - top: Array of top elevations for each layer
        - bottom: Array of bottom elevations for each layer
        - ncol: Number of columns (assumes uniform Hk across columns for simplicity)
        
        Returns:
        - A list of lists with Hk values for each layer.
        """
        hk_values = []
        for layer_top, layer_bottom in zip(top, bottom):
            layer_midpoint_depth = (layer_top + layer_bottom) / 2
            layer_hk = self.get_hk_for_depth(layer_midpoint_depth)
            hk_values.append([layer_hk] * ncol)
        return hk_values

