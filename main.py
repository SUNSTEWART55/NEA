import cv2
import numpy as np
from neural_network import load_model, forward

# where local model is stored
MODEL_PATH_PREFIX = "models/trained_model"
 
# smaller = less blur
BLUR_FACTOR = 3
# BLOCKSIZE = area to calculate light intensity in
# C = sensitivity (higher = more sensitive, fewer pixels pass)
BLOCKSIZE = 11
C = 15
# minimum pixel size to be detected
MIN_CHARACTER_SIZE = 10
# value between 0 and 1, decides whether confident enough to output
CONFIDENCE_THRESHOLD = 0.7
# add extra space on sides to not cut off numbers, scales with the font size
PADDING_MULTIPLIER = 0.1
 
BOX_COLOR = (0, 255, 0)  # green
TEXT_COLOR = (0, 0, 255)  # red
 
# 15 classes, ordered to match OPERATOR_CLASS_MAP indices from data_loader.py
# 0-9 = digits, 10-14 = operators
LABELS = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9',
          '+', '-', 'x', '/', '=']
 
# Pixels close enough to make same colour, to fill in lighter gaps of pen strokes
MERGE_RANGE = 6
 
 
def start_model():
    """
    Loads the trained NEA model. load_model() returns a flat tuple:
    (weight_1, bias_1, weight_2, bias_2, weight_3, bias_3)
    which matches forward()'s positional arguments exactly.
    """
    model = load_model(MODEL_PATH_PREFIX)
    print("Model loaded, starting webcam...")
    return model
 
 
def image_processing(frame):
    # blurs the image to reduce noise
    blurred = cv2.GaussianBlur(frame, (BLUR_FACTOR, BLUR_FACTOR), 0)
    # sets to greyscale
    gray = cv2.cvtColor(blurred, cv2.COLOR_BGR2GRAY)
 
    # Makes image inverted black and white, adaptive so it adjusts to light
    # intensity in different areas of the frame
    threshold = cv2.adaptiveThreshold(
        gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY_INV, BLOCKSIZE, C
    )
    return threshold
 
 
def close_small_gaps(threshold, merge_range):
    # creates a circular structuring element by the size of merge_range
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (merge_range, merge_range))
    # closes small gaps using that element
    threshold = cv2.morphologyEx(threshold, cv2.MORPH_CLOSE, kernel)
    return threshold
 
 
def roi_reshaping(threshold, x1, y1, x2, y2):
    """
    Reshapes a region of interest to match the NEA model's expected input.
    forward() does weight_1.dot(input_pixels_for_batch) - weights on the
    left - so the input must be a COLUMN vector, shape (784, 1), not a
    row vector like (1, 784). This is the opposite convention to Keras.
    """
    roi = threshold[y1:y2, x1:x2]
    roi = cv2.resize(roi, (28, 28))
    roi = roi.astype(np.float32) / 255.0
    roi = roi.reshape(784, 1)  # column vector: 784 -> 128 -> 64 -> 15
    return roi
 
 
def is_inside(box1, box2):
    x1_a, y1_a, x2_a, y2_a = box1
    x1_b, y1_b, x2_b, y2_b = box2
 
    centre_x = (x1_a + x2_a) / 2
    centre_y = (y1_a + y2_a) / 2
    return x1_b <= centre_x <= x2_b and y1_b <= centre_y <= y2_b
 
 
def filter_boxes(boxes):
    """
    Removes boxes that are contained inside another box - used to fix the
    intersection error (e.g. an 8 being detected as two separate shapes).
    Fixed: the old code re-checked is_inside(box, other_box) using a stale
    leftover loop variable. All that's needed is "keep it if it wasn't
    found inside anything else."
    """
    filtered_boxes = []
    for i, box in enumerate(boxes):
        contained = False
        for j, other_box in enumerate(boxes):
            if i != j and is_inside(box, other_box):
                contained = True
                break
        if not contained:
            filtered_boxes.append(box)
    return filtered_boxes
 
 
def number_recognition(model, roi, frame, x1, y1, x2, y2):
    """
    Runs the NEA forward pass on a single ROI and draws the result.
    forward() takes the input plus all 6 weight/bias arrays as separate
    positional args, and returns all intermediate activations - only the
    last one, output_activated, is the softmax prediction we need.
    """
    weight_1, bias_1, weight_2, bias_2, weight_3, bias_3 = model
    *_ , output_activated = forward(roi, weight_1, bias_1, weight_2, bias_2, weight_3, bias_3)
 
    label_index = np.argmax(output_activated)
    confidence = np.max(output_activated)
 
    if confidence > CONFIDENCE_THRESHOLD:
        label = LABELS[label_index]
    else:
        label = "?"
 
    cv2.rectangle(frame, (x1, y1), (x2, y2), BOX_COLOR, 2)
    cv2.putText(frame, f"{label} {confidence:.0%}", (x1, y1 - 10),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, TEXT_COLOR, 2)
 
    return label
 
 
def main():
    model = start_model()
    webcam = cv2.VideoCapture(0)
 
    while True:
        ret, frame = webcam.read()
        if not ret:
            break
 
        threshold = image_processing(frame)
        threshold = close_small_gaps(threshold, MERGE_RANGE)
 
        # finds shapes in the image
        contours, _ = cv2.findContours(threshold, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        # sorts shapes left to right
        contours = sorted(contours, key=lambda c: cv2.boundingRect(c)[0])
 
        # Step 1: collect every valid box first, before filtering or recognizing.
        boxes = []
        for shape in contours:
            x, y, width, height = cv2.boundingRect(shape)
            aspect_ratio = width / height
 
            if width > MIN_CHARACTER_SIZE and height > MIN_CHARACTER_SIZE and 0.2 < aspect_ratio < 2.0:
                x_padding = int(width * PADDING_MULTIPLIER)
                y_padding = int(height * PADDING_MULTIPLIER)
 
                x1 = max(0, x - x_padding)
                y1 = max(0, y - y_padding)
                x2 = min(frame.shape[1], x + width + x_padding)
                y2 = min(frame.shape[0], y + height + y_padding)
 
                boxes.append((x1, y1, x2, y2))
 
        # Step 2: filter out boxes contained inside other boxes, ONCE, after
        # all boxes for this frame are known.
        filtered_boxes = filter_boxes(boxes)
 
        # Step 3: recognize each filtered box, using that box's own coordinates
        # (the old code accidentally reused the last x1,y1,x2,y2 from the
        # outer loop instead of the box being iterated over).
        expression = ""
        for (x1, y1, x2, y2) in filtered_boxes:
            roi = roi_reshaping(threshold, x1, y1, x2, y2)
            label = number_recognition(model, roi, frame, x1, y1, x2, y2)
            expression += label
 
        cv2.imshow("math detector", frame)
        cv2.imshow("threshold", threshold)
 
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
 
    webcam.release()
    cv2.destroyAllWindows()
 
 
if __name__ == "__main__":
    main()
