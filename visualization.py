import matplotlib.pyplot as plt
import seaborn as sns


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