import tensorflow as tf
from tensorflow.keras.datasets import mnist
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv2D, MaxPooling2D, Flatten, Dense, Dropout
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
from sklearn.metrics import confusion_matrix, classification_report

#配置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'Arial Unicode MS']
plt.rcParams['axes.unicode_minus'] = False

print("=" * 50)
print("实验一：基于神经网络的图像分类")
print("=" * 50)

#加载与预处理
print("\n加载并预处理数据...")

#加载数据
(train_images, train_labels), (test_images, test_labels) = mnist.load_data()

print(f"原始训练集形状: {train_images.shape}")

print(f"原始测试集形状: {test_images.shape}")

#数据预处理
#把像素值缩放到 [0, 1]
train_images = train_images.astype('float32') / 255.0
test_images = test_images.astype('float32') / 255.0

# 维度扩展后维度从 (28, 28) 变为 (28, 28, 1)
train_images = train_images.reshape((60000, 28, 28, 1))
test_images = test_images.reshape((10000, 28, 28, 1))
print(f"预处理后训练集形状: {train_images.shape}")
print(f"预处理后测试集形状: {test_images.shape}")

# 把一部分的训练样本可视化
plt.figure(figsize=(10, 4))
for i in range(10):
    plt.subplot(2, 5, i + 1)
    plt.imshow(train_images[i].reshape(28, 28), cmap='gray')
    plt.title(f'标签: {train_labels[i]}')
    plt.axis('off')
plt.tight_layout()
plt.show()

#开始CNN模型搭建
print("\n构建CNN模型...")

model = Sequential([
    # 第一层卷积
    Conv2D(32,
           (3, 3),
           activation='relu',
           input_shape=(28, 28, 1)),
    MaxPooling2D((2, 2)),

    # 第二层卷积
    Conv2D(64, (3, 3), activation='relu'),
    MaxPooling2D((2, 2)),

    Flatten(),


    Dense(64, activation='relu'),

    # 添加Dropout层防止过拟合
    Dropout(0.5),

    Dense(10, activation='softmax')
])

# 显示模型结构
print("\n模型结构：")
model.summary()

# 编译模型
model.compile(
    optimizer='adam',
    loss='sparse_categorical_crossentropy',
    metrics=['accuracy']
)

print("模型编译完成")

#模型训练
print("\n开始训练模型...")

#跑10个epoch
history = model.fit(
    train_images,
    train_labels,
    epochs=10,
    batch_size=128,
    validation_split=0.2,
    verbose=1)

#画图分析
#训练曲线（折线图）
print("\n绘制训练曲线...")

plt.figure(figsize=(12, 4))

#准确率曲线
plt.subplot(1, 2, 1)
plt.plot(history.history['accuracy'], label='训练准确率', linewidth=2)
plt.plot(history.history['val_accuracy'], label='验证准确率', linewidth=2)
plt.title('模型准确率', fontsize=14)
plt.xlabel('Epoch', fontsize=12)
plt.ylabel('Accuracy', fontsize=12)
plt.legend()
plt.grid(True, alpha=0.3)

# 损失曲线
plt.subplot(1, 2, 2)
plt.plot(history.history['loss'], label='训练损失', linewidth=2)
plt.plot(history.history['val_loss'], label='验证损失', linewidth=2)

plt.title('模型损失', fontsize=14)
plt.xlabel('Epoch', fontsize=12)
plt.ylabel('Loss', fontsize=12)
plt.legend()
plt.grid(True, alpha=0.3)

plt.tight_layout()
plt.show()

#性能评估
print("\n评估模型性能...")

#测试集评估
test_loss, test_acc = model.evaluate(test_images, test_labels, verbose=0)
print(f"测试集准确率: {test_acc:.4f} ({test_acc * 100:.2f}%)")

#获取预测结果
predictions = model.predict(test_images)
predicted_labels = np.argmax(predictions, axis=1)

#绘制混淆矩阵
print("\n绘制混淆矩阵...")

plt.figure(figsize=(10, 8))
cm = confusion_matrix(test_labels, predicted_labels)
sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', xticklabels=range(10), yticklabels=range(10))
plt.title('混淆矩阵', fontsize=14)
plt.ylabel('真实标签', fontsize=12)
plt.xlabel('预测标签', fontsize=12)
plt.show()

#分类报告
print("\n分类报告：")
print(classification_report(test_labels, predicted_labels))

#可视化部分预测结果
print("\n可视化预测样例...")

plt.figure(figsize=(12, 4))
for i in range(10):
    plt.subplot(2, 5, i + 1)
    plt.imshow(test_images[i].reshape(28, 28), cmap='gray')

    is_correct = predicted_labels[i] == test_labels[i]
    color = 'green' if is_correct else 'red'

    plt.title(f'预测:{predicted_labels[i]}\n真实:{test_labels[i]}',color=color, fontsize=9)
    plt.axis('off')

plt.tight_layout()
plt.show()

#可视化错误分类的样本
errors = predicted_labels != test_labels
error_indices = np.where(errors)[0]

if len(error_indices) > 0:
    print(f"\n发现 {len(error_indices)} 个错误分类样本，展示前10个：")

    plt.figure(figsize=(12, 4))
    for i, idx in enumerate(error_indices[:10]):
        plt.subplot(2, 5, i + 1)
        plt.imshow(test_images[idx].reshape(28, 28), cmap='gray')
        plt.title(f'预测:{predicted_labels[idx]}\n真实:{test_labels[idx]}',color='red', fontsize=9)
        plt.axis('off')

    plt.tight_layout()
    plt.show()


print("\n实验完成")