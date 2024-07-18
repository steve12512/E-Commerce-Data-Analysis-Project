import pandas as pd

def read_files():
    #this function reads our datasets and saves them as dataframe objects
    dataframe1 = pd.read_excel('reviews data.xlsx')
    dataframe2 = pd.read_excel('Booking Stats.xlsx')

    return dataframe1, dataframe2








































#MAIN
dataframe1, dataframe2 = read_files()
print(dataframe1.tail())