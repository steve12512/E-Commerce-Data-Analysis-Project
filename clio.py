import pandas as pd

def read_files():
    # This function reads our xlsx files and saves them as dataframe objects
    dataframe1 = read_df1()
    dataframe2 = read_df2()
    return dataframe1, dataframe2

def read_df1():
    sheets_dict = pd.read_excel('Booking Stats.xlsx', sheet_name=None)
    codes_prices_df = sheets_dict['Codes & Prices']

    # Initialize an empty list to store DataFrames
    df_list = []
    
    # List of valid months
    valid_months = ["January", "February", "March", "April", "May", "June",
                    "July", "August", "September", "October", "November", "December"]
    
    # Loop through each sheet
    for sheet_name, df in sheets_dict.items():
        if sheet_name in valid_months:
            # Add a column for the month
            df['month'] = sheet_name
            # Append the DataFrame to the list
            df_list.append(df)
    
    # Concatenate all DataFrames into a single DataFrame
    combined_df = pd.concat(df_list, ignore_index=True)
    combined_df = merge_with_prices(combined_df)


    return combined_df


def merge_with_prices(df):
    #add a price to each listing, based on the month and the product code we have
    price_df = pd.read_excel('Booking Stats.xlsx', sheet_name= 'Codes & Prices')
    print(price_df.columns)

    #map shortcuts to full month names
    month_mapping = {
    'January': 'Jan', 'February': 'Feb', 'March': 'Mar', 'April': 'Apr',
    'May': 'May', 'June': 'Jun', 'July': 'Jul', 'August': 'Aug',
    'September': 'Sept', 'October': 'Oct', 'November': 'Nov', 'December': 'Dec'
}
    #and the reverse
    reverse_month_mapping = {v: k for k, v in month_mapping.items()}



    #unpivot the dataframe to create more discrete listings depending on the month and the country of the product
    unpivoted_df = pd.melt(price_df, id_vars=['Product Code', 'Unnamed: 1', 'Country'], 
                       value_vars=month_mapping.values(), 
                       var_name='month', value_name='Price')

    #map month shortcuts to full month names
    unpivoted_df['month'] = unpivoted_df['month'].map(reverse_month_mapping)


    #now finally add the price of the product to dataframe1
    if df['month'] == unpivoted_df['month'] and df['product_code'] == unpivoted_df['Product Code']:
        df['Ticket Cost'] = unpivoted_df['Price']





    price_df.to_excel('price.xlsx', index= False)
    unpivoted_df.to_excel('unpivoted.xlsx', index= False)









    return df










def read_df2():

    dataframe2 = pd.read_excel('reviews data.xlsx')
    return dataframe2










def save_to_excel(dataframe1, dataframe2):
    dataframe1.to_excel('dataframe1.xlsx', index=False)
    dataframe2.to_excel('dataframe2.xlsx', index=False)

# START
# From here and on, our script starts executing
dataframe1, dataframe2 = read_files()
save_to_excel(dataframe1, dataframe2)