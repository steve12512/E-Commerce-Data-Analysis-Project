#import what you have to
import pandas as pd
import matplotlib as plt
import os
import numpy as np 
from sklearn.cluster import KMeans
from sklearn.preprocessing import LabelEncoder

#SET THE METHODS WE WILL BE USING

def read_files():
    #read dataframes from the excel files

    try:
        if os.path.exists('dataframe1.xlsx'):
            dataframe1 = pd.read_excel('dataframe1.xlsx')
        else:
            dataframe1 = combine_review_sheets()
            
        if os.path.exists('dataframe2.xlsx'):
            dataframe2 = pd.read_excel('dataframe2.xlsx')
        else:
            dataframe2 = combine_booking_sheets()
            print('a')
            #add the ticket cost
            dataframe2 = add_ticket_cost(dataframe2)
            print('b')
            #get the profit
            dataframe2 = profit(dataframe2)
            print('cS')
            
    except Exception as e:
        print(f"An error occurred: {e}")
    return dataframe1, dataframe2

def combine_review_sheets():
    #read and instantiate dataframe

    # File path to your Excel file
    file_path = 'reviews data.xlsx'  # Replace with your actual file path

    #load Excel file
    xlsx = pd.ExcelFile(file_path)

    #collect all unique column titles from each sheet
    all_columns = []

    #iterate through each sheet to collect column names
    for sheet_name in xlsx.sheet_names:
        df = pd.read_excel(file_path, sheet_name=sheet_name, header=1, nrows=0)  # Read only the second row for column names
        all_columns.extend([col for col in df.columns if col not in all_columns and not 'Unnamed' in str(col)])

    #initialize an empty DataFrame to store combined data
    combined_df = pd.DataFrame()

    #iterate through each sheet
    for sheet_name in xlsx.sheet_names:
        # Read the sheet into a DataFrame, starting from the second row for data
        df = pd.read_excel(file_path, sheet_name=sheet_name, header=1)

        # Iterate through each row to find the first entirely empty row
        for i in range(len(df)):
            if pd.isna(df.iloc[i]).all():  # Check if all elements in the row are NaN
                break
        # Keep only the data above the first entirely empty row
        df = df.iloc[:i]

        # Add a column to indicate the source sheet
        df['Source Sheet'] = sheet_name
        
        # Append this DataFrame to the combined DataFrame
        combined_df = pd.concat([combined_df, df], ignore_index=True, sort=False)

    # Reindex the combined DataFrame to include all collected columns plus the Source Sheet column
    combined_df = combined_df.reindex(columns=all_columns + ['Source Sheet'])

    #in the first column of combined_df turn "0" to "FALSE" and "1" to "TRUE"
    combined_df['Important Information'] = combined_df['Important Information'].replace({0: 'FALSE', 1: 'TRUE'})

    #rename the dataframe to dataframe1
    dataframe1 = combined_df
    
    #split recommended['Name of Product Reviewed'] to 2 columns seperated by '|'
    dataframe1[['product_code', 'product_review']] = dataframe1['Name of Product Reviewed'].str.split('|', expand=True)
    
    #drop the column Name of Product Reviewed
    dataframe1.drop(columns=['Name of Product Reviewed'], inplace=True)
    
    #drop the rows where product_code column is na
    dataframe1.dropna(subset=['product_code'], inplace=True)
    
    #drop the rows where product_code does not start with "STL,TO,AU,TL"
    dataframe1 = dataframe1[dataframe1['product_code'].str.startswith(('STL', 'TO', 'AU', 'TL'))]
    
    dataframe1.to_excel('dataframe1.xlsx', index = False)
    
    return dataframe1

def combine_booking_sheets():
    # File path to your Excel file
    file_path = 'Booking Stats.xlsx'  # Replace with your actual file path

    # List of month names to include
    month_names = [
        'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
        'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'
    ]

    # Load Excel file
    xlsx = pd.ExcelFile(file_path)

    # Initialize an empty DataFrame to store combined data
    combined_df = pd.DataFrame()

    # Iterate through each sheet
    for sheet_name in xlsx.sheet_names:
        if sheet_name in month_names:  # Only combine if the sheet is a month
            # Read the sheet into a DataFrame, using the first row as the header
            df = pd.read_excel(file_path, sheet_name=sheet_name)
            
            # Add a column to indicate the source sheet
            df['Source Sheet'] = sheet_name
            
            # Append this DataFrame to the combined DataFrame
            combined_df = pd.concat([combined_df, df], ignore_index=True)
    
    # Rename the combined DataFrame to dataframe2
    dataframe2 = combined_df
    
    dataframe2 = manipulate_dataframe2(dataframe2)
        
    return dataframe2

def manipulate_dataframe2(dataframe2):
    # Language codes mapping based on the provided information
    language_codes = {
        'Greek': 'GR', 'English': 'EN', 'Chinese': 'CH', 'Italian': 'IT',
        'German': 'DE', 'French': 'FR', 'Russian': 'RU', 'Spanish': 'ES',
        'Romanian': 'RO', 'Serbian': 'SR', 'Turkish': 'TR', 'Hebrew': 'HE',
        'Czech': 'CS', 'Hungarian': 'HU', 'Polish': 'PL', 'Bosnian': 'BS',
        'Albanian': 'SQ', 'Irish': 'GA', 'Norwegian': 'NO', 'Portuguese': 'PT',
        'Korean': 'KO', 'Japanese': 'JA'
    }

    # Function to map full language name to language code
    def map_language_to_code(language):
        return language_codes.get(language, None)

    # Apply the function to the 'Language' column to create a new 'Language Code' column
    # Replace 'LanguageColumnName' with the actual name of the column in dataframe2 that contains language names
    dataframe2['Language Code'] = dataframe2['language'].apply(map_language_to_code)

    return dataframe2

def add_ticket_cost(dataframe2):
    
    # Load the "ticket cost" sheet into a DataFrame
    ticket_cost_df = pd.read_excel('Booking Stats.xlsx', sheet_name='Ticket Cost')
    
    # Set the product code as the index for easier access
    ticket_cost_df.set_index('Product Code', inplace=True)
        
    # Drop the rows where net_price column is na
    dataframe2.dropna(subset=['net_price'], inplace=True)
    
    # Concatenate the product_code and Language Code
    dataframe2['Full Product Code'] = dataframe2['product_code'] + dataframe2['Language Code']

    # Iterate over each row in dataframe2
    for index, row in dataframe2.iterrows():
        # Get the full product code for the current row
        full_product_code = row['Full Product Code']
        # Get the month for the current row, assuming the 'month' column format is 'Month YYYY'
        month = row['month'].split()[0]  # Take only the first part, which is the month name



        ticket_cost_df.to_excel('ticket_cost.xlsx', index= False)




        # Find the price in the ticket cost dataframe
        if full_product_code in ticket_cost_df.index:
            # Extract the price for the corresponding month
            price = ticket_cost_df.at[full_product_code, month]
            # Check if the price is a Series or a single value
            if isinstance(price, pd.Series):
                price = price.iloc[0]  # Take the first element of the Series
            elif isinstance(price, str):
                # Clean up the price to be a float (remove '€' and convert to float)
                price = float(price.replace('€', ''))
        else:
            # If the product code is not found, set the price to None or a default value
            price = 0
        
        dataframe2.at[index, 'Ticket Price'] = price
    
    #drop the 'Full Product Code' column
    dataframe2.drop(columns=['Full Product Code'], inplace=True)
    
    #fill the NaN values with 0
    dataframe2['Ticket Price'].fillna(0, inplace=True)
    return dataframe2

def profit(dataframe2):
        
        #calculate the profit
        dataframe2['Profit'] = dataframe2['retail_price'] - dataframe2['Ticket Price']
        dataframe2.to_excel('dataframe2.xlsx', index = False)
        
        return dataframe2

def create_successful():
    #create a new dataframe that contains only the listings with a rating of 4 or higher

    #first create  a copy of the original dataframe to operate upon
    successful_by_Exprerience = dataframe1.copy()
    successful_by_number_of_travellers = dataframe2.copy()

    #filter the successful visits
    if 'Overall Experience' in successful_by_Exprerience.columns:
        successful_by_Exprerience = successful_by_Exprerience[successful_by_Exprerience['Overall Experience'].isin(['Excellent(5 stars)', 'Positive (4 stars)', 'Excellent (5*)', 'Positive (4*)', '5*', '4*','Positive \n(4 stars)'])]
    
    #for each month calculate the number of travelers
    travellers = dataframe2.groupby('month')['num_of_travellers'].sum().reset_index()

    successful_by_Exprerience_percentage = successful_by_Exprerience.groupby('Source Sheet').size().reset_index()
    successful_by_Exprerience_percentage = successful_by_Exprerience_percentage.rename(columns= {'Source Sheet' : 'month'})
    travellers['month'] = travellers['month'].str.replace('2023','').str.strip()

    #now we have to order the months in both dataframes
    #sort by 'month' in descending order
    months = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September']

    successful_by_Exprerience_percentage['month'] = pd.Categorical(successful_by_Exprerience_percentage['month'], categories=months, ordered=True)
    successful_by_Exprerience_percentage = successful_by_Exprerience_percentage.sort_values(by='month', ascending= True)

    #since the travellers dataframe has 3 months which the other df doesnt have, we will have to drop these months
    travellers = travellers[~travellers['month'].isin(['November', 'October', 'December'])]

    travellers['month'] = pd.Categorical(travellers['month'], categories=months, ordered=True)
    travellers = travellers.sort_values(by='month', ascending= True)
    
    #create a new column that stores the values of succesful ratings / number of travellers. below is the process of how these values are calculated
    successful_by_Exprerience_percentage['percentage'] = 0.00
    
    for index, row in successful_by_Exprerience_percentage.iterrows():
        month1 = row['month']
        month2 = travellers.loc[travellers['month'] == month1, 'month'].values
        if len(month2) > 0:
            month2 = month2[0]
            num_of_travellers = travellers.loc[travellers['month'] == month2, 'num_of_travellers'].values[0]
            successful_by_Exprerience_percentage.at[index, 'percentage'] = row[0] / num_of_travellers * 100

    successful_by_Exprerience_percentage = successful_by_Exprerience_percentage.sort_values(by = 'percentage', ascending= False)
    successful_by_Exprerience_percentage = successful_by_Exprerience_percentage.drop(columns=0)
    successful_by_Exprerience_percentage.to_excel('outputfiles\successful_months_by_percentage.xlsx', index= False)


    #group by month column "Source Sheet", "product_code" and calculate the sum of num_of_travellers
    successful_by_number_of_travellers = successful_by_number_of_travellers.groupby(['Source Sheet', 'product_code'])['num_of_travellers'].sum().reset_index()
    
    #sort by num_of_travellers in descending order
    successful_by_number_of_travellers = successful_by_number_of_travellers.sort_values(by=['num_of_travellers'], ascending=False)  
    
    successful_by_Exprerience.to_excel(output_loc + 'Successful_by_Exprerience.xlsx', index = False)
    successful_by_number_of_travellers.to_excel(output_loc + 'Successful_by_number_of_travellers.xlsx', index = False)
    successful_by_number_of_travellers2 = successful_by_number_of_travellers.groupby('Source Sheet')['num_of_travellers'].size().reset_index()
    successful_by_number_of_travellers2 = successful_by_number_of_travellers2.sort_values(by = 'num_of_travellers', ascending= False)
    successful_by_number_of_travellers2.to_excel('outputfiles\\travellers_by_month.xlsx', index = False)
    return successful_by_Exprerience, successful_by_number_of_travellers


def analyze_successful():
    try:
        # Count the occurrences of each tour in each month
        tour_counts = successful_by_Exprerience.groupby(['Source Sheet', 'product_code']).size().reset_index(name='Count')
        # Pivot the table to have months as columns and tours as rows
        tour_counts_pivot = tour_counts.pivot(index='product_code', columns='Source Sheet', values='Count').fillna(0).astype(int)

        # Add a row at the bottom to show the total count for each tour across all months
        tour_counts_pivot.loc['Total'] = tour_counts_pivot.sum()

        # Save the counts to a new Excel file
        output_tour_counts_file = ('TourCountsPerMonth.xlsx')
        tour_counts_pivot.to_excel(output_loc + output_tour_counts_file)

        return tour_counts_pivot
    except Exception as e:
        print(f"An error occurred while reading the Successful.xlsx file: {e}")
        return None, None

def count_product_types_by_codes(file_path, product_codes, output_file_path='product_types_count_result.xlsx'):
    # Load the Excel file into a DataFrame
    df = pd.read_excel(file_path)

    # Filter the DataFrame for September 2023 and specified product codes
    september_df = df[(df['month'] == 'September 2023') & df['product_code'].isin(product_codes)]

    # Count the occurrences of each product type for each product code
    product_types_count = september_df.groupby(['product_code', 'product_type']).size().reset_index(name='Count')

    # Print or use the result as needed
    print(product_types_count)

    # Save the result to an Excel file
    product_types_count.to_excel(output_file_path, index=False)
    print(f"Results saved to {output_file_path}")




def average_travelers_by_tours(file_path, product_codes, output_file_path='average_travelers_result.xlsx'):
    #load the Excel file into a DataFrame
    df = pd.read_excel(file_path)

    #filter the DataFrame for September 2023 and specified toursjn
    september_df = df[(df['month'] == 'September 2023') & df['product_code'].isin(product_codes)]

    # Calculate the average number of travelers for each tour
    average_travelers = september_df.groupby('product_code')['num_of_travellers'].mean().reset_index(name='Average_Num_of_Travelers')

    # Print or use the result as needed
    print(average_travelers)

    # Save the result to an Excel file
    average_travelers.to_excel(output_file_path, index=False)
    print(f"Results saved to {output_file_path}")

def testk_means():
    copy = dataframe2.copy()
    
    #filter only the "Sheets" that have "August, September"
    copy = copy[copy['Source Sheet'].isin(['August', 'September'])]
    
    #encode the "tours" column with label encoder
    le = LabelEncoder()
    copy['tours'] = le.fit_transform(copy['tours'])
    
    #do k means clustering on the "tours" column
    kmeans = KMeans(n_clusters=3, random_state=0).fit(copy[['tours']])
    
    #to excel
    copy['cluster'] = kmeans.labels_
    
    #return the "tours" column to its original state
    copy['tours'] = le.inverse_transform(copy['tours'])
    
    #keep only the top 10 num_of_travellers per cluster
    copy = copy.sort_values(by=['num_of_travellers'], ascending=False)
    copy = copy.groupby('cluster').head(10)
     
    copy.to_excel(output_loc + 'kmeans.xlsx', index = False)
    
def go_together():
    #find which tours go together. to do that we will use the groupby operator on the second dataframe
    grouped = dataframe2.groupby('seller_name')['product_code'].agg(list).reset_index()
    grouped.columns = ['seller name', 'product code']
    
    #in the column 'product code' we want to keep only the unique values for each seller
    grouped['product code'] = grouped['product code'].apply(lambda x: list(set(x)))
    
    grouped.to_excel(output_loc + 'grouped.xlsx', index = False)

    #now create a dictionary, so that for each seller we have the name of the tours he provides, instead of their codes
    map_together(grouped)


def map_together(grouped):
    #create a copy of the dataframe to operate upon
    grouped2 = grouped.copy()

    #map the columns to product names using the product dictionary
    grouped2['product_name'] = grouped2['product code'].apply(lambda codes: ', '.join(product_dict.get(code, '') for code in codes))
    grouped2.to_excel(output_loc + 'sellernames_tours.xlsx', index = False)



def create_dictionary():
    #map product codes to product titles
    mapping = dict(zip(dataframe2['product_code'] , dataframe2['product_title']))

    #Convert the dictionary to a DataFrame in order to save it as an excel file
    df_product = pd.DataFrame(list(mapping.items()), columns=['product_code', 'product_title'])

    #save the DataFrame to an Excel file
    df_product.to_excel(output_loc + 'dictionary.xlsx', index=False)

    return mapping

def profit_per_tour():
    # Now group by 'product_code' and calculate the sum and mean of 'Profit'
    profit = dataframe2.groupby('product_code')['Profit'].agg(['sum', 'mean']).reset_index()

    # Rename the columns for clarity
    profit.columns = ['product_code', 'Total Profit', 'Average Profit']

    # Save the grouped data to a new Excel file
    profit.to_excel(output_loc + 'grouped_profit.xlsx', index=False)

def recommended_stories():
    #We take the name of the tours of the visits that were rated 5 stars
    recommended = dataframe1[dataframe1['Overall Experience'].isin(['Excellent(5 stars)', 'Excellent (5*)', '5*'])]
        
    #Keep only the rows that have unique product codes
    recommended = recommended.drop_duplicates(subset=['product_code'])
    
    recommended = recommended[['product_code']]
    
    recommended.to_excel(output_loc + 'recommended_by_stars.xlsx', index = False)
    
    #Load the grouped_profit.xslx file
    grouped_profit = pd.read_excel(output_loc + 'grouped_profit.xlsx')
    
    #sort the grouped_profit by the Total Profit column
    grouped_profit = grouped_profit.sort_values(by=['Total Profit'], ascending=False)
    
    #keep the first 10 rows
    grouped_profit = grouped_profit.head(10)
    
    #save the grouped_profit to an excel file
    grouped_profit.to_excel(output_loc + 'recommended_by_profit.xlsx', index=False)
        
def optimum_number_of_stories():
    #create a copy of the dataframe2 to operate upon
    dataframe2_copy = dataframe2.copy()
    
    #count how many tours each row has by counting the commas in the tours column
    dataframe2_copy['tours'] = dataframe2_copy['tours'].str.count(',') + 1
  
    #group by the number of tours and calculate the sum of num_of_travellers
    optimum_number_of_stories = dataframe2_copy.groupby('tours')['num_of_travellers'].sum().reset_index()
    
    #ascending order
    optimum_number_of_stories = optimum_number_of_stories.sort_values(by=['num_of_travellers'], ascending=False)
    
    optimum_number_of_stories.to_excel(output_loc + 'optimum_number_of_stories.xlsx', index=False)

def upsell():
    #create a copy of the dataframe2 to operate upon
    dataframe2_copy = dataframe2.copy()
    
    #split the "booking_date" column to 2 columns seperated by " "
    dataframe2_copy[['booking_date', 'booking_time']] = dataframe2_copy['booking_date'].str.split(' ', expand=True)
    
    #filter only "August" and "September"
    dataframe2_copy = dataframe2_copy[dataframe2_copy['Source Sheet'].isin(['August', 'September'])]
    
    #from the booking_time keep only the 2 first digits
    dataframe2_copy['booking_time'] = dataframe2_copy['booking_time'].str[:2]
    
    #group by Source Sheet, booking_time and calculate the sum of num_of_travellers
    upsell = dataframe2_copy.groupby(['Source Sheet', 'booking_time'])['num_of_travellers'].sum().reset_index()
    
    #ascending order
    upsell = upsell.sort_values(by=['num_of_travellers'], ascending=False)
    upsell.to_excel(output_loc + 'upsell.xlsx', index=False)
    
    #keep august for one excel file and september for the other
    august_upsell = upsell[upsell['Source Sheet'] == 'August']
    september_upsell = upsell[upsell['Source Sheet'] == 'September']
    
    #save the results to excel files
    august_upsell.to_excel(output_loc + 'august_upsell.xlsx', index=False)
    september_upsell.to_excel(output_loc + 'september_upsell.xlsx', index=False)
    

def prompt_for_download():
    #create a copy of the dataframe2 to operate upon
    prompt = dataframe2.copy()
    
    month_names = [
        'January', 'February', 'March', 'April', 'May', 'June',
        'July', 'August', 'September', 'October', 'November', 'December'
    ]
    
    #group by Source Sheet and calculate the sum of num_of_travellers
    prompt_for_download = prompt.groupby('Source Sheet')['num_of_travellers'].sum().reset_index()
    
    #descending order
    prompt_for_download = prompt_for_download.sort_values(by=['num_of_travellers'], ascending=False)
    
    #keep only the first row
    prompt_for_download = prompt_for_download.head(1)
    
    #check which month is at the top
    top_month = prompt_for_download.iloc[0]['Source Sheet']
    
    #get the month before the top month
    month_before = month_names[month_names.index(top_month) - 1]
    
    #write at the 3rd row 1st cell the month before the top month
    prompt_for_download.at[2, 'Source Sheet'] = month_before
    
    prompt_for_download.to_excel(output_loc + 'prompt_for_download.xlsx', index=False)

def ask_for_review():
    #when is the best time to ask for a review? the answer is obvious. it lies upon the months that have the highest percentages of 4 and 5 star reviews

    #copy a dataframe to operate upon
    df = dataframe1.copy()

    #group by month and count the occurences of 4 and 5 star reviews
    df = df[df['Overall Experience'].isin(['Excellent (5 stars)', 'Positive (4 stars)', 'Excellent (5*)', 'Positive (4*)', '5*', '4*'])]
    df['Rating'] = df['Overall Experience'].apply(lambda x: '4s' if x in ['Positive (4 stars)', 'Positive (4*)', '4*'] else '5s')
    df = df.groupby(['Source Sheet', 'Rating']).size().unstack(fill_value=0)
    merged_df = pd.merge(df, successful_by_number_of_travellers, on='Source Sheet', how='inner')
    merged_df = merged_df.drop(columns=['product_code'])
    merged_df.drop_duplicates(subset=['Source Sheet'], inplace=True)




    merged_df['success/travellers'] = (merged_df['4s'] + merged_df['5s']) / (merged_df['num_of_travellers'])
    merged_df = merged_df.sort_values(by='success/travellers', ascending=False)

    #save the result to an excel file
    merged_df.to_excel(output_loc + 'best_time_for_review.xlsx', index= True)
    return None


def seasonal_patterns_growth_decline_trends():
    #in this function we want to find certain patterns and trends based on the season. the season by itself implicates a groupby months
    #we will groupby month, product_country and Language Code. then we will sum the profit and number of travellers for these columns

    #create a copy of the original dataframe to operate upon
    df = dataframe2.copy()

    #transofrm month to datetime so that we can operate upon it and sort by it.
    df['month'] = pd.to_datetime(df['month'], format='%B %Y', errors='coerce').dt.month_name()

    #group by 'month', 'product_country', and 'Language Code', then aggregate
    df = df.groupby(['month', 'product_country', 'Language Code']).agg({'Profit': 'sum', 'num_of_travellers': 'sum'}).reset_index()

    #sort by 'month' in descending order
    month_order = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
    df['month'] = pd.Categorical(df['month'], categories=month_order, ordered=True)
    df = df.sort_values(by=['month', 'product_country', 'Language Code'], ascending= [True, True, True])

    #now we have to calculate the percentage change per month by grouping by correctly. [
    df['profit_change'] = df.groupby(['product_country', 'Language Code'])['Profit'].pct_change() * 100
    df['travellers_change'] = df.groupby(['product_country', 'Language Code'])['num_of_travellers'].pct_change() * 100



    #now we will only keep the values that have a diffence of trends greater than 50%, and then do the same for those whose difference >100%, and then for those with difference >200%
    travellers_low_difference = df[np.abs(df['travellers_change']) >= 50]
    travellers_med_difference = df[np.abs(df['travellers_change']) >= 100]
    travellers_high_difference = df[np.abs(df['travellers_change'])>= 200]

    profit_low_difference = df[np.abs(df['profit_change']) >= 50]
    profit_med_difference = df[np.abs(df['profit_change']) >= 100]
    profit_high_difference = df[np.abs(df['profit_change'])>= 200]

    #order some our dataframes
    profit_high_difference = profit_high_difference.sort_values(by = 'profit_change', ascending= False)
    travellers_high_difference = travellers_high_difference.sort_values(by = 'travellers_change', ascending= False)
    travellers_high_difference_noneg = travellers_high_difference.copy()
    travellers_high_difference_noneg = travellers_high_difference_noneg[travellers_high_difference_noneg['Language Code'] != 'EN']

    #test df
    test = df.copy().groupby(['month', 'product_country', 'Language Code']).agg({'num_of_travellers' : 'sum'})
    test.to_excel('seasonal_patterns/test.xlsx', index = True)


    travellers_high_difference['profit_change'] = travellers_high_difference['profit_change'].map('{:.2f}%'.format)
    travellers_high_difference['travellers_change'] = travellers_high_difference['travellers_change'].map('{:.2f}%'.format)




    #save files
    profit_low_difference.to_excel('seasonal_patterns/profit_low.xlsx', index= True)
    profit_med_difference.to_excel('seasonal_patterns/profit_med.xlsx', index = True)
    profit_high_difference.to_excel('seasonal_patterns/profit_high.xlsx', index = True)

    travellers_low_difference.to_excel('seasonal_patterns/travellers_low.xlsx', index= True)
    travellers_med_difference.to_excel('seasonal_patterns/travellers_med.xlsx', index = True)
    travellers_high_difference.to_excel('seasonal_patterns/travellers_high.xlsx', index = True)

    travellers_high_difference_noneg.to_excel('seasonal_patterns/travellers_high_difference_noneg.xlsx', index= True)



    df.to_excel('seasonal_patterns/seasonal_patterns.xlsx', index=True)
    return None


#START
#make folder called outputfiles
if not os.path.exists('outputfiles'):
    os.makedirs('outputfiles')
if not os.path.exists('seasonal_patterns'):
    os.makedirs('seasonal_patterns')


#from here and on our program starts
output_loc = './outputfiles/'

dataframe1, dataframe2 = read_files()
dataframe2 = add_ticket_cost(dataframe2)
print('b')
#get the profit
dataframe2 = profit(dataframe2)
#1. What does a successful tour look like?
successful_by_Exprerience ,successful_by_number_of_travellers = create_successful()

#create a dictionary that maps product codes to product titles
product_dict = create_dictionary()

tour_counts_per_month = analyze_successful()

#some breakpoints


#2. Which tours go together
go_together()


#profit per tour
profit_per_tour()

#3. Which stories would we recommend
recommended_stories()

#4. What is the most optimum number of stories??
optimum_number_of_stories()

#5. When is the best time to upsell?
upsell()

#6. When is the best time to prompt for download?
prompt_for_download()

#7 when is the best time to ask for a review
ask_for_review()

#8 seasonal patterns and growth/decline trends
seasonal_patterns_growth_decline_trends()



#test k means clustering
testk_means()