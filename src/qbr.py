#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# vim: fenc=utf-8 ts=4 sw=4 et

import sys
import kociemba
import argparse
from video import webcam
# import i18n  # Removed i18n dependency
import os
from config import config
from constants import (
    ROOT_DIR,
    E_INCORRECTLY_SCANNED,
    E_ALREADY_SOLVED
)

# Set default locale.
locale = config.get_setting('locale')
if not locale:
    config.set_setting('locale', 'en')
    locale = config.get_setting('locale')

# i18n initialization removed - using hardcoded English strings

class Qbr:

    def __init__(self, normalize):
        self.normalize = normalize

    def run(self):
        """The main function that will run the Qbr program."""
        print("=== QBR Rubik's Cube Solver ===")
        print("Instructions:")
        print("1. Hold your cube so one face is clearly visible to the camera")
        print("2. Make sure the face is well-lit and all 9 stickers are visible")
        print("3. Press SPACE to capture the current face")
        print("4. Repeat for all 6 faces (white, red, green, yellow, orange, blue)")
        print("5. If colors are not detected correctly, press 'c' to enter calibration mode")
        print("6. Press 'r' to start/stop recording your solve (optional)")
        print("7. Press ESC to exit")
        print("")
        print("IMPORTANT: If you get a color validation error, use calibration mode!")
        print("Press 'c' to start calibration, then hold each colored face to the camera")
        print("and press SPACE to calibrate each color.")
        print("")
        print("🎥 RECORDING: Press 'r' to start recording, press 'r' again to stop.")
        print("Video will be saved as 'rubiks_cube_solve_[timestamp].mp4'")
        print("=" * 40)
        
        state = webcam.run()

        # If we receive a number then it's an error code.
        if isinstance(state, int) and state > 0:
            self.print_E_and_exit(state)

        try:
            algorithm = kociemba.solve(state)
            length = len(algorithm.split(' '))
        except Exception:
            self.print_E_and_exit(E_INCORRECTLY_SCANNED)

        print("Starting position: \nfront: green\ntop: white\n")
        print(f"Moves: {length}")
        print(f"Solution: {algorithm}")
        
        # The solving phase is now handled automatically in video.py
        # No need to ask user - it transitions automatically
        
        if self.normalize:
            print("\nDetailed solution:")
            for index, notation in enumerate(algorithm.split(' ')):
                # Simplified move descriptions
                move_descriptions = {
                    'R': 'Turn the right side a quarter turn away from you.',
                    'R\'': 'Turn the right side a quarter turn towards you.',
                    'R2': 'Turn the right side 180 degrees.',
                    'L': 'Turn the left side a quarter turn towards you.',
                    'L\'': 'Turn the left side a quarter turn away from you.',
                    'L2': 'Turn the left side 180 degrees.',
                    'U': 'Turn the top layer a quarter turn to the left.',
                    'U\'': 'Turn the top layer a quarter turn to the right.',
                    'U2': 'Turn the top layer 180 degrees.',
                    'D': 'Turn the bottom layer a quarter turn to the right.',
                    'D\'': 'Turn the bottom layer a quarter turn to the left.',
                    'D2': 'Turn the bottom layer 180 degrees.',
                    'B': 'Turn the back side a quarter turn to the left.',
                    'B\'': 'Turn the back side a quarter turn to the right.',
                    'B2': 'Turn the back side 180 degrees.',
                    'F': 'Turn the front side a quarter turn to the right.',
                    'F\'': 'Turn the front side a quarter turn to the left.',
                    'F2': 'Turn the front side 180 degrees.'
                }
                text = move_descriptions.get(notation, f'Move: {notation}')
                print('{}. {}'.format(index + 1, text))

    def print_E_and_exit(self, code):
        """Print an error message based on the code and exit the program."""
        if code == E_INCORRECTLY_SCANNED:
            print('\033[0;33m[QBR ERROR] Oops, you did not scan in all 6 sides correctly')
            print('Please try again.\033[0m')
            print("\nTroubleshooting tips:")
            print("1. Make sure all 6 faces are scanned (white, red, green, yellow, orange, blue)")
            print("2. Ensure good lighting - avoid shadows and glare")
            print("3. Hold the cube steady and make sure all 9 stickers are visible")
            print("4. Try calibration mode by pressing 'c' if colors are not detected correctly")
            print("5. Make sure your cube has standard colors (not custom stickers)")
            print("")
            print("COLOR VALIDATION FAILED: This usually means the colors aren't being detected accurately.")
            print("SOLUTION: Use calibration mode by pressing 'c' when the program starts.")
            print("Then hold each colored face to the camera and press SPACE to calibrate.")
        elif code == E_ALREADY_SOLVED:
            print('\033[0;33m[QBR ERROR] Your cube has already been solved\033[0m')
        sys.exit(code)

if __name__ == '__main__':
    # Define the application arguments.
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-n',
        '--normalize',
        default=False,
        action='store_true',
        help='Shows the solution normalized. For example "R2" would be: \
              "Turn the right side 180 degrees".'
    )
    args = parser.parse_args()

    # Run Qbr with all arguments.
    Qbr(args.normalize).run()
