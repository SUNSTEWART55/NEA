import cv2
import numpy as np
import os
from tensorflow.keras.datasets import mnist
 
def load_digit_data():
    (train_images, train_labels), (test_images, test_labels) = mnist.load_data()
 
    train_images = train_images.reshape(train_images.shape[0], 784).T / 255.0
    test_images = test_images.reshape(test_images.shape[0], 784).T / 255.0
 
    return train_images, train_labels, test_images, test_labels
 
def invert(image):
    if image[0][0] > 127:
        image = 255 - image
    return image
 
 
def center_and_resize(image, output_size=28, margin=4):
    coords = np.column_stack(np.where(image > 30))
    if coords.size == 0:
        return np.zeros((output_size, output_size), dtype=np.uint8)
 
    y_min, x_min = coords.min(axis=0)
    y_max, x_max = coords.max(axis=0)
    cropped = image[y_min:y_max + 1, x_min:x_max + 1]
 
    target_size = output_size - margin
    h, w = cropped.shape
    scale = target_size / max(h, w)
    new_h, new_w = max(1, int(h * scale)), max(1, int(w * scale))
    resized = cv2.resize(cropped, (new_w, new_h), interpolation=cv2.INTER_AREA)
 
    canvas = np.zeros((output_size, output_size), dtype=np.uint8)
    y_offset = (output_size - new_h) // 2
    x_offset = (output_size - new_w) // 2
    canvas[y_offset:y_offset + new_h, x_offset:x_offset + new_w] = resized
    return canvas
 
 
def preprocess_image_file(path):
    img = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
    if img is None:
        return None
    img = invert(img)
    img = center_and_resize(img)
    return img
 
def load_class_folder(folder_path, label, save_converted_to=None):
    images = []
    labels = []
 
    if not os.path.isdir(folder_path):
        return np.empty((0, 28, 28), dtype=np.uint8), np.empty((0,), dtype=np.int64)
 
    if save_converted_to:
        os.makedirs(save_converted_to, exist_ok=True)
 
    for filename in os.listdir(folder_path):
        if not filename.lower().endswith((".png", ".jpg", ".jpeg")):
            continue
 
        full_path = os.path.join(folder_path, filename)
        converted = preprocess_image_file(full_path)
        if converted is None:
            continue
 
        images.append(converted)
        labels.append(label)
 
        if save_converted_to:
            out_name = os.path.splitext(filename)[0] + ".png"
            cv2.imwrite(os.path.join(save_converted_to, out_name), converted)
 
    return np.array(images), np.array(labels)
 
 
def load_dataset_from_class_folders(root_dir, class_to_label, save_converted_to=None):
    def load_split(split_name):
        all_images, all_labels = [], []
        for classname, label in class_to_label.items():
            folder = os.path.join(root_dir, split_name, classname)
            out_dir = None
            if save_converted_to:
                out_dir = os.path.join(save_converted_to, split_name, classname)
            images, labels = load_class_folder(folder, label, save_converted_to=out_dir)
            if len(images) == 0:
                continue
            all_images.append(images)
            all_labels.append(labels)
 
        if not all_images:
            return np.empty((784, 0)), np.empty((0,), dtype=np.int64)
 
        images = np.concatenate(all_images)
        labels = np.concatenate(all_labels)
        images = images.reshape(images.shape[0], 784).T / 255.0
        return images, labels
 
    train_images, train_labels = load_split("train")
    test_images, test_labels = load_split("eval")
    return train_images, train_labels, test_images, test_labels
 
def combine_datasets(*datasets):
    train_images = np.concatenate([d[0] for d in datasets], axis=1)
    train_labels = np.concatenate([d[1] for d in datasets])
    test_images = np.concatenate([d[2] for d in datasets], axis=1)
    test_labels = np.concatenate([d[3] for d in datasets])
    return train_images, train_labels, test_images, test_labels
 
def save_dataset(path_prefix, train_images, train_labels, test_images, test_labels):
    np.save(f"{path_prefix}_train_images.npy", train_images)
    np.save(f"{path_prefix}_train_labels.npy", train_labels)
    np.save(f"{path_prefix}_test_images.npy", test_images)
    np.save(f"{path_prefix}_test_labels.npy", test_labels)
 
 
def load_saved_dataset(path_prefix):
    train_images = np.load(f"{path_prefix}_train_images.npy")
    train_labels = np.load(f"{path_prefix}_train_labels.npy")
    test_images = np.load(f"{path_prefix}_test_images.npy")
    test_labels = np.load(f"{path_prefix}_test_labels.npy")
    return train_images, train_labels, test_images, test_labels
 
OPERATOR_CLASS_MAP = {
    "plus": 10,
    "minus": 11,
    "times": 12,
    "div": 13,
    "equal": 14,
}
 
def load_operator_data(kaggle_root, save_converted_to=None):
    return load_dataset_from_class_folders(kaggle_root, OPERATOR_CLASS_MAP, save_converted_to)
