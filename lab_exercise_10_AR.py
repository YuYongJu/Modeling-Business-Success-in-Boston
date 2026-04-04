# LAB EXERCISES 10 by Abigail Rillovick

import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, f1_score
# Predefined dataset
data = {
'ID': list(range(1, 101)),
'Hours_worked': [150, 72, 168, 55, 30, 10, 158, 60, 170, 128, 120, 115, 50,
145, 118, 58, 172, 110, 70, 140, 85, 95, 102, 66, 134, 143, 77, 89, 160, 121, 109,
97, 53, 147, 112, 59, 165, 108, 73, 138, 92, 101, 104, 69, 132, 141, 79, 87, 162,
119, 107, 99, 56, 148, 114, 61, 167, 105, 75, 136, 90, 100, 106, 67, 133, 142, 78,
88, 161, 122, 110, 98, 54, 146, 113, 60, 166, 107, 74, 137, 91, 103, 105, 68, 131,
139, 80, 86, 159, 123, 111, 96, 52, 144, 117, 62, 169, 109, 76, 135],
'Coffee_intake': [3.1, 2.9, 5.0, 2.5, 4.4, 2.0, 3.6, 3.0, 5.3, 2.4, 5.9, 3.2,
1.9, 5.7, 2.7, 4.6, 4.8, 5.4, 4.1, 3.5, 3.0, 2.7, 4.9, 2.8, 5.6, 5.2, 3.3, 3.8,
4.2, 2.6, 3.4, 2.9, 2.1, 5.5, 2.8, 4.3, 5.1, 5.0, 3.7, 3.6, 2.9, 3.1, 4.8, 2.7,
5.4, 5.3, 3.2, 3.9, 4.0, 2.5, 3.3, 2.8, 2.2, 5.6, 2.9, 4.4, 5.2, 5.1, 3.8, 3.7,
3.0, 3.2, 4.7, 2.6, 5.5, 5.4, 3.1, 3.8, 4.1, 2.7, 3.5, 2.9, 2.3, 5.7, 2.8, 4.5,
5.3, 5.2, 3.6, 3.5, 2.8, 3.0, 4.6, 2.7, 5.3, 5.2, 3.4, 3.9, 4.2, 2.6, 3.6, 2.8,
2.4, 5.8, 2.9, 4.6, 5.4, 5.3, 3.7, 3.6],
'Sleep_hours': [5.1, 7.2, 4.8, 7.5, 8.0, 8.5, 5.0, 7.0, 4.5, 6.2, 4.3, 6.8,
7.8, 4.9, 6.5, 7.1, 4.7, 4.4, 6.0, 5.8, 6.9, 7.3, 4.6, 7.0, 4.8, 5.0, 6.7, 6.4,
5.3, 6.6, 6.3, 7.1, 7.7, 4.9, 6.8, 6.2, 5.1, 4.6, 6.3, 5.9, 7.0, 6.8, 4.7, 7.2,
4.9, 5.1, 6.6, 6.3, 5.4, 6.7, 6.4, 7.2, 7.6, 4.8, 6.9, 6.1, 5.0, 4.7, 6.2, 5.8,
6.8, 6.6, 4.8, 7.1, 4.9, 5.2, 6.5, 6.2, 5.2, 6.5, 6.1, 7.0, 7.5, 4.7, 6.8, 6.0,
4.9, 4.8, 6.1, 5.9, 6.9, 6.7, 4.9, 7.0, 5.0, 5.2, 6.4, 6.1, 5.3, 6.4, 5.9, 6.9,
7.4, 4.6, 6.7, 5.9, 4.8, 4.7, 6.0, 5.8],
'Stress_level': [6.2, 5.5, 7.7, 5.3, 6.8, 4.9, 6.1, 5.8, 7.5, 6.4, 8.1, 5.6,
5.0, 7.5, 5.9, 6.6, 7.2, 7.8, 6.2, 6.0, 5.7, 5.4, 7.3, 5.6, 7.6, 7.4, 6.1, 6.3,
6.5, 5.5, 5.9, 5.7, 5.1, 7.4, 5.8, 6.5, 7.3, 7.2, 6.2, 6.1, 5.8, 6.0, 7.1, 5.5,
7.5, 7.3, 6.0, 6.2, 6.4, 5.4, 5.8, 5.6, 5.2, 7.6, 5.7, 6.6, 7.4, 7.3, 6.3, 6.2,
5.9, 6.1, 7.0, 5.5, 7.4, 7.2, 6.1, 6.3, 6.5, 5.6, 5.9, 5.7, 5.3, 7.7, 5.8, 6.7,
7.5, 7.4, 6.2, 6.1, 5.7, 5.9, 6.9, 5.4, 7.3, 7.2, 6.0, 6.3, 6.6, 5.5, 6.0, 5.8,
5.4, 7.8, 5.9, 6.8, 7.6, 7.5, 6.3, 6.2],
}
df = pd

df = pd.DataFrame(data)

# problem 1
def binarize_stress(df, threshold):
    """Converts continuous Stress_level column
    into binary target variable, creates new columns High_stress
    that is 1 if Stress_level >= threshold or else 0, 
    drops Stress_level column
    Parameters: df (DataFrame): contains Stress_level column
    threshold (float): threshold value
    Returns: df (DataFrame): with High_stress column and without Stress_level column"""
    df['High_stress'] = (df['Stress_level'] >= threshold).astype(int)
    df.drop(columns=['Stress_level'], inplace=True)
    return df

# problem 2
def split_data(df):
    """Splits dataset into training, validation, and test sets"""
    X = df.drop(columns=['High_stress'])
    y = df['High_stress']
    X_temp, X_test, y_temp, y_test = train_test_split(X, y, test_size=0.2, random_state=2500)
    X_train, X_val, y_train, y_val = train_test_split(X_temp, y_temp, test_size=0.2, random_state=2500)
    return X_train, X_val, X_test, y_train, y_val, y_test

def feature_selection(X_train, X_val, X_test, cols):
    """Selects specific features from the feature sets"""
    X_train_sel = X_train[cols]
    X_val_sel = X_val[cols]
    X_test_sel = X_test[cols]
    return X_train_sel, X_val_sel, X_test_sel

# problem 3
def train_model(X_train, y_train):
    """Trains a logistic regression model on the training data"""
    model = LogisticRegression()
    model.fit(X_train, y_train)
    return model

# problem 4
def evaluate_model(model, X, y):
    """Evaluates a trained model on a dataset and 
    returns performance metrics"""
    y_pred = model.predict(X)
    acc = accuracy_score(y, y_pred)
    f1 = f1_score(y, y_pred, average='binary')
    return acc, f1

def main():
    print("Problem 1: Binarize Stress Level")
    df_binary = binarize_stress(df, threshold=6.5)
    print(f"Columns after binarization: {df_binary.columns.tolist()}")
    print(f"High stress class counts:\n{df_binary['High_stress'].value_counts()}")

    print("Problem 2")
    X_train, X_val, X_test, y_train, y_val, y_test = split_data(df_binary)
    print(f"Training set:   {len(X_train)} samples")
    print(f"Validation set: {len(X_val)} samples")
    print(f"Test set:       {len(X_test)} samples")
    print(f"Feature columns:    {X_train.columns.tolist()}")

    features = ['Hours_worked', 'Coffee_intake', 'Sleep_hours']
    X_train_sel, X_val_sel, X_test_sel = feature_selection(X_train, X_val, X_test, features)
    print(f"Selected features: {X_train_sel.columns.tolist()}")

    print("Problem 3: Training Model")
    model = train_model(X_train_sel, y_train)

    print("Problem 4: Evaluating Model")
    train_acc, train_f1 = evaluate_model(model, X_train_sel, y_train)
    val_acc, val_f1 = evaluate_model(model, X_val_sel, y_val)
    test_acc, test_f1 = evaluate_model(model, X_test_sel, y_test)

    print(f"Training Set - Accuracy: {train_acc:.4f}, F1: {train_f1:.4f}")
    print(f"Validation Set - Accuracy: {val_acc:.4f}, F1: {val_f1:.4f}")
    print(f"Test Set - Accuracy: {test_acc: .4f}, F1: {test_f1:.4f}")

    # Compare with single feature model
    print("Comparing with single feature (Hours_worked only)")
    X_train_h, X_val_h, X_test_h = feature_selection(X_train, X_val, X_test, ['Hours_worked'])
    model_hours = train_model(X_train_h, y_train)
    test_acc_h, test_f1_h = evaluate_model(model_hours, X_test_h, y_test)
    print(f"Single feature model - Accuracy: {test_acc_h:.4f}, F1: {test_f1_h:.4f}")

if __name__ == '__main__':
    main()