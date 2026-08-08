import numpy as np
from tensorflow.keras.datasets import mnist

def load_digit_data():
    (train_images, train_labels), (test_images, test_labels) = mnist.load_data()

    train_images = train_images.reshape(train_images.shape[0], 784).T / 255.0
    test_images = test_images.reshape(test_images.shape[0], 784).T / 255.0

    return train_images, train_labels, test_images, test_labels

# creates inital random weights and assigns biases to 0
def init_layer(neurons_in, neurons_out):
    weights = np.random.randn(neurons_out, neurons_in) * 0.01
    biases = np.zeros(((neurons_out, 1)))
    return weights, biases

# creates neural netowek and assigns weights and biases to each neuron
def init_network():
    weight_1, bias_1 = init_layer(784, 128)
    weight_2, bias_2 = init_layer(128, 64)
    weight_3, bias_3 = init_layer(64, 15)
    return weight_1, bias_1, weight_2, bias_2, weight_3, bias_3

# used on hidden layers
def rectified_linear_unit(weighted_sum):
    return np.maximum(0, weighted_sum)

# used on output layer to get probability prediction
def softmax(weighted_sum):
    expZ = np.exp(weighted_sum - np.max(weighted_sum, axis=0, keepdims = True))
    return expZ / np.sum(expZ, axis=0, keepdims = True)

def forward(input_pixels_for_batch, weight_1, bias_1, weight_2, bias_2, weight_3, bias_3):
    hidden1_weighted_sum = weight_1.dot(input_pixels_for_batch) + bias_1
    hidden1_activated = rectified_linear_unit(hidden1_weighted_sum)

    hidden2_weighted_sum = weight_2.dot(hidden1_activated) + bias_2
    hidden2_activated = rectified_linear_unit(hidden2_weighted_sum)

    output_weighted_sum = weight_3.dot(hidden2_activated) + bias_3
    output_activated = softmax(output_weighted_sum)

    return hidden1_weighted_sum, hidden1_activated, hidden2_weighted_sum, hidden2_activated, output_weighted_sum, output_activated

# calculates the loss
def cross_entropy_loss(output_activated, labels):
    n_samples = labels.shape[0]
    correct_class_probability = output_activated[labels, np.arange(n_samples)]
    loss = -np.mean(np.log(correct_class_probability + 1e-9))
    return loss

# converts from one-hot into matrix of integers
def one_hot(labels, num_classes=15):
    one_hot_labels = np.zeros((num_classes, labels.shape[0]))
    one_hot_labels[labels, np.arange(labels.shape[0])] = 1
    return one_hot_labels

def rectified_linear_unit_derivative(weighted_sum):
    return (weighted_sum > 0).astype(float)

def backward(input_pixels,labels, weight_1, bias_1, weight_2, bias_2, weight_3, bias_3, hidden1_weighted_sum, hidden1_activated, hidden2_weighted_sum, hidden2_activated, output_weighted_sum, output_activated):
    n_samples = input_pixels.shape[1]
    one_hot_labels = one_hot(labels)

    # output layer
    output_error = output_activated - one_hot_labels
    weight3_gradient = output_error.dot(hidden2_activated.T) / n_samples
    bias3_gradient = np.sum(output_error, axis=1, keepdims=True) / n_samples

    # hidden layer 2
    hidden2_error = weight_3.T.dot(output_error) * rectified_linear_unit_derivative(hidden2_weighted_sum)
    weight2_gradient = hidden2_error.dot(hidden1_activated.T) / n_samples
    bias2_gradient = np.sum(hidden2_error, axis=1, keepdims=True) / n_samples

    # hidden layer 1
    hidden1_error = weight_2.T.dot(hidden2_error) * rectified_linear_unit_derivative(hidden1_weighted_sum)
    weight1_gradient = hidden1_error.dot(input_pixels.T) / n_samples
    bias1_gradient = np.sum(hidden1_error, axis=1, keepdims=True) / n_samples

    return weight1_gradient, bias1_gradient, weight2_gradient, bias2_gradient, weight3_gradient, bias3_gradient

# nudges all weights and biases to move closer to being correct
def update_parameters(weight_1, bias_1, weight_2, bias_2, weight_3, bias_3, weight1_gradient, bias1_gradient, weight2_gradient, bias2_gradient, weight3_gradient, bias3_gradient, learning_rate):
    weight_1 = weight_1 - learning_rate * weight1_gradient
    bias_1 = bias_1 - learning_rate * bias1_gradient

    weight_2 = weight_2 - learning_rate * weight2_gradient
    bias_2 = bias_2 -learning_rate * bias2_gradient

    weight_3 = weight_3 - learning_rate * weight3_gradient
    bias_3 = bias_3 -learning_rate * bias3_gradient

    return weight_1, bias_1, weight_2, bias_2, weight_3, bias_3

def train_step(input_pixels, labels, weight_1, bias_1, weight_2, bias_2, weight_3, bias_3, learning_rate):
    # forward pass
    hidden1_weighted_sum, hidden1_activated, hidden2_weighted_sum, hidden2_activated, output_weighted_sum, output_activated = forward(input_pixels, weight_1, bias_1, weight_2, bias_2, weight_3, bias_3)

    loss = cross_entropy_loss(output_activated, labels)

    # works out how adjust values
    weight1_gradient, bias1_gradient, weight2_gradient, bias2_gradient, weight3_gradient, bias3_gradient = backward(input_pixels, labels, weight_1, bias_1, weight_2, bias_2, weight_3, bias_3, hidden1_weighted_sum, hidden1_activated, hidden2_weighted_sum, hidden2_activated, output_weighted_sum, output_activated)
    
    # adjust value
    weight_1, bias_1, weight_2, bias_2, weight_3, bias_3 = update_parameters(weight_1, bias_1, weight_2, bias_2, weight_3, bias_3, weight1_gradient, bias1_gradient, weight2_gradient, bias2_gradient, weight3_gradient, bias3_gradient, learning_rate)

    return weight_1, bias_1, weight_2, bias_2, weight_3, bias_3, loss

def train_network(train_images, train_labels, weight_1, bias_1, weight_2, bias_2,weight_3, bias_3, learning_rate, epochs, batch_size):

    n_samples = train_images.shape[1]
    best_accuracy = 0
    best_weights = None

    for epoch in range(epochs):
        # shuffles data for each epoch
        permutation = np.random.permutation(n_samples)
        shuffled_images = train_images[:, permutation]
        shuffled_labels = train_labels[permutation]

        epochs_loss = 0
        n_batches = 0

        for start in range(0, n_samples, batch_size):
            end = start + batch_size
            batch_images = shuffled_images[:, start:end]
            batch_labels = shuffled_labels[start:end]

            weight_1, bias_1, weight_2, bias_2, weight_3, bias_3, loss = train_step(batch_images, batch_labels, weight_1, bias_1, weight_2, bias_2, weight_3, bias_3, learning_rate)

            epochs_loss += loss
            n_batches += 1

        average_loss = epochs_loss / n_batches
        test_accuracy = evaluate(test_images, test_labels, weight_1, bias_1, weight_2, bias_2, weight_3, bias_3)
        print(f"epoch {epoch}, average loss = {average_loss}, test accuracy = {test_accuracy * 100:.2f}")

        if test_accuracy > best_accuracy:
            best_accuracy = test_accuracy
            best_weights = (weight_1.copy(), bias_1.copy(), weight_2.copy(), bias_2.copy(), weight_3.copy(), bias_3.copy())

    return best_weights

def evaluate(test_images, test_labels, weight_1, bias_1, weight_2, bias_2, weight_3, bias_3):
    _, _, _, _, _, output_activated = forward(test_images, weight_1, bias_1, weight_2, bias_2, weight_3, bias_3)

    predictions = np.argmax(output_activated, axis=0)
    accuracy = np.mean(predictions == test_labels)
    return accuracy


train_images, train_labels, test_images, test_labels = load_digit_data()
weight_1, bias_1, weight_2, bias_2, weight_3, bias_3 = init_network()

weight_1, bias_1, weight_2, bias_2, weight_3, bias_3 = train_network(
    train_images, train_labels, weight_1, bias_1, weight_2, bias_2, weight_3, bias_3,
    learning_rate=0.5, epochs=20, batch_size=64
)

accuracy = evaluate(test_images, test_labels, weight_1, bias_1, weight_2, bias_2, weight_3, bias_3)
print(f"best found accuracy = {accuracy *100:.2f}%")