#Begin by importing our nessicary modules
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
#This File created by Joe Gaspari

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
        df1[col].replace({np.nan:0}, inplace=True)
        df1[col].replace({'na':0.0}, inplace=True)
        
    #since we must alter all three of these columns to remove string literals best we use a loop.
    #fixcolumns (fixcol) holds the name of each column head we wish to alter in our for loop.
    fixcol = ['prop_atleast1dose', 'prop_partially', 'prop_fully', 'numtotal_partially']
    
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
    dff.insert(1, "Region", region(pruid), True)
    
    
    return dff



def region(reg):
    
    di = {1:'Canada', 10:'Newfoundland and Labrador', 12:'Nova Scotia',24:'Quebec',
       46:'Manitoba', 47:'Saskatchewan', 59:'British Columbia', 60:'Yukon',
       61:'Northwest Territories', 62:'Nunavut', 11:'Prince Edward Island',
       13:'New Brunswick', 48:'Alberta', 35:'Ontario'}
    
    return di[reg]


def viscompar(dataframe, regn):
    '''
    Viscompar will take the data frame and plot both y axis separatly 
    
    argument 1 (Dataframe): Input selected dataframe from databyregion
    
    Returns: 
    
    All plots comprised of partially and fully vaccinated over the 39 week interval
    
    '''
    
    
    plt.figure(figsize=(20,10))
    plt.title(f"Total Number of Partial/Fully Vaccinated in {region(regn)} Over 39 Weeks", fontsize=18)
    plt.plot('week_end','sumTotFul', data=dataframe, label='Fully Vaxed', linestyle='-', marker='o')
    
  
    plt.plot('week_end','sumTotPartially', data=dataframe, label='Partially Vaxed', linestyle='-', marker='o')
   

    plt.legend()
    return plt

def NormComp(dataframe, regn):
    '''
    Viscompar will take the data frame and plot both y axis separatly 
    
    argument 1 (Dataframe): Input selected dataframe from databyregion
    
    Returns: 
    
    All plots comprised of partially and fully vaccinated over the 39 week interval
    
    '''
    
    
    plt.figure(figsize=(20,10))
    plt.title(f"Normalized percentage of Partial/Fully Vaccinated with Respect to population in {region(regn)} Over 39 Weeks", fontsize=12)
    plt.plot('week_end','NPart', data=dataframe, label='Fully Vaxed', linestyle='-', marker='o')
    
  
    plt.plot('week_end','NFully', data=dataframe, label='Partially Vaxed', linestyle='-', marker='o')
   

    plt.legend()
    return plt


def findMaxFully(dataframe):
    '''
    This method will take a cleaned data frame and iterate through all the unique regions, and will create a new data frame containing the prename, the week of the max of partial or fully 
    
    argument 1 (DataFrame): Input whole uncleaned dataframe
    
    Returns:
    
    (DataFrame): Comprised of the max weeks for fully vaccinated by each region
    
    '''
    #first we are going to take our data frame and find its unique regions
    regionid = dataframe['pruid'].unique()
    
    #this new dataframe will store our max week and number of fully vaccinated
    data1 = pd.DataFrame(columns= ['Region','Week', 'NumFully'])
    
    for e in regionid:
        #here we create our dataframe based on the regions found in regionid 
        dt = databyRegion(dataframe, e)
        
        #We wish to find the max element in column sumTotful
        column = dt['sumTotFul']

        #We can call max() on this column to return our max value efficently
        max_val = column.max()
        
        #We use idxmax() to find the index position of the max element in order to determine its corresponding week
        Col_ind = column.idxmax()
        
        #We can now use the index position to find the week
        week = dt[(dt.index == Col_ind)]
        #Since week is returned as a pandas datatime, we get excessive string characters that are not needed
        week2 = str(week['week_end'])
        #Hence we string splice then enter this splice into our new frame
        week3 = week2[3:15]
        reg = region(e)
        
        data1 = data1.append({'Region':reg, 'Week':week3, 'NumFully':max_val}, ignore_index=True)
        #This process will iterate over each region
        
    #this will clear away any string literals that get past our splicing procedure
    data1['Week'].replace(regex=True, inplace=True, to_replace=r'[^0-9.\-]',value=r'')
    data1['Week'] = data1['Week'].astype(str)
    
    data1['Week'] = data1['Week'].apply(pd.to_datetime)

    return data1


def findMaxPartial(dataframe):
    '''
    This method will take a cleaned data frame and iterate through all the unique regions, and will create a new data frame containing the prename, the week of the max of partial or fully 
    
    argument 1 (DataFrame): Input whole uncleaned dataframe
    
    Returns:
    
    (DataFrame): Comprised of the max weeks for Partially vaccinated by each region
    
    '''
    
     #first we are going to take our data frame and find its unique regions
    regionid = dataframe['pruid'].unique()
    
    #this new dataframe will store our max week and number of fully vaccinated
    data1 = pd.DataFrame(columns= ['Region','Week', 'NumPartially'])
    
    for e in regionid:
        #here we create our dataframe based on the regions found in regionid 
        dt = databyRegion(dataframe, e)
        
        #We wish to find the max element in column sumTotful
        column = dt['sumTotPartially']

        #We can call max() on this column to return our max value efficently
        max_val = column.max()
        
        #We use idxmax() to find the index position of the max element in order to determine its corresponding week
        Col_ind = column.idxmax()
        
        #We can now use the index position to find the week
        week = dt[(dt.index == Col_ind)]
        #Since week is returned as a pandas datatime, we get excessive string characters that are not needed
        week2 = str(week['week_end'])
        #Hence we string splice then enter this splice into our new frame
        week3 = week2[3:15]
        reg = region(e)
        
        data1 = data1.append({'Region':reg, 'Week':week3, 'NumPartially':max_val}, ignore_index=True)
        #This process will iterate over each region
    
    #this will clear away any string literals that get past our splicing procedure
    data1['Week'].replace(regex=True, inplace=True, to_replace=r'[^0-9.\-]',value=r'')
    data1['Week'] = data1['Week'].astype(str)
    
    data1['Week'] = data1['Week'].apply(pd.to_datetime)
    

    return data1


def showRelationship(dataframe):
    '''
    This method will display a joint plot between the change in partially vacinated vs fully vaccinated, from here we can see the relative assent to fully vaccinated by examining the two slopes that form from our resultant graph. This method will take a databyregion dataframe and produce a seaborn jointplot 
    
    argument 1 (DataFrame): This data frame must be specific to each region
    
    Returns:
    
    A Seaborn joint plot, showing the relationship between partially and fully vaccinated in each region.
    '''
    
    sns.jointplot(x='sumTotFul', y='sumTotPartially', data=dataframe, kind='reg')
    
    return plt


def calc_rel_vac(dataF):
    
    '''
    We are going to create data frames with the normalized percentage of vacinated with respect to the population
    
    
    '''
    popdat = pd.read_csv("../data/raw/QuartPopData.csv", thousands=',').drop('Geography', 1)

    da1 = pd.read_csv("../data/raw/QuartPopData.csv", thousands=',')

    stdPop = pd.DataFrame(popdat.std(axis=1), columns=['Standard Deviation'])
    meanPop = pd.DataFrame(popdat.mean(axis=1), columns=['Mean 20/21'])

    ddd = da1.merge(meanPop, left_index=True, right_index=True).merge(stdPop,  left_index=True, right_index=True)
    #ddd now contains the mean and std of each row or each region
    return ddd

def popDict(reg1):
    '''
    We use this method to return the values of population within each region
    Arguments: Takes a region by name (String)
    
    Returns: (int) Population
    '''
    di = {'Canada':38246108, 'Newfoundland and Labrador':520553, 'Nova Scotia':992055,'Quebec':8604495,
       'Manitoba':1383765, 'Saskatchewan':1179844, 'British Columbia':5214805, 'Yukon':42986,
      'Northwest Territories':45504, 'Nunavut':39403, 'Prince Edward Island':164318,
       'New Brunswick':789225, 'Alberta':4442879, 'Ontario':14826276}
    
    return di[reg1]


def graph3( dataf ):
    
    plt.figure(figsize=(16, 10))
    plt.title("Total Number of Fully Vacinated")
    g = sns.scatterplot(x='week_end', 
                        y='sumTotFul', 
                        hue='Region', 
                        data=dataf,
                        palette='pastel').set_xticklabels(range(39))
    plt.legend()
    return plt


def graph4( dataf ):
    plt.figure(figsize=(16, 10))
    plt.title("Total Number of Fully Vacinated with Respect to Population")
    g = sns.scatterplot(x='week_end',
                        y='NFully', 
                        hue='Region',
                        data=dataf, 
                        palette='pastel').set_xticklabels(range(39))
    plt.legend()
    return plt


def graph1( dataf ):
    plt.figure(figsize=(16, 10))
    plt.title("Total Number of Partially Vacinated")
    g = sns.scatterplot(x='week_end',
                        y='sumTotPartially', 
                        hue='Region',
                        data=dataf, 
                        palette='pastel').set_xticklabels(range(39))
    plt.legend()
    return plt


def graph2( dataf ):
    plt.figure(figsize=(16, 10))
    plt.title("Total Number of Partially Vacinated with Respect to Population")
    g = sns.scatterplot(x='week_end',
                        y='NPart', 
                        hue='Region',
                        data=dataf, 
                        palette='pastel').set_xticklabels(range(39))
    plt.legend()
    return plt


def showCh(dataframe):
    '''
    This method will display a joint plot between the change in partially vacinated vs fully vaccinated, from here we can see the relative assent to fully vaccinated by examining the two slopes that form from our resultant graph. This method will take a databyregion dataframe and produce a seaborn jointplot 
    
    argument 1 (DataFrame): This data frame must be specific to each region
    
    Returns:
    
    A Seaborn joint plot, showing the relationship between Normalized partially and fully vaccinated in each region.
    '''
    
    sns.jointplot(x='NFully', y='NPart', 
                      data=dataframe, 
                      hue='Region', 
                      palette='pastel', legend=False)
   
   
    
    
    return plt