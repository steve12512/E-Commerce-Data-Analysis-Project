import numpy as np
import pandas as pd
from functions import read_files, save_to_excel, successful_tour_looks_like










#this is our main function file
#From here and on, our script starts executing
dataframe1, dataframe2 = read_files()
save_to_excel(dataframe1, dataframe2)

#how does a successful tour look like?
successful_tour_looks_like(dataframe1)