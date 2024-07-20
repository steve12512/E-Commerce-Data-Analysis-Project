import pandas as pd

def read_files():
    #this function reads our xlsx files and saves them as dataframe objects

    dataframe1 = pd.read_excel('Booking Stats.xlsx')
    dataframe2 = pd.read_excel('reviews data.xlsx')











































#START
#from here and on, our script starts executing

dataframe1, dataframe2, = read_files()