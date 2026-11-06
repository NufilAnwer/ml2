import platform
import sys
import tensorflow as tf
import numpy as np
import pandas as pd
import sklearn
import mlflow
import PIL

print('Python:', sys.version)
print('Platform:', platform.platform())
print('TensorFlow:', tf.__version__)
print('NumPy:', np.__version__)
print('Pandas:', pd.__version__)
print('scikit-learn:', sklearn.__version__)
print('MLflow:', mlflow.__version__)
print('Pillow:', PIL.__version__)
print('TensorFlow GPUs:', tf.config.list_physical_devices('GPU'))
