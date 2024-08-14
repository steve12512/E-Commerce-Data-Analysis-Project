import pandas as pd
import numpy as np
from fuzzywuzzy import process

#this is the file that contains the functions we will be using in our script

def read_files():
    # This function reads our xlsx files and saves them as dataframe objects
    dataframe1 = read_df1()
    dataframe2 = read_df2(dataframe1) #dataframe2 needs to have access to dataframe1 for the merging of their product codes
    return dataframe1, dataframe2

def read_df1():
    sheets_dict = pd.read_excel('unimportant/Booking Stats.xlsx', sheet_name=None)
    codes_prices_df = sheets_dict['Codes & Prices']

    # Initialize an empty list to store DataFrames
    df_list = []
    
    # List of valid months
    valid_months = ["January", "February", "March", "April", "May", "June",
                    "uly", "August", "September", "October", "November", "December"]
    
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

    #drop duplicated and then change variable types to preserve memory
    combined_df = combined_df.drop_duplicates()
    combined_df = parsing_df1(combined_df)    

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
    
    #first match null values, and then remove the ones that cant be matched
    merged_df = edit_nulls(merged_df, unpivoted_df)

    #add ticket price
    merged_df = add_ticket_price(merged_df)
    
    return merged_df




def edit_nulls(merged_df, unpivoted_df):
    #match null values based on different approaches on how to match their product codes. then remove the ones that cannot be matched
    #previous logic will not work for all listings. so for the listings that are still null, work in a different way
    #find the rows for which Ticket Price is null. then, for these rows, take their product code as a string and find the first ticket dataframe listing that has a product code column that matches that string.
    merged_df['Ticket Price'] = merged_df['Ticket Price'].astype(str)


    #keep a variable to count the execution of the lambda function. if we are on the first, keep track of the month. if we are on the second, use the price of another month(considering it is the same)
    count = 0
    match_nulls(count, merged_df, unpivoted_df)
    #increment the count variable, and execute the lambda function again, this time not caring about the month(since for the corresponding month, no price was found, and we take it that it its price is approximate to one of its neighbours)
    count +=1
    match_nulls(count, merged_df, unpivoted_df)

    #convert empty strings or whitespace-only strings to NaN
    merged_df['Ticket Price'] = merged_df['Ticket Price'].astype(str).str.strip()  # Remove leading/trailing whitespace
    merged_df['Ticket Price'] = merged_df['Ticket Price'].replace('', np.nan)  # Replace empty strings with NaN

    # Remove rows with null values in specified columns
    merged_df.dropna(subset=['retail_price', 'Ticket Price'], inplace=True)
    return merged_df



def match_nulls(count, merged_df, unpivoted_df):
    #this function is called 2 times. the 1st time, it tries to find the price for listings based on their product code. the second time, it does that again with a different approach.

    null_price_rows = merged_df['Ticket Price'].isnull()
    merged_df.loc[null_price_rows, 'Ticket Price'] = merged_df.loc[null_price_rows].apply(
    lambda row: search_in_string(row, unpivoted_df, count), axis=1)



def add_ticket_price(merged_df):
    #parse data into correct form and then add a profit column to the dataframe
    # Convert to numeric, handling non-numeric values
    merged_df['Ticket Price'] = pd.to_numeric(merged_df['Ticket Price'], errors='coerce')
    merged_df['retail_price'] = pd.to_numeric(merged_df['retail_price'], errors='coerce')

    #add a column representing the profit per tour
    merged_df['Profit'] = merged_df['retail_price'] - merged_df['Ticket Price']

    #due to non consistency of the data, some columns have 0 <= profit. drop these
    merged_df = merged_df[ merged_df['Profit'] > 0]
    return merged_df


def strip_language_code(code):
    #modify the dataset so as to remove '_', and Language shortcuts, in order to properly map product codes to corresponding ticket prices from different excel sheets saved as different dataframes.
    
    languages = ['GR', 'EN', 'FR', 'DE', 'IT', 'ES']

    if '_'  in code:
        return code.split('_')[0]


    if code[-2:] in languages:
        return code[:-2]
        
    return code


def search_in_string(row, unpivoted_df, count):
    #search for the string within the strings of the column product code, in the prices dataframe
    #save the product code and the month that are our keys.
    key = row['product_code']
    month = row['month']
    
    #if we are at the 1st iteration
    if count == 0 :
        filtered_df = unpivoted_df[(unpivoted_df['product_code'] == key) & (unpivoted_df['month'] == month)]
    else:
        filtered_df = unpivoted_df[(unpivoted_df['product_code'] == key)]


    if not filtered_df.empty:
        # If there's a match, return the first price
        return filtered_df['Price'].iloc[0]
    else:
        return np.nan

def parsing_df1(combined_df):
    #this function will change the variable types of dataframe1 before saving in order to reduce the excel size.
    numeric_cols = ['seller_id', 'num_of_travellers', 'retail_price', 'net_price', 'Profit']
    combined_df[numeric_cols] = combined_df[numeric_cols].astype('float64')
    return combined_df


def read_df2(dataframe1):
    #reads the second dataframe, df2, which contains the reviews

    sheets = pd.read_excel('unimportant/reviews data.xlsx', sheet_name=None)
    dataframes = []

    #iterate over the sheets, create a new column, and then append them to the bigger dataframe
    for sheet_name, df in sheets.items():
        df['month'] = sheet_name
        dataframes.append(df)
    
    #split some columns and rename others
    dataframe2 = pd.concat(dataframes, ignore_index=True)
    dataframe2.rename(columns = {'Unnamed: 3' : 'Reviews', 'Unnamed: 1' : 'Product Code and Name', 'Unnamed2': 'Review', 'Unnamed: 6' : 'Experience'}, inplace= True)
    dataframe2[['Product Code', 'Name of Product']] = dataframe2['Product Code and Name'].str.split('|', expand=True)

    #cast as string in order to later split the product code
    dataframe2['Product Code'] = dataframe2['Product Code'].astype(str)

    #split dataframe2's product codes 
    dataframe2['split_product_code'] = dataframe2['Product Code'].apply(lambda x: x.split('_')[0])

    #create a new column for the country and the language of the listing
    dataframe2 = pd.merge(dataframe2, dataframe1[['split_product_code', 'Country', 'language']], on='split_product_code', how='left')
    dataframe2 = dataframe2.drop_duplicates()

    return dataframe2


def successful_tour_looks_like(dataframe1, dataframe2):
    #how does a sucessful tour look like? filter the listings in df1 that have a profit higher than the average. then groupby country and month, find insights about the listings with the most important being the sum of profit, and then sort them in descending order
    # to begin with, keep a copy of dataframe1
    df1 = dataframe1.copy()
    df2 = dataframe2.copy()

    #calculate the profit mean for the tours in dataframe1
    mean = df1['Profit'].mean()
    
    #filter the listings in dataframe1 that have a profit higher than the average
    df1 = df1[df1['Profit'] > mean]

    #calculate the number of products per listing
    df1['num_products'] = df1['product_code'].apply(lambda x: len(x.split('_')))

    #groupby country and month, and find the average number of travellers, the language of the product
    df1 = df1.groupby(['Country', 'month']).agg(
        average_travellers=('num_of_travellers', 'mean'), 
        Total_Travellers=('num_of_travellers', 'size'),   
        Average_number_of_products=('num_products', 'mean'),
        Total_profit = ('Profit', 'sum')
    ).reset_index()

    #keep listings that have at least 30 travellers
    df1 = df1[df1['Total_Travellers'] > 30]

    #sort values based on average profit, descending
    df1.sort_values(by = 'Total_profit', ascending = False)

    #keep the 3 most profitable listings per groupby element (we have to fit it in a presentation!!!) NOT NECESSARY STEP THOUGH
    #df1 = df1.groupby(['Country', 'month']).head(3).reset_index(drop=True)s

    df1.to_excel('questions/successful_tour_looks_like.xlsx', index = False)

    return None

def which_tours_go_together(dataframe1, dataframe2):
    #which tours go together? first make a copy of our dataframes

    df1 = dataframe1.copy()
    df2 = dataframe2.copy()

    #split product codes on _, create a new column for each combination and count the number of its occurances
    df1['product_combinations'] = df1['product_code'].apply(lambda x: tuple(sorted(x.split('_'))))
    grouped_df = df1['product_combinations'].value_counts().reset_index(name='Occurrences')
    grouped_df.columns = ['Product_Combination', 'Occurrences']

    #filter for combinations with at least 2 products
    grouped_df = grouped_df[grouped_df['Product_Combination'].apply(lambda x: len(x) > 1)]

    #store a dictionary to map product codes to their names
    code_to_tour = dict(zip(df2['split_product_code'], df2['Name of Product']))

    #for each product code in product code combination, map it to its corresponding tour name, and after having done that for all codes, concatenate the string
    grouped_df['tour_names'] = grouped_df['Product_Combination'].apply(lambda x: get_tour_names(x, code_to_tour, df2))    

    #sort the DataFrame by the number of occurrences
    grouped_df = grouped_df.sort_values(by='Occurrences', ascending=False)

    #save  to an Excel file
    grouped_df.to_excel('questions/tours_go_together.xlsx', index=False)
    return grouped_df


def get_tour_names(product_codes, code_to_tour, df2):
    #this function maps product codes to their tour names for whole packaged bought together

    tour_names = []
    for code in product_codes:
        #remove  unwanted characters
        clean_code = code.replace('(', '').replace(')', '').replace('\'', '').strip()
        if clean_code in code_to_tour:
            tour_names.append(code_to_tour[clean_code])
            continue
        else:
            #remove the last 2 letter that signify the language if they are letters  in order to get better matching
            if clean_code[-2:] in ['IT', 'FR', 'GR', 'EN', 'ES', 'CN']:
                clean_code = clean_code[:-2]

            if clean_code in code_to_tour:
                tour_names.append(code_to_tour[clean_code])    
                continue       
            else:
                #else search in a different column of dataframe2 that contains both names and codes, seperated by |
                matching_row = df2[df2['Product Code and Name'].str.contains(clean_code, na=False)]
                if not matching_row.empty:
                    tour_name = matching_row.iloc[0]['Product Code and Name'].split('|')[1].strip()
                    tour_names.append(tour_name)    
                    continue

            #fuzzy matching as a fallback if we still havent found the word
            closest_match, confidence = process.extractOne(clean_code, code_to_tour.keys())
            if confidence > 80:  # Confidence threshold for fuzzy matching
                tour_names.append(code_to_tour[closest_match])
            else:
                tour_names.append('Unknown')  # Or any other handling for unmatched codes
    return ', '.join(tour_names)

def save_to_excel(dataframe1, dataframe2):
    dataframe1.to_excel('dataframe1.xlsx', index=False)
    dataframe2.to_excel('dataframe2.xlsx', index=False)


def edit_dfs(df1, df2):
    #change the structure of dataframe1 so as to have split product code saved as a set containing all of split product codes
    df1['split_product_codes'] = df1['product_code'].apply(lambda x: set(x.split('_')))
    df2['split_product_codes'] = df2['Product Code'].apply(lambda x: set(x.split('_')))
    return df1, df2

def add_df2_profit(dataframe1, dataframe2):
    #add a profit column to df2. copy our dataframes
    
    df1 = dataframe1.copy()
    df2 = dataframe2.copy()

    #first try to search for the whole  product code
<<<<<<< HEAD
    df2['Profit'] = df1['product_code'] if df2['Product Code'] == df1['product_code'] else df2['split_product_codes'].apply(function_name)
    
=======
    df2['Profit'] = df2['split_product_codes'].apply(lambda key: codes_to_profit(key, df1, df2))




def codes_to_profit(key, df1, df2):
    # Convert key to a frozenset to handle unordered comparisons
    key_frozenset = frozenset(key)
>>>>>>> 384f63b08c33ad2796878c1cd7b2d1c75768fd36

    # Search for an exact match
    exact_match = df1[df1['split_product_codes'].apply(lambda x: key_frozenset == frozenset(x))]

    if not exact_match.empty:
        # Return the profit of the first match
        return exact_match['Profit'].iloc[0]

    # If no exact match found, try to find partial matches
    for code_set in df1['split_product_codes']:
        if key_frozenset.issubset(frozenset(code_set)):
            return df1[df1['split_product_codes'] == code_set]['Profit'].iloc[0]

    # If still no match, return NaN
    return np.nan






def which_tours_do_we_recommend_to_a_traveller(dataframe1, dataframe2, go_together):
    #which tours do we recommend to a traveller? first make a copy of our dataframes to operate upon

    df1= dataframe1.copy()
    df2 = dataframe2.copy()
    together = go_together.copy()

    #filter the listings in df2 that have had a rating higher than 4
    liked_tours = df2[df2['Experience'].isin(['Excellent (5 stars)', 'Positive (4 stars)', 'Positive \n(4 stars)' , 'Excellent (5*)', 'Positive (4*)', '5*', '4*'])]
    liked_tours.to_excel('unimportant/liked.xlsx', index =False)