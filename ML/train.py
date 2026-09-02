import numpy as np
from ML.neural_network import init_network, train_network, evaluate, save_model, load_model
from ML.data_loader import (
    load_digit_data,
    load_operator_data,
    combine_datasets,
    save_dataset,
    load_saved_dataset,
)

KAGGLE_ROOT = r"C:\coding_projects\python_projects\NEA\data\archive_cleaned"
CONVERTED_OUTPUT = r"C:\coding_projects\python_projects\NEA\data\converted_operators"
 
print("loading MNIST...")
mnist_data = load_digit_data()
 
print("loading and converting operator data...")
operator_data = load_operator_data(KAGGLE_ROOT, save_converted_to=CONVERTED_OUTPUT)
 
print("combining datasets...")
train_images, train_labels, test_images, test_labels = combine_datasets(mnist_data, operator_data)
print(f"combined: {train_images.shape[1]} training images, {test_images.shape[1]} test images, "
      f"classes present: {sorted(set(train_labels.tolist()))}")
 
print("saving combined dataset to disk (so future runs can skip reloading/reconverting)...")
save_dataset("data/combined_dataset", train_images, train_labels, test_images, test_labels)
 
print("training...")
weight_1, bias_1, weight_2, bias_2, weight_3, bias_3 = init_network()
weight_1, bias_1, weight_2, bias_2, weight_3, bias_3 = train_network(
    train_images, train_labels, test_images, test_labels,
    weight_1, bias_1, weight_2, bias_2, weight_3, bias_3,
    learning_rate=0.5, epochs=20, batch_size=64,
)
 
print("saving trained model...")
save_model("models/trained_model", weight_1, bias_1, weight_2, bias_2, weight_3, bias_3)
 
print("evaluating final saved model...")
w1, b1, w2, b2, w3, b3 = load_model("models/trained_model")
accuracy = evaluate(test_images, test_labels, w1, b1, w2, b2, w3, b3)
print(f"final accuracy (reloaded model) = {accuracy * 100:.2f}%")
