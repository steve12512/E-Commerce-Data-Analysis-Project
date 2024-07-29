import pandas as pd
import numpy as np


def read_files():
    # This function reads our xlsx files and saves them as dataframe objects
    dataframe1 = read_df1()
    dataframe2 = read_df2()
    return dataframe1, dataframe2

def read_df1():
    sheets_dict = pd.read_excel('unimportant/Booking Stats.xlsx', sheet_name=None)
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
    
    #remove listings where both retail and net price are null
    combined_df = combined_df.dropna(subset=['retail_price', 'net_price'], how='all')

    #add ticket price
    combined_df = merge_with_prices(combined_df)

    #combined_df.drop_duplicates()
    return combined_df


def merge_with_prices(df):
    #add a ticket price to each listing, based on the month and the product code we have
    price_df = pd.read_excel('unimportant/Booking Stats.xlsx', sheet_name= 'Codes & Prices')

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


    #rename columns in unpivoted_df to match df
    unpivoted_df.rename(columns={'Product Code': 'product_code'}, inplace=True)

    #remove language shortcuts and '_'s in both dataframes, so that their product codes match
    unpivoted_df['split_product_code'] = unpivoted_df['product_code'].apply(strip_language_code)
    #df['product_code'] = df['product_code'].str.replace(r"_.*|([A-Z]{2})$", "", regex=True)

    #rename the df's column Product Code so that it matches merged_df's column
    df.rename(columns= {'product_code': 'split_product_code'}, inplace = True)

    #now finally add the price of the product to dataframe1
    merged_df = pd.merge(df, unpivoted_df, on=['split_product_code', 'month'], how='left')

    # Rename the 'Price' column to 'Ticket Price'
    merged_df.rename(columns={'Price': 'Ticket Price'}, inplace=True)
    

    price_df.to_excel('unimportant/price.xlsx', index= False)
    unpivoted_df.to_excel('unimportant/unpivoted.xlsx', index= False)
    
    #that logic will not work for all listings. so for the listings that are still null, work in a different way
    #find the rows for which Ticket Price is null. then, for these rows, take their product code as a string and find the first ticket dataframe listing that has a product code column that matches that string.
    null_price_rows = merged_df['Ticket Price'].isnull()
    merged_df['Ticket Price'] = merged_df['Ticket Price'].astype(str)

    print(merged_df.dtypes)
    #keep a variable to count the execution of the lambda function. if we are on the first, keep track of the month. if we are on the second, use the price of another month(considering it is the same)
    count = 0
    merged_df.loc[null_price_rows, 'Ticket Price'] = merged_df.loc[null_price_rows].apply(
    lambda row: search_in_string(row, unpivoted_df), axis=1)

    #increment the count variable, and execute the lambda function again, this time not caring about the month(since for the corresponding month, no price was found, and we take it that it its price is approximate to one of its neighbours)
    count +=1
    


    #add a column representing the profit per tour
    #merged_df['Profit'] = merged_df[]

    return merged_df



def strip_language_code(code):
    #modify the dataset so as to remove '_', and Language shortcuts, in order to properly map product codes to corresponding ticket prices from different excel sheets saved as different dataframes.
    
    languages = ['GR', 'EN', 'FR', 'DE', 'IT', 'ES']

    if '_'  in code:
        return code.split('_')[0]


    if code[-2:] in languages:
        return code[:-2]
        
    return code


def search_in_string(row, unpivoted_df):
    #search for the string within the strings of the column product code, in the prices dataframe
    #save the product code and the month that are our keys.
    key = row['product_code']
    month = row['month']
    
    filtered_df = unpivoted_df[(unpivoted_df['product_code'] == key) & (unpivoted_df['month'] == month)]


    if not filtered_df.empty:
        # If there's a match, return the first price
        return filtered_df['Price'].iloc[0]
    else:
        return np.nan




def read_df2():
    #reads the second dataframe, df2, which contains the reviews

    sheets = pd.read_excel('unimportant/reviews data.xlsx', sheet_name=None)

    dataframes = []

    #iterate over the sheets, create a new column, and then append them to the bigger dataframe
    for sheet_name, df in sheets.items():
        df['month'] = sheet_name
        dataframes.append(df)

    dataframe2 = pd.concat(dataframes, ignore_index=True)
    dataframe2.rename(columns = {'Unnamed: 3' : 'Reviews'}, inplace= True)
    dataframe2[['Product Code', 'Name of Product']] = dataframe2['Unnamed: 1'].str.split('|', expand=True)
    return dataframe2


def successful_tour_looks_like():
    #how does a sucessful tour look like? to begin with, keep a copy of dataframe1
    df = dataframe1.copy()










    return None




def save_to_excel(dataframe1, dataframe2):
    dataframe1.to_excel('dataframe1.xlsx', index=False)
    dataframe2.to_excel('dataframe2.xlsx', index=False)

# START
# From here and on, our script starts executing
dataframe1, dataframe2 = read_files()
save_to_excel(dataframe1, dataframe2)

#how does a successful tour look like?
successful_tour_looks_like()