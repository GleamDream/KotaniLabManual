import os
import numpy as np
from matplotlib import pyplot as plt

from estimiter import AdaptiveThresholdEstimiter, load_data, count_area, augment_area

def augment_area2(img) -> int:
    return (img.shape[0] * img.shape[1]) - np.count_nonzero(img)

if __name__ == "__main__":
    img = load_data(os.path.join(os.environ["image_dir"]))
    
    #ate = AdaptiveThresholdEstimiter(area_count, 'minimize')
    #ate = AdaptiveThresholdEstimiter(augment_area, 'maximize')
    ate = AdaptiveThresholdEstimiter(augment_area2, 'maximize')
    ate.fit(img, n_trials = 50)
    
    for i, x in enumerate(img):
        fig, (ax1, ax2) = plt.subplots(nrows = 1, ncols = 2, figsize = (8, 4))
        ax1.imshow(x, cmap = 'gray', vmin = 0, vmax = 255)
        ax2.imshow(ate._predict_one(x), cmap = 'gray', vmin = 0, vmax = 255)
        plt.show()
        plt.close()
        if i > 5:
            break