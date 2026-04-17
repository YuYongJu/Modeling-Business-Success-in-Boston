import matplotlib.pyplot as plt
import preprocessing
import pandas as pd
import shared

save_location = 'eda_plots/'

def plot_coords(businesses_df, stops_df):
    """
    Plot business and MBTA stop locations.
    Businesses in blue, stops in red.
    """
    plt.figure(figsize=(10, 10))

    plt.scatter(
        businesses_df["longitude"], businesses_df["latitude"],
        c="blue", s=5, alpha=0.5, label="Businesses"
    )
    plt.scatter(
        stops_df["longitude"], stops_df["latitude"],
        c="red", s=20, alpha=0.8, label="MBTA Stops"
    )

    plt.xlabel("Longitude")
    plt.ylabel("Latitude")
    plt.title("Boston Businesses and MBTA Stops")
    plt.legend()
    plt.tight_layout()
    plt.xlim(-71.2, -70.9)
    plt.ylim(42.2, 42.4)
    plt.savefig(save_location + "boston_map.png", dpi=150)
    plt.show()

def plot_age_vs_transit(df):
    plt.figure(figsize=(8, 5))
    plt.scatter(
        df['distance_to_closest_stop'] / 1000,
        df['age_years'],
        alpha=0.3, s=10, color='steelblue'
    )
    plt.xlabel('Distance to Nearest MBTA Stop (km)')
    plt.ylabel('Business Age (years)')
    plt.title('Business Age vs. Distance to Transit')
    plt.tight_layout()
    plt.xlim(0, 5)
    plt.savefig(save_location + 'age_vs_transit_distance.png')
    plt.show()

def plot_chains_by_neighborhood(df):
    df = df.copy()
    total_by_neighborhood = df.groupby('neighborhood').size()
    
    df = df[df['chain_count'] > 1]
    df['chain_category'] = pd.cut(
        df['chain_count'],
        bins=[1, 4, float('inf')],
        labels=['Small Chain (2-4)', 'Large Chain (5+)']
    )

    grouped = df.groupby(['neighborhood', 'chain_category']).size().unstack(fill_value=0)
    grouped = grouped.div(total_by_neighborhood, axis=0) * 100
    grouped['total'] = grouped.sum(axis=1)
    grouped = grouped.sort_values('total').drop(columns='total')

    plt.figure(figsize=(12, 5))
    grouped.plot(
        kind='bar',
        stacked=True,
        color=['orange', 'red'],
        figsize=(12, 5)
    )
    plt.title('Chain Businesses as % of Total by Neighborhood')
    plt.xlabel('Neighborhood')
    plt.ylabel('% of Total Businesses')
    plt.xticks(rotation=45, ha='right')
    plt.legend(title='Chain Category')
    plt.tight_layout()
    plt.savefig(save_location + 'chains_by_neighborhood.png')
    plt.show()

def plot_chain_vs_longevity(df):
    df = df.copy()
    df['chain_category'] = pd.cut(
        df['chain_count'],
        bins=[0, 1, 4, float('inf')],
        labels=['Independent', 'Small Chain (2-4)', 'Large Chain (5+)']
    )

    groups = ['Independent', 'Small Chain (2-4)', 'Large Chain (5+)']
    data = [
        df.loc[df['chain_category'] == g, 'age_years'].dropna().values
        for g in groups
    ]

    fig, ax = plt.subplots(figsize=(8, 5))

    bp = ax.boxplot(
        data,
        tick_labels=groups,
        patch_artist=True,
        medianprops=dict(color='red', linewidth=2.5),
        boxprops=dict(color='black', linewidth=1.8),
        whiskerprops=dict(color='black', linewidth=1.6),
        capprops=dict(color='black', linewidth=2.0),
        flierprops=dict(
            marker='o', markerfacecolor='red',
            markeredgecolor='black', markersize=5
        ),
        widths=0.5
    )

    box_colors = ['#a8c4e0', '#b5d8b5', '#f4c97a']
    for patch, color in zip(bp['boxes'], box_colors):
        patch.set_facecolor(color)

    ax.set_title(
        'Business Longevity by Chain Status',
        fontsize=13, color='black', pad=12
    )
    ax.set_xlabel('Chain Category', fontsize=11, color='black', labelpad=8)
    ax.set_ylabel('Age (years)', fontsize=11, color='black', labelpad=8)
    ax.tick_params(colors='black', labelsize=10)
    ax.yaxis.grid(True, color='lightgray', linewidth=0.8, zorder=0)

    for spine in ax.spines.values():
        spine.set_edgecolor('black')
        spine.set_linewidth(1.2)

    plt.tight_layout()
    plt.savefig(save_location + 'chain_vs_longevity.png', dpi=150)
    plt.show()

def plot_age_by_neighborhood(df):
    current_year = 2026
    global_mode = 4
    ref_year = current_year - global_mode

    order = (
        df.groupby('neighborhood')['age_years']
        .median()
        .sort_values()
        .index
    )
    df['neighborhood'] = pd.Categorical(
        df['neighborhood'], categories=order, ordered=True
    )
    df = df.sort_values('neighborhood')

    fig, ax = plt.subplots(figsize=(10, 7))

    # Narrower boxes via widths parameter
    df.boxplot(
        column='age_years',
        by='neighborhood',
        grid=False,
        ax=ax,
        boxprops=dict(color='black', linewidth=1.5),
        whiskerprops=dict(color='black', linewidth=1.5),
        capprops=dict(color='black', linewidth=1.5),
        medianprops=dict(color='red', linewidth=2.5),
        showmeans=False
    )

    # Titles and labels with large font
    ax.set_title('Business Age by Neighborhood', fontsize=20, pad=15)
    plt.suptitle('')
    ax.set_xlabel('Neighborhood', fontsize=16)
    ax.set_ylabel('Year Registered', fontsize=16)
    plt.xticks(rotation=45, ha='right', fontsize=14)
    plt.yticks(fontsize=14)

    # Border
    for spine in ax.spines.values():
        spine.set_visible(True)
        spine.set_edgecolor('black')
        spine.set_linewidth(1.5)

    # Global mean reference line
    ax.axhline(
        y=global_mode,
        color='steelblue',
        linestyle='--',
        linewidth=2,
        zorder=5
    )
    ax.text(
        len(order) + 0.6, global_mode,
        f'Mode: {global_mode} years',
        va='center', ha='left', fontsize=13, color='steelblue',
        bbox=dict(boxstyle='round', facecolor='white',
                  edgecolor='steelblue', linewidth=1.5, alpha=0.9)
    )

    plt.tight_layout()
    plt.savefig(
        save_location + 'age_by_neighborhood.png',
        dpi=150, bbox_inches='tight'
    )
    plt.show()

def plot_active_by_neighborhood(df):
    grouped = df.groupby(['neighborhood', 'is_active']).size().unstack(fill_value=0)
    grouped.columns = ['Inactive', 'Active']
    grouped['total'] = grouped['Active'] + grouped['Inactive']
    grouped['pct_active'] = grouped['Active'] / grouped['total'] * 100
    grouped['pct_inactive'] = grouped['Inactive'] / grouped['total'] * 100
    grouped = grouped.sort_values('pct_active')

    fig, ax = plt.subplots(figsize=(14, 6))
    grouped[['pct_inactive', 'pct_active']].plot(
        kind='bar', stacked=True, color=['red', 'steelblue'], ax=ax
    )

    for i, (_, row) in enumerate(grouped.iterrows()):
        if row['pct_inactive'] > 5:
            ax.text(i, row['pct_inactive'] / 2,
                f"{row['pct_inactive']:.1f}%",
                ha='center', va='center', fontsize=12, fontweight='bold')

        if row['pct_active'] > 5:
            ax.text(i, row['pct_inactive'] + row['pct_active'] / 2,
                    f"{row['pct_active']:.1f}%",
                    ha='center', va='center', fontsize=12, fontweight='bold')

    
    plt.title('Active vs Inactive Businesses by Neighborhood')
    plt.xlabel('Neighborhood')
    plt.ylabel('% of Businesses')
    plt.xticks(rotation=45, ha='right')
    plt.legend(title='Status', bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.tight_layout()
    plt.savefig(save_location + 'active_by_neighborhood.png', dpi=150)
    plt.show()

def main():
    plt.rcParams.update({'font.size': 14})
    df = pd.read_csv('data/compiled_data.csv')
    stops_df = pd.read_csv('data/MBTA_stops.csv')
    plot_coords(df, stops_df)
    plot_age_vs_transit(df)
    plot_chains_by_neighborhood(df)
    plot_chain_vs_longevity(df)
    plot_age_by_neighborhood(df)
    plot_active_by_neighborhood(df)

if __name__ == '__main__':
    main()