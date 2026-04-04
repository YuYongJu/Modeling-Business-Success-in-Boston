# Lab 08
# Abigail Rillovick
# 3/19/2026
from sklearn.cluster import KMeans
from sklearn.cluster import AgglomerativeClustering
from sklearn.metrics import silhouette_score
from sklearn.datasets import load_iris

# Problem 1

def perform_kmeans(X, n_clusters):
    """Performs K-Means clustering on the data.
    Parameters: X (list of lists): Feature data
     n_clusters (int): Number of clusters """
    model = KMeans(n_clusters=n_clusters, random_state=2500)
    model.fit(X)
    labels = model.labels_.tolist()
    print("Cluster labels: ", labels)
    return labels

# Problem 2

def perform_hierarchical(X, n_clusters):
    """Performs hierarchical clustering on the data. 
    Parameters: X (list of lists): Feature data
     n_clusters (int): Number of clusters
      Rwturns: labels(list): cluster labels for each sample"""
    model = AgglomerativeClustering(n_clusters=n_clusters, linkage='average')
    model.fit(X)
    labels = model.labels_.tolist()
    return labels

# Problem 3
def find_optimal_clusters(X, clustering_option="kmeans", max_k=10):
    """Finds the optimal number of clusters by testing different 
    values of k and comparing their silhouette scores.
    Parameters: X (list of lists): Feature data
     clustering_option (str): Indicates which clustering method to use, either
     'kmeans' or 'hierarchical' (default = 'kmeans')
     max_k (int): Maximum number of clusters to test (default = 10)
     Returns: high_k (int): Optimal number of clusters (k with highest silhouette score)"""
    high_k = 2
    high_score = -1
    for k in range(2, max_k + 1):
        if clustering_option == 'hierarchical':
            labels = perform_hierarchical(X, k)
            score = silhouette_score(X, labels)
            score = float(score)
            print(f"Silhouette Score: {score:.3f}")
            if score > high_score:
                high_score = score
                high_k = k
        else:
            labels = perform_kmeans(X, k)
            score = silhouette_score(X, labels)
            score = float(score)
            print(f"Silhouette Score: {score:.3f}")
            if score > high_score:
                high_score = score
                high_k = k
    return int(high_k)

# Problem 4
def save_clustering_results(labels, filename):
    """Saves the clustering results to a CSV file.
    Parameters: labels (list): Predicted cluster labels
    filename (str): Name of the output CSV file
    Returns: CSV file """
    with open(filename, "w") as f:
        f.write("cluster_label\n")
        for label in labels:
            f.write(f"{label}\n")

def main():
    data = load_iris()
    X = data.data.tolist()

    # Running Problem 1
    kmeans_labels = perform_kmeans(X, 3)
    print(kmeans_labels)

    # Running Problem 2
    hierarchical_labels = perform_hierarchical(X, 3)
    print(hierarchical_labels)

    # Running Problem 3
    optimal_k = find_optimal_clusters(X, 'kmeans', 5)
    print(f"Optimal number of clusters using kmeans: {optimal_k}")

    # Running Problem 4
    kmeans_labels = perform_kmeans(X, optimal_k)
    save_clustering_results(kmeans_labels, "kmeans_results.csv")

if __name__ == '__main__':
    main()
