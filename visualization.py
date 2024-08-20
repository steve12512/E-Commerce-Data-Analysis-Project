import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

#this file contains the functions used for data visualization
def plot_travellers_vs_spending(df1):
    """
    Plot the relationship between the average number of travellers and the average money spent.
    
    Parameters:
    dataframe (pd.DataFrame): DataFrame with 'average_travellers' and 'Average_Money_Spent' columns.
    
    Returns:
    None
    """
    # Set the plot size
    plt.figure(figsize=(10, 6))
    
    # Plot the line plot with markers
    sns.lineplot(
        data=df1, 
        x='average_travellers', 
        y='Average_Money_Spent', 
        marker='o', 
        hue='Country'
    )
    
    # Set plot title and labels
    plt.title('Relationship between Average Number of Travellers and Average Money Spent')
    plt.xlabel('Average Number of Travellers')
    plt.ylabel('Average Money Spent')
    
    # Display legend and layout adjustments
    plt.legend(title='Country', bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.tight_layout()
    
    # Show the plot
    plt.show()



def visualize_optimum_number_of_stories_profit(df1):
    #visualize the corellation between number of stories and average profit
    #rename columns for clarity
    df1.columns = ['Number of Stories', 'Average Profit']

    # Create a seaborn plot
    plt.figure(figsize=(10, 9))
    #Create the bar plot with a different palette and thinner bars
    sns.barplot(x='Number of Stories', y='Average Profit', data=df1, palette='coolwarm', width=0.5)

    # Adding titles and labels
    plt.title('Average Profit by Number of Stories', fontsize=16)
    plt.xlabel('Number of Stories', fontsize=14)
    plt.ylabel('Average Profit', fontsize=14)

    # Adding the values on top of each bar
    for index, value in enumerate(df1['Average Profit']):
        plt.text(index, value + 200, f'{int(value)}', ha='center', va='bottom')
    plt.show()

    
def visualize_optimum_number_of_stories_likedness(df):
    #visualize the correlation between likedness and mean number of stories per likedness group
    plt.figure(figsize=(10, 6))
    sns.barplot(x='Standardized_Experience', y='Most_Common_Number_of_Stories', data=df, palette='rocket')
    plt.title('Mean Number of Stories by Experience Rating')
    plt.xlabel('Experience Rating')
    plt.ylabel('Mean Number of Stories')
    plt.show()