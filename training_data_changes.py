import cv2
import numpy as np

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

    cropped = image[y_min:y_max+1, x_min:x_max+1]

    target_size = output_size - margin

    h, w = cropped.shape
    scale = target_size / max(h, w)
    new_h, new_w = int(h * scale), int(w * scale)

    resized = cv2.resize(cropped, (new_w, new_h), interpolation=cv2.INTER_AREA)

    canvas = np.zeros((output_size, output_size), dtype=np.uint8)
    y_offset = (output_size - new_h) // 2
    x_offset = (output_size - new_w) // 2
    canvas[y_offset : y_offset+new_h, x_offset : x_offset+new_w] = resized

    return canvas



img = cv2.imread(r"C:\Users\harry\Downloads\archive\train\div\998.jpg", cv2.IMREAD_GRAYSCALE)

img = invert(img)
img = center_and_resize(img)

print(img.shape)

cv2.imshow("final", img)
cv2.waitKey(0)