import os
from glob import glob
from typing import Callable

import cv2
import numpy as np

def load_data(base, ext = "png", maximum = 1e9):
    ret = list()
    for i, file in enumerate(glob(os.path.join(base, "*." + ext))):
        if i > maximum: break
        img = cv2.imread(file)
        if len(img.shape) != 2:
            img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        ret.append(img)
    return np.array(ret)

def count_area(img) -> int:
    contours, _  = cv2.findContours(255 - img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    return len(contours)

def augment_area(img) -> int:
    contours, _ = cv2.findContours(255 - img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    max_contour = max(contours, key = lambda x: cv2.contourArea(x))
    return cv2.contourArea(max_contour)

class AdaptiveThresholdEstimiter:
    def __init__(self, evaluate = count_area, direction = 'minimize'):
        assert isinstance(evaluate, Callable), "1st argument 'evaluate' must be Callable"
        self.evaluate = evaluate
        self.direction = direction

        self.method_name = {
            "ADAPTIVE_THRESH_MEAN_C": cv2.ADAPTIVE_THRESH_MEAN_C,
            "ADAPTIVE_THRESH_GAUSSIAN_C": cv2.ADAPTIVE_THRESH_GAUSSIAN_C
        }

        self.method = "ADAPTIVE_THRESH_MEAN_C"
        self.block_size = 3
        self.C = 0

    def _predict_one(self, x):
        #return cv2.adaptiveThreshold(x, 255, eval("cv2." + self.method), cv2.THRESH_BINARY, self.block_size, self.C)
        return cv2.adaptiveThreshold(x, 255, self.method_name[self.method], cv2.THRESH_BINARY, self.block_size, self.C)
    
    def predict(self, x):
        return np.array([self._predict_one(_x) for _x in x])
    
    def fit(self, x, n_trials = 20):
        import optuna

        def bayes_objective(trial):
            self.method = trial.suggest_categorical('method', list(self.method_name.keys()))
            self.block_size = trial.suggest_categorical('block_size', [3, 5, 7, 9, 11, 13])
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