from __future__ import annotations
from typing import List, Dict, Callable

import os
from glob import glob

import cv2
import numpy as np

def load_data(base: str, ext: str = "png", maximum: int = 1e9) -> np.ndarray:
    ret: List[np.ndarray] = list()
    for i, file in enumerate(glob(os.path.join(base, "*." + ext))):
        if i > maximum: break
        img: np.ndarray = cv2.imread(file)
        if len(img.shape) != 2:
            img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        ret.append(img)
    return np.array(ret)

def count_area(img: np.ndarray) -> int:
    contours, _  = cv2.findContours(255 - img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    return len(contours)

def augment_area(img: np.ndarray) -> int:
    contours, _ = cv2.findContours(255 - img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    max_contour = max(contours, key = lambda x: cv2.contourArea(x))
    return cv2.contourArea(max_contour)

class AdaptiveThresholdEstimiter:
    def __init__(self, evaluate: Callable[[np.ndarray], int] = count_area, direction: str = 'minimize'):
        assert isinstance(evaluate, Callable), "argument 'evaluate' must be Callable"
        self.evaluate: Callable[[np.ndarray], int] = evaluate
        self.direction: str = direction

        self.method_name: Dict[str, int] = {
            "ADAPTIVE_THRESH_MEAN_C": cv2.ADAPTIVE_THRESH_MEAN_C,
            "ADAPTIVE_THRESH_GAUSSIAN_C": cv2.ADAPTIVE_THRESH_GAUSSIAN_C
        }

        self.method: str = "ADAPTIVE_THRESH_MEAN_C"
        self.block_size: int = 3
        self.C: int = 0

    def _predict_one(self, x: np.ndarray) -> np.ndarray:
        #return cv2.adaptiveThreshold(x, 255, eval("cv2." + self.method), cv2.THRESH_BINARY, self.block_size, self.C)
        return cv2.adaptiveThreshold(x, 255, self.method_name[self.method], cv2.THRESH_BINARY, self.block_size, self.C)
    
    def predict(self, x: np.ndarray) -> np.ndarray:
        return np.array([self._predict_one(_x) for _x in x])
    
    def fit(self, x: np.ndarray, n_trials: int = 20) -> AdaptiveThresholdEstimiter:
        import optuna

        def bayes_objective(trial) -> int:
            self.method = trial.suggest_categorical('method', list(self.method_name.keys()))
            self.block_size = trial.suggest_int('block_size', 3, 13, 2)
            self.C = trial.suggest_int('C', -10, 10)
            return np.array(list(map(self.evaluate, self.predict(x)))).sum()

        study = optuna.create_study(direction = self.direction, sampler = optuna.samplers.TPESampler(seed = 1))
        study.optimize(bayes_objective, n_trials = n_trials)
        print(f"Found best parameters: {study.best_trial.params}")
        print(f"      best score: {study.best_trial.value}")
        self.best_params_ = study.best_trial.params
        self.method = self.best_params_["method"]
        self.block_size = self.best_params_["block_size"]
        self.C = self.best_params_["C"]
        return self