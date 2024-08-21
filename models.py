import pandas as pd
from mlxtend.frequent_patterns import apriori, association_rules

def find_frequent_product_combinations(df, min_support=0.01, min_confidence=0.5):
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

    return frequent_itemsets, rules