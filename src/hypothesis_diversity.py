import pandas as pd
import numpy as np
from math import radians, sin, cos, sqrt, atan2
from scipy import stats
import matplotlib.pyplot as plt

import shared

folder = "data/"
filename = "CityofBoston-CityClerkDBA_cleaned.csv"
plots_folder = "eda_plots/"

TODAY          = pd.Timestamp("2026-03-31")
RADIUS         = 0.10
BINS           = [-1, 0.5, 1.5, float("inf")]
LABELS         = ["Low", "Medium", "High"]
DAY_INTERVALS = [1400, 2800, 4200]

# Load & prepare data
df = pd.read_csv(folder + filename, dtype={"Zipcode": str})

df[["Date of Filing", "Date of Expiration"]] = df[["Date of Filing", "Date of Expiration"]].apply(pd.to_datetime, errors="coerce")
df = df.dropna(subset=["Date of Filing", "Date of Expiration"])

df["Closed"]   = (df["Date of Expiration"] < TODAY).astype(int)
df["age"] = np.where(df["Closed"],
                           (df["Date of Expiration"] - df["Date of Filing"]).dt.days,
                           (TODAY - df["Date of Filing"]).dt.days)
df = df[df["age"] > 0]

# Diversity score functions 
def haversine_distance(lat1, lon1, lat2, lon2):
    '''
    Haversine captures a circle; Manhattan gives a diamond/square. 
    For diversity scoring this probably doesn't matter much. Use Manhattan distance.
    '''
    R = 3958.8
    lat1, lon1 = radians(lat1), radians(lon1)
    lat2 = np.radians(lat2)
    lon2 = np.radians(lon2)
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = np.sin(dlat/2)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon/2)**2
    return R * 2 * np.arctan2(np.sqrt(a), np.sqrt(1 - a))

def neighborhood_diversity_score(types):
    counts = types.value_counts()
    proportions = counts / counts.sum()
    return -sum(proportions * np.log(proportions))

def get_diversity_score(df, idx, radius_miles=RADIUS):
    '''
    Calculate a diversity score for each business based on nearby businesses.
    '''
    row    = df.loc[idx]
    lat_miles = 69.0        # degrees lat per mile
    lon_miles = 52.0        # degrees lon per mile at Boston's latitude

    dist = haversine_distance(row["latitude"], row["longitude"],
                                df["latitude"], df["longitude"] )
    nearby = df[(dist <= radius_miles) & (df.index != idx)]

    if len(nearby) < 2:
        return 0.0
    return neighborhood_diversity_score(nearby["Type of Business"])

def plot_diversity_vs_age(df):
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))

    # Scatter: raw diversity score vs age
    axes[0].scatter(df["Diversity Score"], df["age"], alpha=0.3, s=10)
    axes[0].set_xlabel("Diversity Score")
    axes[0].set_ylabel("Age (days)")
    axes[0].set_title("Diversity Score vs Business Age")

    # Line: mean age per diversity level
    means = df.groupby("Diversity Level", observed=True)["age"].mean()
    axes[1].plot(means.index, means.values, marker="o")
    axes[1].set_xlabel("Diversity Level")
    axes[1].set_ylabel("Mean Age (days)")
    axes[1].set_title("Mean Business Age by Diversity Level")

    plt.tight_layout()
    plt.savefig(plots_folder + "diversity_vs_age.png")
    plt.show()

# Build heatmap matrix 
def build_heatmap(df):
    heatmap_data = np.zeros((len(LABELS), len(DAY_INTERVALS)))
    for i, level in enumerate(LABELS):
        subset = df[df["Diversity Level"] == level]
        for j, day in enumerate(DAY_INTERVALS):
            if len(subset) == 0:
                heatmap_data[i, j] = np.nan
            else:
                still_open_at_day = subset[
                    ((subset["age"] >= day) & (subset["Closed"] == 0)) |
                    ((subset["age"] >  day) & (subset["Closed"] == 1))
                ]
                heatmap_data[i, j] = round(len(still_open_at_day) / len(subset), 2)
    return heatmap_data

# Plot heatmap
def plot_heatmap(heatmap_data):
    fig, ax = plt.subplots(figsize=(8, 5))
    im = ax.imshow(heatmap_data, cmap="RdYlGn", vmin=-1, vmax=1, aspect="auto")

    cbar = plt.colorbar(im, ax=ax)
    cbar.set_label("Survival Probability")
    cbar.set_ticks(np.arange(-1, 1.25, 0.25))

    ax.set_xticks(range(len(DAY_INTERVALS)))
    ax.set_xticklabels([f"{d:,}" for d in DAY_INTERVALS])
    ax.set_yticks(range(len(LABELS)))
    ax.set_yticklabels(LABELS)
    ax.set_xlabel("Days Since Opening")
    ax.set_ylabel("Diversity Level")
    ax.set_title("Survival Probability by Diversity Level and Days Since Opening")

    for i in range(len(LABELS)):
        for j in range(len(DAY_INTERVALS)):
            val  = heatmap_data[i, j]
            text = f"{val:.2f}" if not np.isnan(val) else "N/A"
            ax.text(j, i, text, ha="center", va="center",
                    fontsize=12, color="black", fontweight="bold")

    plt.tight_layout()
    plt.savefig(plots_folder + "survival_heatmap.png")
    plt.show()

def plot_btype_heatmap(df):
    categories = sorted(df["business_category"].unique())
    levels = ["Low", "Medium", "High"]

    fig, axes = plt.subplots(1, len(DAY_INTERVALS),
                             figsize=(6 * len(DAY_INTERVALS), 6))

    for ax, day in zip(axes, DAY_INTERVALS):
        heatmap_data = np.zeros((len(categories), len(levels)))

        for i, cat in enumerate(categories):
            for j, level in enumerate(levels):
                subset = df[
                    (df["business_category"] == cat) &
                    (df["Diversity Level"] == level)
                ]
                if len(subset) == 0:
                    heatmap_data[i, j] = np.nan
                else:
                    still_open = subset[
                        ((subset["age"] >= day) & (subset["Closed"] == 0)) |
                        ((subset["age"] >  day) & (subset["Closed"] == 1))
                    ]
                    heatmap_data[i, j] = round(
                        len(still_open) / len(subset), 2
                    )

        im = ax.imshow(heatmap_data, cmap="RdYlGn",
                       vmin=0, vmax=1, aspect="auto")
        plt.colorbar(im, ax=ax).set_label("Survival Probability")

        ax.set_xticks(range(len(levels)))
        ax.set_xticklabels(levels)
        ax.set_yticks(range(len(categories)))
        ax.set_yticklabels(categories)
        ax.set_xlabel("Diversity Level")
        ax.set_ylabel("Business Type")
        ax.set_title(f"Survival Probability at Day {day:,}")

        for i in range(len(categories)):
            for j in range(len(levels)):
                val = heatmap_data[i, j]
                text = f"{val:.2f}" if not np.isnan(val) else "N/A"
                ax.text(j, i, text, ha="center", va="center",
                        fontsize=10, color="black", fontweight="bold")

    plt.tight_layout()
    plt.savefig(plots_folder + "btype_survival_heatmap.png")
    plt.show()

def plot_kaplan_meier(df):
    fig, ax = plt.subplots(figsize=(10, 6))

    colors = {"Low": "blue", "Medium": "orange", "High": "green"}

    for level in ["Low", "Medium", "High"]:
        subset = df[df["Diversity Level"] == level].copy()
        subset = subset.sort_values("age")
        
        total = len(subset)
        survival = []
        for day in subset["age"]:
            still_open = len(subset[
                ((subset["age"] >= day) & (subset["Closed"] == 0)) |
                ((subset["age"] >  day) & (subset["Closed"] == 1))
            ])
            survival.append(still_open / total)

        ax.plot(subset["age"], survival,
                label=f"{level} Diversity",
                color=colors[level])

    ax.set_xlabel("Days Since Opening")
    ax.set_ylabel("Survival Probability")
    ax.set_title("Business Survival by Nearby Business Diversity")
    ax.legend()
    plt.tight_layout()
    plt.savefig(plots_folder + "kaplan_meier.png")
    plt.show()

def plot_neighbor_heatmap(df):
    categories = sorted(df["business_category"].unique())
    labels = ["Isolated", "Clustered"]
    heatmap_data = np.zeros((len(categories), 2))
    count_data = np.zeros((len(categories), 2), dtype=int)

    for i, btype in enumerate(categories):
        for j, clustered in enumerate([0, 1]):
            subset = df[
                (df["business_category"] == btype) &
                (df["same_type_nearby"] == clustered)
            ]
            count_data[i, j] = len(subset)
            if len(subset) == 0:
                heatmap_data[i, j] = np.nan
            else:
                heatmap_data[i, j] = round(
                    len(subset[subset["Closed"] == 0]) / len(subset), 2
                )

    fig, ax = plt.subplots(figsize=(6, 8))
    im = ax.imshow(heatmap_data, cmap="RdYlGn", vmin=0, vmax=1, aspect="auto")
    plt.colorbar(im, ax=ax).set_label("Survival Probability")

    ax.set_xticks(range(2))
    ax.set_xticklabels(labels)
    ax.set_yticks(range(len(categories)))
    ax.set_yticklabels(categories)
    ax.set_xlabel("Same Type Nearby")
    ax.set_ylabel("Business Type")
    ax.set_title("Survival Probability: Isolated vs Clustered")

    for i in range(len(categories)):
        for j in range(2):
            val = heatmap_data[i, j]
            count = count_data[i, j]
            prob = f"{val:.2f}" if not np.isnan(val) else "N/A"
            ax.text(j, i, f"{prob}\n(n={count})", ha="center", va="center",
                    fontsize=9, color="black", fontweight="bold")

    plt.tight_layout()
    plt.savefig(plots_folder + "neighbor_heatmap.png")
    plt.show()

# Same Type Nearby
def get_same_type_nearby(df, idx, radius_miles=RADIUS):
    row = df.loc[idx]
    lat1, lon1 = radians(row["latitude"]), radians(row["longitude"])
    lat2 = np.radians(df["latitude"])
    lon2 = np.radians(df["longitude"])
    dlat, dlon = lat2 - lat1, lon2 - lon1
    a = np.sin(dlat/2)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon/2)**2
    dist = 3958.8 * 2 * np.arctan2(np.sqrt(a), np.sqrt(1 - a))
    nearby = df[(dist <= radius_miles) & (df.index != idx)]
    return int(any(nearby["business_category"] == row["business_category"]))

# Main 
def main():
    df["business_category"] = df["Type of Business"].apply(shared.categorize_business_type)
    df.drop(df[df["business_category"] == "Other"].index, inplace=True)

    # Diversity scores
    df["Diversity Score"] = [get_diversity_score(df, i) for i in df.index]
    df["Diversity Level"] = pd.qcut(df["Diversity Score"], q=3, labels=LABELS)
    df["same_type_nearby"] = [get_same_type_nearby(df, i) for i in df.index]

    print("\nBusiness counts by category:")
    print(df["business_category"].value_counts().to_string())
    
    plot_kaplan_meier(df)
    plot_btype_heatmap(df)
    plot_neighbor_heatmap(df)
    plot_diversity_vs_age(df)
    # Heatmap
    heatmap_data = build_heatmap(df)
    print("\nHeatmap Values:")
    heatmap_df = pd.DataFrame(heatmap_data, index=LABELS,
                               columns=[f"Day {d:,}" for d in DAY_INTERVALS])
    print(heatmap_df.to_string())
    plot_heatmap(heatmap_data)
    
    groups = [df[df["Diversity Level"] == lvl]["age"].dropna() for lvl in LABELS]
    f_stat, p_value = stats.f_oneway(*groups)
 
    corr, pval = stats.pearsonr(df["Diversity Score"], df["age"])

    print(df["Diversity Level"].value_counts())
    print(df["Diversity Score"].describe())
    print(df["Diversity Score"].value_counts().head(20))
    # Save
    #df.to_csv(folder + "CityofBoston-CityClerkDBA_hypothesis_diversity.csv", index=False)

if __name__ == "__main__":
    main()
