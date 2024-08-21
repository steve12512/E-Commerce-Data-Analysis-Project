import pandas as pd
from mlxtend.frequent_patterns import apriori, association_rules


def prepare_data_for_association_rules(df1):
    # Expand the list of product combinations into separate columns
    
    df_expanded = df1.explode('product_code')

    # One-hot encode the product combinations
    df_encoded = pd.get_dummies(df_expanded['product_combinations'])
    
    # Aggregate by id (assuming 'id' represents a unique booking or transaction)
    df_encoded = df_encoded.groupby(df['id']).max()

    return df_encoded