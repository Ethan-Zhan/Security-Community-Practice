import tensorflow as tf
import cv2
import matplotlib

print(f"TensorFlow 版本：{tf.__version__}")
print(f"OpenCV 版本：{cv2.__version__}")
print(f"Matplotlib 版本：{matplotlib.__version__}")
# 检查 GPU 状态
gpus = tf.config.list_physical_devices('GPU')
if gpus:
    print(f" GPU 可用：{gpus}")
else:
    print(" 未检测到 GPU，将使用 CPU 训练 ")