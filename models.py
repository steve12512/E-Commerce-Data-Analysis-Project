import pandas as pd
from mlxtend.frequent_patterns import apriori, association_rules
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import matplotlib.pyplot as plt
import seaborn as sns

def find_frequent_product_combinations(df, dictionary, min_support=0.01, min_confidence=0.5):
    """
    Find frequent product combinations and generate association rules.

    Parameters:
    df (pd.DataFrame): The input dataframe containing product combinations.
    min_support (float): The minimum support threshold for the Apriori algorithm.
    min_confidence (float): The minimum confidence threshold for the association rules.

    Returns:
    pd.DataFrame: A dataframe containing the frequent itemsets and association rules.
    """
    # Prepare the data
    df['product_combinations'] = df['product_code'].apply(lambda x: x.split('_'))
    df_expanded = df.explode('product_combinations')
    df_encoded = pd.get_dummies(df_expanded['product_combinations'])
    df_encoded = df_encoded.groupby(df['id']).max()

    # Apply the Apriori algorithm
    frequent_itemsets = apriori(df_encoded, min_support=min_support, use_colnames=True)
    frequent_itemsets = frequent_itemsets.sort_values(by='support', ascending=False)

    # Generate association rules
    rules = association_rules(frequent_itemsets, metric="confidence", min_threshold=min_confidence)
    rules = rules.sort_values(by='confidence', ascending=False)
    
    frequent_itemsets['itemsets'] = frequent_itemsets['itemsets'].apply(lambda x: frozenset([dictionary[code] for code in x]))
    rules['antecedents'] = rules['antecedents'].apply(lambda x: frozenset([dictionary[code] for code in x]))
    rules['consequents'] = rules['consequents'].apply(lambda x: frozenset([dictionary[code] for code in x]))
    return frequent_itemsets, rules



def associate_together(df1, dictionary):
    # This function attempts to find which tours go together by using association rules
    df1_copy = df1.copy()  # Copy our version of dataframe1

    # Initialize a dictionary to store results for each country
    results = {}

    # Group by country and process each group
    for country, group in df1_copy.groupby('Country'):
        frequent_itemsets, rules = find_frequent_product_combinations(group, dictionary)
        results[country] = {'frequent_itemsets': frequent_itemsets, 'rules': rules}

    # Optionally, save results to files
    for country, result in results.items():
        result['frequent_itemsets'].to_csv(f'associations/{country}_frequent_itemsets.csv', index=False)
        result['rules'].to_csv(f'associations/{country}_association_rules.csv', index=False)

    # Or display the results for inspection
    for country, result in results.items():
        print(f"Country: {country}")
        print("Frequent Itemsets:")
        print(result['frequent_itemsets'])
        print("Association Rules:")
        print(result['rules'])

    return results


import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import matplotlib.pyplot as plt
import seaborn as sns

def clusters(df):
    countries = ['Greece', 'Portugal', 'Italy', 'Spain']
    
    for country in countries:
        # Step 1: Filter the data for each country
        country_df = df[df['Country'] == country].copy()

        # Step 2: Select relevant features for clustering
        features = ['num_of_travellers', 'Profit', 'retail_price']  # Add more features if needed
        X = country_df[features]

        # Step 3: Standardize the features
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)

        # Step 4: Use the elbow method to find the optimal number of clusters
        wcss = []  # Within-cluster sum of squares
        for i in range(1, 11):
            kmeans = KMeans(n_clusters=i, random_state=42)
            kmeans.fit(X_scaled)
            wcss.append(kmeans.inertia_)

        # Plot the elbow graph for each country
        plt.figure(figsize=(10, 6))
        plt.plot(range(1, 11), wcss, marker='o', linestyle='--')
        plt.title(f'Elbow Method for Optimal Number of Clusters for {country}')
        plt.xlabel('Number of Clusters')
        plt.ylabel('WCSS')
        plt.show()

        # Step 5: Fit the KMeans model with the optimal number of clusters (e.g., k=3)
        optimal_clusters = 3  # Replace with the chosen number from the elbow method if different
        kmeans = KMeans(n_clusters=optimal_clusters, random_state=42)
        country_df['Cluster'] = kmeans.fit_predict(X_scaled)

        # Step 6: Analyze and visualize the clusters
        plt.figure(figsize=(12, 6))
        sns.scatterplot(data=country_df, x='num_of_travellers', y='Profit', hue='Cluster', palette='viridis', s=100)
        plt.title(f'Clusters of Listings in {country}')
        plt.xlabel('Number of Travellers')
        plt.ylabel('Profit')
        plt.legend(title='Cluster')
        plt.show()

        # Optional: Save the clustered data
        country_df.to_csv(f'clusters/{country.lower()}_clustered_listings.csv', index=False)
        
        # Cluster summary
        cluster_summary = country_df.groupby('Cluster').agg(
            avg_num_of_travellers=('num_of_travellers', 'mean'),
            total_travellers=('num_of_travellers', 'sum'),
            avg_profit=('Profit', 'mean'),
            total_profit=('Profit', 'sum'),
            avg_spending=('retail_price', 'mean'),
            total_spending=('retail_price', 'sum'),
            most_common_tours=('product_code', lambda x: x.mode().iloc[0]),  # Most frequently booked tour
            most_common_travel_day=('travel_day', lambda x: x.mode().iloc[0]),  # Most common travel day
            count_listings=('product_code', 'size')  # Number of listings in the cluster
        ).reset_index()

        # Step 3: Display the cluster summary
        print(f"Cluster Summary for {country}:")
        print(cluster_summary)

        # Optional: Save the summary to a CSV file for further analysis
        cluster_summary.to_csv(f'clusters/{country.lower()}_cluster_summary.csv', index=False)

