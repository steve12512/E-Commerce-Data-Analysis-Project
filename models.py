import pandas as pd
from mlxtend.frequent_patterns import apriori, association_rules

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
