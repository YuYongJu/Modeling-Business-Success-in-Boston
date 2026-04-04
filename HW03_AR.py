# HW 03 Abigail Rillovick

import pandas as pd
import math
import statistics
import numpy as np
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import f1_score

# Part 1

class KNN:
    def __init__(self, k):
        """Initalizes the KNN model"""
        self.k = k

    def fit(self, X, y):
        """Store training data and labels"""
        self.X_train = X
        self.y_train = [int(label) for label in y]

    def euclidean_distance(self, x1, x2):
        """Compare Euclidean distance between two data points
        Parameters: x1 (list): first data point
        x2 (list): second data point
        Returns: ed (float): Euclidean distance between x1 and x2"""
        ed = math.sqrt(sum((y - z) ** 2 for y,z in zip(x1, x2)))
        return ed
    
    def compute_distances(self, x):
        """Computes the distance from a single input point to all training data points
        Parameters: x (list): input data point
        Returns: distances (list of tuples): list of tuples containing the distance and corresponding label for each training data point"""
        distances = []
        for i in range(len(self.X_train)):
            dist = self.euclidean_distance(x, self.X_train[i])
            label = self.y_train[i]
            if isinstance(label, list):
                label = label[0]
            distances.append((dist, label))
        return distances
    
    def get_kneighbors(self, distances):
        """Sort the list of (distance, label) tuples by distance in ascending
        order and return return only the k nearest neighbors
        Parameters: distances (list of tuples): list of tuples as returned by compute_distances
        Returns: k_neighbors (list of tuples): list of the k nearest neighbors (distance, label) tuples"""
        sorted_distances = sorted(distances, key=lambda x: x[0])
        k_neighbors = sorted_distances[:self.k]
        return k_neighbors
    
    def classification(self, k_nearest):
        """Takes K nearest neighbors and returns the most frequently occurring
        class labels among them (majority vote)
        Parameters: k_nearest (list of tuples): list of the k nearest neighbors (distance, label) tuples
        Returns: predicted_label (int): predicted class label by majority vote among K neighbors"""
        labels = [label for _, label in k_nearest]
        predicted_label = statistics.mode(labels)
        return predicted_label
    
    def predict_single(self, x):
        """Coordinates the full prediction pipline for a single data point by calling
        compute_distances, get_kneighbors, and classification in order
        Parameters: x (list): input data point
        Returns: predicted_label (int): predicted class label for input data point"""
        distances = self.compute_distances(x)
        k_nearest = self.get_kneighbors(distances)
        predicted_label = self.classification(k_nearest)
        return predicted_label
    
    def predict(self, X):
        """Generates predictions for a list of input data points by calling predict_single for each point
        Parameters: X (list of lists): list of input data points
        Returns: predictions (list): list of predicted class labels for each input data point"""
        predictions = [self.predict_single(x) for x in X]
        return predictions

# Part 2
# DS 2500 Spring 2026 HW 03 by Abigail Rillovick
# kn main
if __name__ == "__main__":
    X_train_full = pd.read_csv("HW_03_train_features.csv")
    y_train_full = pd.read_csv("HW_03_train_target.csv").squeeze()

    if "ROW_ID" in y_train_full.columns:
        y_train_full.drop(columns=["ROW_ID"], inplace=True)
    y_train_full = y_train_full.squeeze()

    X_test = pd.read_csv("HW_03_test_features.csv")

    # drop ROW_ID column from dataframes if exists
    if "ROW_ID" in X_train_full.columns:
        X_train_full.drop(columns=["ROW_ID"], inplace=True)
    if "ROW_ID" in X_test.columns:
        X_test.drop(columns=["ROW_ID"], inplace=True)

    y_train_full = y_train_full.squeeze()

    def preprocess(X_train, X_val, X_test):
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_val_scaled = scaler.transform(X_val)
        X_test_scaled = scaler.transform(X_test)
        return X_train_scaled.tolist(), X_val_scaled.tolist(), X_test_scaled.tolist()

    X_train, X_val, y_train, y_val = train_test_split(X_train_full, y_train_full, test_size=0.2, random_state=2500)

    X_train_scaled, X_val_scaled, X_test_scaled = preprocess(X_train, X_val, X_test)

    y_train_list = y_train.astype(int).tolist()
    y_val_list = y_val.astype(int).tolist()

    def find_best_k(X_train, y_train, X_val, y_val, max_k=30):
        best_k = 1
        best_f1 = 0

        for k in range(1, max_k + 1, 2):
            model = KNN(k)
            model.fit(X_train, y_train)
            preds = model.predict(X_val)
            score = f1_score(y_val, preds)

            if score > best_f1:
                best_f1 = score
                best_k = k      
        return best_k

    best_k = find_best_k(X_train_scaled, y_train_list, X_val_scaled, y_val_list)

    # check validation performance
    val_model = KNN(best_k)
    val_model.fit(X_train_scaled, y_train_list)
    val_preds = val_model.predict(X_val_scaled)

    # retrain on data and predict on test set
    X_full_scaled, _, X_test_final_scaled = preprocess(X_train_full, X_train_full, X_test)
    y_full_list = y_train_full.astype(int).tolist()

    final_model = KNN(best_k)
    final_model.fit(X_full_scaled, y_full_list)

    test_preds = final_model.predict(X_test_final_scaled)

    output = pd.DataFrame({
        "ROW_ID": range(len(test_preds)),
        "Target": test_preds
    })

    output.to_csv("HW_03_predictions.csv", index=False)