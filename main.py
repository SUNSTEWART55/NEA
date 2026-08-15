import cv2
import numpy as np
from neural_network import load_model, forward  # NEA model, not TensorFlow

MODEL_PATH_PREFIX = "models/trained_model"

# 1. intersection error: when 8 is written, the crossover between the loops
#    creates a small white dot, which can get detected as two separate shapes.
# 2. Confidence for 6 is often too high/inconsistent - keep an eye on this
#    once real predictions are flowing.

# smaller = less blur
BLUR_FACTOR = 3
# BLOCKSIZE = area to calculate light intensity in
# C = sensitivity (higher = more sensitive, fewer pixels pass)
BLOCKSIZE = 11
C = 15

# Absolute floor only - excludes true single-pixel sensor noise before we've
# even estimated font size. Everything else scales with the detected
# handwriting size below, rather than being a fixed pixel count.
ABSOLUTE_NOISE_FLOOR = 2

# A shape must have its largest dimension be at least this fraction of the
# estimated font size to count as a real character on its own (after merging).
MIN_CHARACTER_SIZE_RATIO = 0.3

# Widest a valid shape can be relative to its height, and vice versa - wide
# enough to allow flat strokes like "-" or "/", narrow enough to allow tall
# thin strokes like "1", without letting through near-square noise blobs
# relative to the rest of the frame.
ASPECT_MIN = 0.1
ASPECT_MAX = 15

# How close (vertically, as a fraction of font size) two shapes need to be
# to get merged into one - e.g. a division sign's dots joining its line, or
# the two bars of an equals sign joining each other.
MERGE_VERTICAL_GAP_RATIO = 0.6
# How much horizontal tolerance is allowed when checking two shapes are
# aligned (not just vertically close but positioned above/below each other).
MERGE_HORIZONTAL_MARGIN_RATIO = 0.3

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


def estimate_font_size(boxes):
    """
    Reference size for this frame, used to scale MIN_CHARACTER_SIZE and the
    merge-gap threshold instead of using fixed pixel values that only work
    at one distance/zoom level.

    Uses the LARGEST shape's size, not the median. A real character stroke
    (digit, line, etc.) is reliably the biggest thing in frame; dots and
    noise are reliably smaller than it. Median fails specifically when a
    frame has few "main" shapes and several small ones (e.g. a division
    sign alone: 1 line + 2 dots) - the median then lands on dot-size, not
    line-size, which produces a merge-gap threshold far too small to ever
    bridge the real gap between the dots and the line.
    """
    if not boxes:
        return None

    return max(max(x2 - x1, y2 - y1) for (x1, y1, x2, y2) in boxes)


def boxes_are_horizontally_aligned(box1, box2, margin):
    # True if the boxes' x-ranges overlap, or are within `margin` of overlapping.
    x1_a, _, x2_a, _ = box1
    x1_b, _, x2_b, _ = box2
    return not (x2_a + margin < x1_b or x2_b + margin < x1_a)


def vertical_gap_between(box1, box2):
    # Gap between the boxes along the y-axis; 0 if they already overlap vertically.
    _, y1_a, _, y2_a = box1
    _, y1_b, _, y2_b = box2
    if y2_a < y1_b:
        return y1_b - y2_a
    if y2_b < y1_a:
        return y1_a - y2_b
    return 0


def merge_two_boxes(box1, box2):
    x1_a, y1_a, x2_a, y2_a = box1
    x1_b, y1_b, x2_b, y2_b = box2
    return (min(x1_a, x1_b), min(y1_a, y1_b), max(x2_a, x2_b), max(y2_a, y2_b))


def merge_nearby_shapes(boxes, font_size):
    """
    Combines shapes that are vertically close AND horizontally aligned into
    a single box. findContours sees a division sign as 3 separate shapes
    (2 dots + 1 line) and an equals sign as 2 separate shapes (2 bars) -
    this joins each group back into one box before size/aspect filtering,
    so they get recognized as a single character instead of being dropped
    or misread individually.

    Runs repeatedly so chains merge fully (e.g. dot -> line -> dot), not
    just adjacent pairs on a single pass.
    """
    if font_size is None or len(boxes) < 2:
        return boxes

    gap_threshold = font_size * MERGE_VERTICAL_GAP_RATIO
    horizontal_margin = font_size * MERGE_HORIZONTAL_MARGIN_RATIO

    merged = list(boxes)
    merge_happened = True

    while merge_happened:
        merge_happened = False
        for i in range(len(merged)):
            for j in range(i + 1, len(merged)):
                close_enough = vertical_gap_between(merged[i], merged[j]) < gap_threshold
                aligned = boxes_are_horizontally_aligned(merged[i], merged[j], horizontal_margin)
                if close_enough and aligned:
                    merged[i] = merge_two_boxes(merged[i], merged[j])
                    del merged[j]
                    merge_happened = True
                    break
            if merge_happened:
                break

    return merged


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

        # Step 1: collect every contour as a raw box first, past only the
        # absolute noise floor - no size/aspect filtering yet, since that
        # needs an estimated font size, and merging needs to happen before
        # small (but legitimate) marks like division dots get judged.
        raw_boxes = []
        for shape in contours:
            x, y, width, height = cv2.boundingRect(shape)

            if width >= ABSOLUTE_NOISE_FLOOR and height >= ABSOLUTE_NOISE_FLOOR:
                x_padding = int(width * PADDING_MULTIPLIER)
                y_padding = int(height * PADDING_MULTIPLIER)

                x1 = max(0, x - x_padding)
                y1 = max(0, y - y_padding)
                x2 = min(frame.shape[1], x + width + x_padding)
                y2 = min(frame.shape[0], y + height + y_padding)

                raw_boxes.append((x1, y1, x2, y2))

        # Step 2: estimate this frame's handwriting size from the raw boxes,
        # so every threshold below scales with how big the writing actually
        # is, instead of being tuned for one distance/zoom level.
        font_size = estimate_font_size(raw_boxes)

        # Step 3: merge vertically-close, horizontally-aligned shapes - this
        # is what joins division dots to their line, and joins the two bars
        # of an equals sign, before either gets judged on size alone.
        merged_boxes = merge_nearby_shapes(raw_boxes, font_size)

        print(f"font_size={font_size}")
        for (x1, y1, x2, y2) in merged_boxes:
            w, h = x2 - x1, y2 - y1
            print(f"  merged box: w={w} h={h} ratio={w/h:.2f} max_dim={max(w, h)}")

        # Step 4: NOW apply the real size/aspect filter, scaled to this
        # frame's font size. Anything still too small here never found a
        # merge partner, which is exactly what should happen to real noise.
        sized_boxes = []
        min_character_size = (font_size * MIN_CHARACTER_SIZE_RATIO) if font_size else 0
        for (x1, y1, x2, y2) in merged_boxes:
            width = x2 - x1
            height = y2 - y1
            aspect_ratio = width / height if height else 0

            if max(width, height) >= min_character_size and ASPECT_MIN < aspect_ratio < ASPECT_MAX:
                sized_boxes.append((x1, y1, x2, y2))

        # Step 5: filter out boxes contained inside other boxes, ONCE, after
        # all boxes for this frame are known.
        filtered_boxes = filter_boxes(sized_boxes)

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