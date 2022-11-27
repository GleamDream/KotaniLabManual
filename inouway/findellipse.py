from __future__ import annotations
from typing import Tuple

from matplotlib import pyplot as plt
import pandas as pd
import numpy as np
import cv2

class FindEllipse:
    """
    class FindEllipse

    This class detects ellipses from an image using the least-squares method.

    Parameters
    ----------
    src : str or numpy.ndarray
        File name for import data required csv
        or Image array
    
    Notes
    ----------
    The argument must be an image array or a filename string.
    """
    def __init__(self, src: any):
        assert (isinstance(src, np.ndarray) or isinstance(src, str)), "The argument must be an image array or a filename string."
        
        if isinstance(src, str):
            self.img = pd.read_csv(src, sep = " ", header = None, index_col = None).values.astype(np.uint8)
        
        if isinstance(src, list): 
            self.img = np.array(src, dtype = np.uit8)

        if isinstance(src, np.ndarray):
            self.img = src
            if len(src.shape) != 2:
                self.img = cv2.cvtColor(self.img, cv2.COLOR_BGR2GRAY)
            
    def find(self, th: int = 1, idx: int = -1) -> Tuple[Tuple[float, float], Tuple[float, float], float]:
        """
        Returns Ellipse Parameters
        
        Parameters
        ----------
        th : int
            Threshold for binarization, default `1`
        idx : int
            Index of contour used in find ellipse calculation, default `-1`
        
        Returns
        ----------
        center : Tuple[float, float]
            The center of ellipse position
        axis : Tuple[float, float]
            The longer axis (major axis) and the shoter axis (minor axis)
        rotation : float
            The angle of rotation (degree)
        """
        self.img[self.img < th] = 0
        self.img[self.img >= th] = 255
        self.img = self.img.astype(np.uint8)
        contours, _ = cv2.findContours(self.img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
        self.ellipse = cv2.fitEllipse(contours[idx])
        self.center = self.ellipse[0]
        self.px, self.py = self.center
        self.axis = self.ellipse[1]
        self.major_axis, self.minor_axis = self.axis
        self.rot = self.ellipse[2]
        return self.center, (self.major_axis, self.minor_axis), self.rot
    
    def draw(self, color = (0, 0, 255)) -> FindEllipse:
        image_rgb = cv2.cvtColor(self.img, cv2.COLOR_GRAY2RGB)
        cv2.ellipse(image_rgb, self.find(), color, 1)
        image_rgb[round(self.py), round(self.px)] = color
        plt.imshow(image_rgb)
        plt.title(str(self))
        plt.show()
        return self

    def __str__(self):
        return f"Center: ({round(self.px)}, {round(self.py)}), Axis: ({round(self.major_axis, 1)}, {round(self.minor_axis, 1)}), Rot: {round(self.rot, 1)}"

if __name__ == "__main__":
    res = [
        FindEllipse((np.random.rand(255, 255) * 255).astype(np.uint8)),
        FindEllipse("with_anger.csv"),
        FindEllipse("without_anger.csv"),
        
    ]
    for ellipse in res:
        ellipse.draw()
        print(ellipse)
        print(ellipse.center, ellipse.axis, ellipse.rot)