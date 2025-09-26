# -*- coding: utf-8 -*-
"""
Created on Sat Sep 30 11:29:02 2023

@author: Dell
"""

class VerticalRefinement:
    def __init__(self, top_level, bottom_level, point_1_level, point_2_level,
                 layer_thickness_1, layer_thickness_2,
                 multiplier_above_screen, multiplier_below_screen, multiplier_between_screen):
        self.top_level = top_level
        self.bottom_level = bottom_level
        self.point_1_level = point_1_level
        self.point_2_level = point_2_level
        self.layer_thickness_1 = layer_thickness_1
        self.layer_thickness_2 = layer_thickness_2
        self.multiplier_above_screen = multiplier_above_screen
        self.multiplier_below_screen = multiplier_below_screen
        self.multiplier_between_screen = multiplier_between_screen


    def calculate_thicknesses(self):
        # Calculate layer thicknesses and levels here...
        layer_thicknesses_up = []
        level_upward_pt1 = [self.point_1_level]
        current_level_up = self.point_1_level
        layer_thickness_1=self.layer_thickness_1
        while current_level_up < self.top_level:
            layer_thickness_1 *= self.multiplier_above_screen
            layer_thicknesses_up.append(layer_thickness_1)
            level_upward_pt1.append(current_level_up)
            current_level_up += layer_thickness_1
        layer_thicknesses_up.sort(reverse=True)
        level_upward_pt1.pop(0)
        level_upward_pt1.pop(0)
        level_upward_pt1.reverse()
        level_upward_pt1.pop(0)
        level_upward_pt1.insert(0, self.top_level)
        

        layer_thicknesses_down = []
        level_downward_pt2 = [self.point_2_level]
        current_level_down = self.point_2_level
        while current_level_down > self.bottom_level + self.layer_thickness_2:
            self.layer_thickness_2 *= self.multiplier_below_screen
            layer_thicknesses_down.append(self.layer_thickness_2)
            level_downward_pt2.append(current_level_down)
            current_level_down -= self.layer_thickness_2
        level_downward_pt2.pop(0)

        screen_thickness = []
        level_sc_top = [self.point_1_level]
        level_sc_down = [self.point_2_level]
        current_level1 = self.point_1_level
        current_level2 = self.point_2_level
        mid_point = (self.point_1_level + self.point_2_level) / 2
        while current_level1 > mid_point:
            screen_thickness.append(self.layer_thickness_1)
            current_level1 -= self.layer_thickness_1
            current_level2 += self.layer_thickness_1
            self.layer_thickness_1 *= self.multiplier_between_screen
            level_sc_top.append(current_level1)
            level_sc_down.append(current_level2)
        level_sc_down.reverse()
        level_sc_top.pop(-1)
        level_sc_down.pop(0)
        level_sc_down.pop(-1)

        # Combine the level lists
        top = level_upward_pt1 + level_sc_top + level_sc_down + level_downward_pt2
        bottom = top[1:]
        bottom.append(self.bottom_level)

        # Calculate thickness for each layer
        thickness = [t - b for t, b in zip(top, bottom)]

        return top, bottom, thickness