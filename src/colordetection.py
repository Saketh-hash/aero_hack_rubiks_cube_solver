#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# vim: fenc=utf-8 ts=4 sw=4 et

import numpy as np
import cv2
from helpers import ciede2000, bgr2lab
from config import config
from constants import CUBE_PALETTE, COLOR_PLACEHOLDER

class ColorDetection:

    def __init__(self):
        self.prominent_color_palette = {
            'red': (0, 0, 255),
            'orange': (0, 165, 255),
            'blue': (255, 0, 0),
            'green': (0, 255, 0),
            'white': (255, 255, 255),
            'yellow': (0, 255, 255)
        }

        # Load colors from config and convert the list -> tuple.
        self.cube_color_palette = config.get_setting(
            CUBE_PALETTE,
            self.prominent_color_palette
        )
        for side, bgr in self.cube_color_palette.items():
            self.cube_color_palette[side] = tuple(bgr)

    def get_prominent_color(self, bgr):
        """Return the prominent display color for the exact BGR color."""
        for color_name, color_bgr in self.cube_color_palette.items():
            if tuple([int(c) for c in bgr]) == color_bgr:
                return self.prominent_color_palette[color_name]
        return COLOR_PLACEHOLDER

    def get_dominant_color(self, roi):
        """
        Get dominant BGR color from a given region (roi) using k-means clustering.

        :param roi: The region of interest as a numpy array.
        :returns: tuple - Dominant color in BGR format
        """
        try:
            # Check if ROI is valid
            if roi is None or roi.size == 0:
                return COLOR_PLACEHOLDER
                
            pixels = np.float32(roi.reshape(-1, 3))
            n_colors = 1
            criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 200, 0.1)
            flags = cv2.KMEANS_RANDOM_CENTERS

            _, labels, palette = cv2.kmeans(pixels, n_colors, None, criteria, 10, flags)
            _, counts = np.unique(labels, return_counts=True)
            dominant = palette[np.argmax(counts)]
            return tuple(map(int, dominant))
        except Exception as e:
            print(f"Dominant color detection error: {e}")
            return COLOR_PLACEHOLDER

    def get_closest_color(self, bgr):
        """
        Get the closest cube color using the CIEDE2000 distance in LAB color space.

        :param bgr: tuple - input BGR color
        :returns: dict - { color_name, color_bgr, distance }
        """
        try:
            lab = bgr2lab(bgr)
            distances = []
            for color_name, color_bgr in self.cube_color_palette.items():
                distance = ciede2000(lab, bgr2lab(color_bgr))
                distances.append({
                    'color_name': color_name,
                    'color_bgr': color_bgr,
                    'distance': distance
                })
            closest = min(distances, key=lambda x: x['distance'])
            return closest
        except Exception as e:
            # Fallback to a default color if color detection fails
            print(f"Color detection error: {e}")
            return {
                'color_name': 'white',
                'color_bgr': (255, 255, 255),
                'distance': float('inf')
            }

    def convert_bgr_to_notation(self, bgr):
        """
        Convert a BGR color to Rubik's cube face notation.

        :param bgr: tuple - BGR color
        :returns: str - one of 'F', 'U', 'B', 'R', 'L', 'D'
        """
        try:
            notation_map = {
                'green': 'F',
                'white': 'U',
                'blue': 'B',
                'red': 'R',
                'orange': 'L',
                'yellow': 'D'
            }
            closest_color = self.get_closest_color(bgr)['color_name']
            return notation_map.get(closest_color, 'F')  # Default to 'F' if color not found
        except Exception as e:
            print(f"Color conversion error: {e}")
            return 'F'  # Default fallback

    def set_cube_color_pallete(self, palette):
        """
        Manually set cube color palette.

        :param palette: dict with color_name: BGR tuple
        """
        for side, bgr in palette.items():
            self.cube_color_palette[side] = tuple(map(int, bgr))

# Singleton instance for use across project
color_detector = ColorDetection()