import numpy as np
from neural_network import init_network, train_network, evaluate
from data_loader import load_digit_data

train_images, train_labels, test_images, test_labels = load_digit_data()
weight_1, bias_1, weight_2, bias_2, weight_3, bias_3 = init_network()

weight_1, bias_1, weight_2, bias_2, weight_3, bias_3 = train_network(
    train_images, train_labels, test_images, test_labels,
    weight_1, bias_1, weight_2, bias_2, weight_3, bias_3,
    learning_rate=0.5, epochs=20, batch_size=64
)

accuracy = evaluate(test_images, test_labels, weight_1, bias_1, weight_2, bias_2, weight_3, bias_3)
print(f"final accuracy = {accuracy * 100:.2f}%")