from functions import *
from visualization import *

#this file answer our questions

def successful_tour_looks_like(dataframe1, dataframe2):
    #how does a sucessful tour look like? filter the listings in df1 that have a profit higher than the average. then groupby country and month, find insights about the listings with the most important being the sum of profit, and then sort them in descending order
    # to begin with, keep a copy of dataframe1    df1 = dataframe1.copy()
    df1 = dataframe1.copy()
    df2 = dataframe2.copy()

    # Calculate the profit mean for the tours in dataframe1
    mean = df1['Profit'].mean()

    # Filter the listings in dataframe1 that have a profit higher than the average
    df1 = df1[df1['Profit'] > mean]

    # Calculate the number of products per listing
    df1['num_products'] = df1['product_code'].apply(lambda x: len(x.split('_')))

    # Group by country and month, find insights, and calculate the top 3 most common travel days and their counts
    df1 = df1.groupby(['Country', 'month']).agg(
        most_common_tour = ('stories', lambda x : x.mode().tolist()[0:4]),
        average_travellers=('num_of_travellers', 'mean'), 
        Total_Travellers=('num_of_travellers', 'size'),
        Average_number_of_products=('num_products', 'mean'),
        Total_profit=('Profit', 'sum'),
        Top_3_travel_days=('travel_day', lambda x: Counter(x).most_common(3)), 
        Average_Money_Spent_per_group = ('retail_price', 'mean'),
        average_money_spent_per_traveller = ('money_spent_per_traveller', 'mean'),
        most_common_languages=('language', lambda x: x.mode().tolist()[:3]),
        most_common_number_of_stories = ('number_of_stories', lambda x: x.mode().tolist()[0])     
    ).reset_index()

    #keep listings that have at least 30 travellers
    df1 = df1[df1['Total_Travellers'] > 30]
    # Sort values based on total profit, descending
    df1 = df1.sort_values(by='Total_profit', ascending=False)

    # Save the result to an Excel file
    save_df_to_excel_with_standard_width(df1,'questions/successful_tours_looks_like.xlsx', column_width= 20)
    return df1



def which_tours_go_together(dataframe1, dataframe2):
    #which tours go together? first make a copy of our dataframes
    df1 = dataframe1.copy()
    df2 = dataframe2.copy()

    #split product codes on _, create a new column for each combination and count the number of its occurances
    df1['product_combinations'] = df1['product_code'].apply(lambda x: tuple(sorted(x.split('_'))))
    
    
    grouped_df = df1.groupby('product_combinations').agg(
    Occurrences=('product_combinations', 'size'),
    Average_Profit=('Profit', 'mean')
).reset_index()

    #filter for combinations with at least 2 products
    grouped_df = grouped_df[grouped_df['product_combinations'].apply(lambda x: len(x) > 1)]

    #store a dictionary to map product codes to their names
    code_to_tour = dict(zip(df2['split_product_code'], df2['Name of Product']))

    #for each product code in product code combination, map it to its corresponding tour name, and after having done that for all codes, concatenate the string
    grouped_df['tour_names'] = grouped_df['product_combinations'].apply(lambda x: get_tour_names(x, code_to_tour, df2))    

    #sort the DataFrame by the number of occurrences
    grouped_df = grouped_df.sort_values(by='Occurrences', ascending=False)

    #save  to an Excel file
    save_df_to_excel_with_standard_width(grouped_df, 'questions/tours_go_together.xlsx', column_width=20)
    grouped_df.to_excel('questions/tours_go_together.xlsx', index=False)
    return grouped_df



def which_tours_do_we_recommend_to_a_traveller(dataframe1, dataframe2, go_together):
    #which tours do we recommend to a traveller? first make a copy of our dataframes to operate upon
    #result 1 filters dataframe 2 into the most liked tours and finds the occurence of these tours per month, country as well as their profit sum
    #result 2 uses dataframe 1, and groups by country, month, product and finds the sum of profit
    df1= dataframe1.copy()
    df2 = dataframe2.copy()
    together = go_together.copy()

    #filter the listings in df2 that have had a rating higher than 4
    liked_tours = df2[df2['Experience'].isin(['Excellent (5 stars)', 'Positive (4 stars)', 'Positive \n(4 stars)' , 'Excellent (5*)', 'Positive (4*)', '5*', '4*'])]

    #now do a pivot operation. keep the name of our product as index, and pivot the experience column into 2 columns, the 4 and 5 ratings, and count the occurence of each review for the afore mentioned product
    pivot_df = liked_tours.pivot_table(index = 'Product Code and Name', columns = 'Experience', aggfunc = 'size', fill_value = 0).reset_index()
  
    #calculate the 'successful_experience' as the sum of the experience ratings columns
    pivot_df['successful_experience'] = pivot_df['Excellent (5 stars)'] + pivot_df['Excellent (5*)'] + pivot_df['Positive \n(4 stars)'] + pivot_df['Positive (4 stars)'] + pivot_df['Positive (4*)']

    #aggregate additional information (Profit, Country, Month)
    additional_info = liked_tours.groupby(['Product Code and Name', 'Country', 'month']).agg(
        total_profit=('Profit', 'sum'),
        count_listings=('Product Code and Name', 'size')
    ).reset_index()
    
    
    #merge the pivot table with additional information
    result1 = pd.merge(pivot_df, additional_info, on='Product Code and Name', how='left')

    #sort the result by 'total_profit' in descending order
    result1 = result1.sort_values(by='total_profit', ascending=False)

    #now we ll do the same but we ll be using df1
    result2 = df1.groupby(['Country', 'month', 'product_title']).agg(
        product_title_occurences=('product_title', 'count'),
        total_profit=('Profit', 'sum'),
        total_travellers=('num_of_travellers', 'sum')
    ).reset_index()

    result2 = result2.sort_values(by=['Country', 'total_profit'], ascending=[True, False])
    
    #keep only those with total profit > 1000
    result2 = result2[result2['total_profit'] >= 1000]
    
    
    # Keep only the top 5 listings per country based on 'total_profit'
    #top_5_per_country = result2.groupby('Country').head(5)
    top_5_per_country = (
    result2.drop_duplicates(subset=['Country', 'product_title'])
           .groupby('Country')
           .head(15)
) 
    result1.to_excel('questions/recommended1.xlsx', index =False)
    result2.to_excel('questions/recommended2.xlsx', index =False)
    save_df_to_excel_with_standard_width(top_5_per_country, 'questions/rec3.xlsx', column_width=18)

    
def optimum_number_of_stories_profit(df):
   #use dataframe1. groupby number of stories, and mean profit to find the corellation between em
   df1 = df.copy()
   df1 = df1.groupby('number_of_stories')['Profit'].mean().reset_index()
   df1.to_excel('questions/optimum_number_of_stories.xlsx', index = False)
   visualize_optimum_number_of_stories_profit(df1)
   df1.to_excel('questions/optimum_by_profit.xlsx', index = False)
   save_df_to_excel_with_standard_width(df1,'questions/optimum_by_profit.xlsx.xlsx', column_width= 20)
   return df1


def optimum_number_of_stories_liked(df2):
    #use dataframe2 to visualize the correlation between number of stories and likenedness
    #copy our dataframes
    df2_copy = df2.copy()
    df2_copy = df2_copy.groupby('Standardized_Experience').agg(
        Number_of_listings = ('Standardized_Experience', 'size'),
        Most_Common_Number_of_Stories = ('number_of_stories', lambda x : x.mode().iloc[0])).reset_index()
    #visualize and save the result
    df2_copy.to_excel('questions/optimum_number_of_stories_likedness.xlsx', index = False)
    save_df_to_excel_with_standard_width(df2_copy,'questions/optimum_number_of_stories_likedness.xlsx', column_width= 20)
    visualize_optimum_number_of_stories_likedness(df2_copy)

    
    
def common_booking_hours(dataframe1):
    #this function, finds for each country, the most common booking hours
    df1 = dataframe1.copy()
    df1_copy = df1.groupby('Country').agg(
        Most_Common_Booking_hours=('booking_hour', lambda x: ', '.join(
            [str(hour) for hour in x.value_counts().index[:6]]  # Sort by frequency and get top 4
        ))
    ).reset_index()
    df1_copy.to_excel('questions/most_common_hours.xlsx', index = False)
    return df1_copy

def successful_tour_looks_like_without_months(dataframe1, dataframe2):
    #
    df1 = dataframe1.copy()

    # Calculate the number of products per listing
    df1['num_products'] = df1['product_code'].apply(lambda x: len(x.split('_')))

    # Group by country to find insights and calculate statistics
    df1_grouped = df1.groupby(['Country']).agg(
        most_common_tour=('stories', lambda x: x.mode().tolist()[:4]),
        average_travellers=('num_of_travellers', 'mean'),
        Total_Travellers=('num_of_travellers', 'size'),
        Average_number_of_products=('num_products', 'mean'),
        Total_profit=('Profit', 'sum'),
        Average_profit=('Profit', 'mean'),
        Top_3_travel_days=('travel_day', lambda x: Counter(x).most_common(3)),
        Average_Money_Spent_per_group=('retail_price', 'mean'),
        average_money_spent_per_traveller=('money_spent_per_traveller', 'mean'),
        most_common_languages=('language', lambda x: x.mode().tolist()[:3]),
        most_common_number_of_stories=('number_of_stories', lambda x: x.mode().tolist()[0])
    ).reset_index()


    # Sort values based on total profit, descending
    df1_filtered = df1_grouped.sort_values(by='Total_profit', ascending=False)

    # Save the result to an Excel file
    save_df_to_excel_with_standard_width(df1_filtered, 'questions/successful_tours_look_like_WITHOUT_MONTHS.xlsx', column_width=20)
    return df1_filtered

def find_info_for_spain(df):
    #this function provides information for spain. let us start by copying our dataframe
    coppy= df.copy()
    spain = coppy[coppy['Country'] == 'Spain']

    #groupby stories and find info
    spain = spain.groupby('stories').agg(
        occurences = ('stories', 'size'),
        average_travellers=('num_of_travellers', 'mean'), 
        Total_Travellers=('num_of_travellers', 'size'),
        Total_profit=('Profit', 'sum'),
        Average_profit = ('Profit', 'mean'),
        Top_3_travel_days=('travel_day', lambda x: Counter(x).most_common(3)),        
        most_common_languages=('language', lambda x: x.mode().tolist()[:3])
        ).reset_index()
    spain = spain.sort_values(by = 'occurences', ascending = False)
    return spain