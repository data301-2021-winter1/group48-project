#Begin by importing our nessicary modules
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
%matplotlib inline
%reload_ext autoreload
%autoreload 2
import seaborn as sns



def load_and_process(url_path):
    '''
    This function takes the vaccination data set and strips it of columns ['Unnamed: 11', 'numweekdelta_atleast1dose', 'numweekdelta_fully', 'propweekdelta_partially', 'propweekdelta_fully','prfname'] as they do not provide insightful data for the purposes of this analysis. The function also cleans the remaining columns for string literals.
    
    Parameters:
    
    argument 1 (string): The url or path to the dataset
    
    Returns:
    
    Dataframe: With cleaned columns that are of float type for all numeric data and object type for all categorical data.

    '''
    #We begin our first method chain by loading our dataframe, strippping columns and then correcting for elements that have string literals. As they complicate the aggrigation process when using the Dataframe groupby() function.
    
    df1 = ( pd.read_csv(url_path)
              .drop('Unnamed: 11', 1)
              .drop('numweekdelta_atleast1dose', 1)
              .drop('numweekdelta_fully', 1)
              .drop('propweekdelta_partially', 1)
              .drop('propweekdelta_fully', 1)
              .drop('prfname', 1) )
    
    for col in df1.columns:
        df1[col].replace({np.nan:0.0}, inplace=True)
        df1[col].replace({'na':0.0}, inplace=True)
        
    #since we must alter all three of these columns to remove string literals best we use a loop.
    #fixcolumns (fixcol) holds the name of each column head we wish to alter in our for loop.
    fixcol = ['prop_atleast1dose', 'prop_partially', 'prop_fully']
    
    for e in fixcol:
        df1[e].replace(regex=True, inplace=True, to_replace=r'[^0-9.\-]',value=r'')
        df1[e] = df1[e].astype(float)
        
    #The date form found in the data is not usable in pandas and as such must be converted to a true date/time as shown below
    df1['week_end'] = df1['week_end'].apply(pd.to_datetime)
    
    return df1


def databyRegion(cleanData, pruid):
    
    '''
Since we are interested in segregating the data based on the region, this method will take the cleaned dataframe from load_and_process and also the pruid with which you are interested in. It will then build you a smaller data frame including the aggragated sums of partially and fully vaccinated across all vaccine products. Each tuple corresponds to the reporting week with which the data was collected.

    Parameters:
    
    argument 1 (Dataframe): Input a cleaned dataframe 
    
    argument 2 (pruid): Input the pruid matching the region with which you would like to specify the data within
    
    Returns:
    
    Dataframe: Holding the sum total of each reporting week of partially and fully vaccinated
    '''
    
    #Here we have taken our cleanDataframe and sequestered the pruid attribute, we then set it to equal that which the user requested in the method parameter.
    newdf = cleanData[(cleanData.pruid == pruid)]
    
    #Here we are using pd group by function to focus our set by week and summing all the vaccine counts for each product under the fully vaccinated column
    new1 = newdf.groupby("week_end")["numtotal_fully"].sum().to_frame(name = 'sumTotFul').reset_index()
    
    #We do the same thing but we now sum along the number of partially vaccinated, based on week
    new2 = newdf.groupby("week_end")["numtotal_partially"].sum().to_frame(name = 'sumTotPartially').reset_index()
    
    #We now can merge our two sets based on the fact that they share a common axis week_end, thus we perform an inner join on the two frames to produce our new dataframe dff which will be returned to the caller for use in further analysis 
    dff = pd.merge(new1, new2, on='week_end', how = 'inner')
    
    return dff