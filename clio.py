import numpy as np
import pandas as pd
from functions import *
from questions import *


#this is our main function file
#From here and on, our script starts executing
dataframe1, dataframe2 = read_files()


#do a minor edit in df1 so as to have all split product codes saved as a set
dataframe1, dataframe2 = edit_dfs(dataframe1, dataframe2)   



#how does a successful tour look like?
successful = successful_tour_looks_like(dataframe1, dataframe2)





#which tours go together?
go_together = which_tours_go_together(dataframe1, dataframe2)

#which tours go together?
#add profit to dataframe2
dataframe2 = add_df2_profit(dataframe1, dataframe2)

#which tours do we recommend to a traveller?
which_tours_do_we_recommend_to_a_traveller(dataframe1, dataframe2, go_together)

plot_travellers_vs_spending(successful)


optimum1 = optimum_number_of_stories_profit(dataframe1)
optimum2 = optimum_number_of_stories_liked(dataframe2)




save_to_excel(dataframe1, dataframe2)
