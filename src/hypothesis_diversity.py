import pandas as pd
import numpy as np
from math import radians, sin, cos, sqrt, atan2
from scipy import stats
import matplotlib.pyplot as plt

folder = "/Users/tulahionas/Spring_2026_DS_2500/Final_Project/"
filename = "CityofBoston-CityClerkDBA_cleaned.csv"

TODAY          = pd.Timestamp("2026-03-31")
RADIUS         = 0.25
BINS           = [-1, 0.5, 1.5, float("inf")]
LABELS         = ["Low", "Medium", "High"]
DAY_INTERVALS  = [1000, 2500, 4000]

# Load & prepare data
df = pd.read_csv(folder + filename, dtype={"Zipcode": str})

df[["Date of Filing", "Date of Expiration"]] = df[["Date of Filing", "Date of Expiration"]].apply(pd.to_datetime, errors="coerce")
df = df.dropna(subset=["Date of Filing", "Date of Expiration"])

df["Closed"]   = (df["Date of Expiration"] < TODAY).astype(int)
df["Duration"] = np.where(df["Closed"],
                           (df["Date of Expiration"] - df["Date of Filing"]).dt.days,
                           (TODAY - df["Date of Filing"]).dt.days)
df = df[df["Duration"] > 0]

# Diversity score functions 
def distance_in_miles(lat1, lon1, lat2, lon2):
    R = 3958.8
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlat, dlon = lat2 - lat1, lon2 - lon1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    return R * 2 * atan2(sqrt(a), sqrt(1 - a))

def neighborhood_diversity_score(types):
    counts = types.value_counts()
    proportions = counts / counts.sum()
    return -sum(proportions * np.log(proportions))

def get_diversity_score(idx, radius_miles=RADIUS):
    row    = df.loc[idx]
    nearby = df[df.index != idx].copy()
    nearby["dist"] = nearby.apply(
        lambda r: distance_in_miles(row["Latitude"], row["Longitude"],
                            r["Latitude"],  r["Longitude"]), axis=1)
    nearby = nearby[nearby["dist"] <= radius_miles]
    if len(nearby) < 2:
        return 0.0
    return neighborhood_diversity_score(nearby["Type of Business"])

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
                    ((subset["Duration"] >= day) & (subset["Closed"] == 0)) |
                    ((subset["Duration"] >  day) & (subset["Closed"] == 1))
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
    plt.savefig(folder + "survival_heatmap.png")
    plt.show()

# Main 
def main():
    # Diversity scores
    df["Diversity Score"] = [get_diversity_score(i) for i in df.index]
    df["Diversity Level"] = pd.cut(df["Diversity Score"], bins=BINS, labels=LABELS)

    # Heatmap
    heatmap_data = build_heatmap(df)
    print("\nHeatmap Values:")
    heatmap_df = pd.DataFrame(heatmap_data, index=LABELS,
                               columns=[f"Day {d:,}" for d in DAY_INTERVALS])
    print(heatmap_df.to_string())
    plot_heatmap(heatmap_data)
    
    groups = [df[df["Diversity Level"] == lvl]["Duration"].dropna() for lvl in LABELS]
    f_stat, p_value = stats.f_oneway(*groups)
 
    corr, pval = stats.pearsonr(df["Diversity Score"], df["Duration"])
 
    # Save
    df.to_csv(folder + "CityofBoston-CityClerkDBA_hypothesis_diversity.csv", index=False)

if __name__ == "__main__":
    main()
