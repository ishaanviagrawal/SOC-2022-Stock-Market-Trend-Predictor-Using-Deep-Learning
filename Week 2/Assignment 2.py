from statistics import correlation
import numpy as np
import pandas as pd
import datetime
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import pearsonr

T = 60
P = 7
M = 4
R = 0.8
F = 0.0005


def GetData(NameOfFile):
    data = pd.read_csv(f"C:/Users/Ishaanvi/Downloads/SOC-22-main/SOC-22-main/Week-2/{NameOfFile}.csv", usecols=['datadate', 'tic', 'adjcp'])

    return data  # pd.DataFrame Object


def PartitionData(Data):
  
    dates = Data.datadate.unique()
    DateToIndex = {dates[key]:key for key in range(0, len(dates))}
    partitioned_data = []
    for i in range(0, len(dates)):
        df = Data[Data["datadate"] == dates[i]]
        partitioned_data.append(df)


    return partitioned_data, DateToIndex  # List containing of the Data Partitioned according to Date, and the Dictionary mapping Dates to their index in the list


data = "DATA"
Data = GetData(data)
PartitionedData, DateToIndex= PartitionData(Data)



def Switch(firstStock, SecondStock, today ,PartitionedDataFrames):

    momentum_first = PartitionedDataFrames[DateToIndex[int(today)]]["adjcp"].iloc[firstStock] - PartitionedDataFrames[DateToIndex[int(today)] - 50]["adjcp"].iloc[firstStock]
    momentum_second = PartitionedDataFrames[DateToIndex[int(today)]]["adjcp"].iloc[SecondStock] - PartitionedDataFrames[DateToIndex[int(today)] - 50]["adjcp"].iloc[SecondStock] 
    
    sum_first = 0
    for i in range(DateToIndex[int(today)] - 50, DateToIndex[int(today)] + 1):
        sum_first += PartitionedDataFrames[i]["adjcp"].iloc[firstStock]

        sum_first = sum_first/50

    sum_second = 0
    for i in range(DateToIndex[int(today)] - 50, DateToIndex[int(today)] + 1):
        sum_second += PartitionedDataFrames[i]["adjcp"].iloc[SecondStock]

        sum_second = sum_second/50

    momentum_first = momentum_first/sum_first
    momentum_second = momentum_second/sum_second



    if momentum_first>momentum_second:
        return firstStock
    else:
        return SecondStock     #One of two(firstStock/SecondStock) depending on which should grow more in the future.



today = "2020" + datetime.date.today().strftime("%m%d")

date_to_index_dict = PartitionData(Data)[1]
partitioned_data_list = PartitionData(Data)[0]

price_list = []
today_date_index = date_to_index_dict[int(today) - 2]
for i in range(0, 30): #creating list with all the prices of tickets
    price_list.append(partitioned_data_list[today_date_index]["adjcp"].iloc[i])


class PortFolio:
    def __init__(self): 
        #Initialize all variables
        self.initial_balance = 100000
        self.current_balance = 100000
        self.stocks_owned = []
        self.stock_prices = np.array(price_list) 
        self.negatively_correlated_stocks = []
        self.stock_pairs_owned = []


    def SellStock(self, index):
        #index : The index of the Stock to sell (0-29)
        amount = (self.stocks_owned[index])*(self.stock_prices[index])
        self.current_balance += amount*(1-F)
        self.stocks_owned[index] = 0
    
    def BuyStock(self,index, number):
        #index : The index of the Stock to buy (0-29) 
        #number : Number of shares to buy (float)
        amount = (self.stock_prices[index])*(number)
        self.current_balance -= amount(1+F)
        self.stocks_owned[index] += number

    def CalculateNetWorth(self):
        #Return Net Worth (All Shares' costs+ Balance)
        cost = 0
        for i in range(0,30):
            cost += (self.stocks_owned[i])*(self.stock_prices[i])

        return cost + self.current_balance



    def ChangePricesTo(self,newPriceVector):
        # newPriceVector : Numpy array containing the prices of all the stocks for the current day
        self.stock_prices = newPriceVector


    def ChangePairs(self, PartitionedDataFrame, today, Tday):  
        # Calls the Switch function for all the pairs of stocks owned
        pass




    
    def RebalancePortfolio(self):
        # Calculates the Co-relation Matrix and changes the list of pairs, which you'll be using to trade
        pivoted = Data.pivot('datadate', 'tic', 'adjcp').reset_index()
        corr_df = pivoted.corr(method='pearson')
        corr_df.head().reset_index()

        tic_list = []
        for i in range(0, 30): #creating list with all the ticket names
            tic_list.append(PartitionedData[0]["tic"][i])
        
        # You'll have to take care of cases, where a single stock would be involved in two or more of the most negatively co-related Stocks
        buffer_stocks = []
        for i in range(0, 30): #taking care of first index
            corr = 0
            for j in range(0, 30):
                correlation = corr_df[tic_list[i]][tic_list[j]]
                if  correlation < corr:
                    corr = correlation
                    second_index = j
            if corr<0:
                buffer_stocks.append((i, second_index))
        
        for i in range(0, 30): #taking care of second index
            corr = 0
            for k in range(0, len(buffer_stocks)):
                if buffer_stocks[k][1] == i:
                    if corr_df[tic_list[buffer_stocks[k][0]]][tic_list[buffer_stocks[k][1]]] < corr:
                        corr = corr_df[tic_list[buffer_stocks[k][0]]][tic_list[buffer_stocks[k][1]]]
                        first_index = buffer_stocks[k][0]
            if corr<0:
                self.negatively_correlated_stocks.append((first_index, i))
        
        for (a, b) in self.negatively_correlated_stocks: #only unique pairs
            if (b, a) in self.negatively_correlated_stocks:
                self.negatively_correlated_stocks.remove((b, a))


        
        # It would be a good idea, to call BuyStock and SellStock from here itself, instead of calling ChangePairs later as it will cause havoc that way
        for i in range(0, len(self.stocks_owned)):
            self.SellStock(i)

        for i in range(0, len(self.negatively_correlated_stocks)):
            index = Switch(self.negatively_correlated_stocks[i][0], self.negatively_correlated_stocks[i][0], today - 2, PartitionedData)
            self.BuyStock(index, 10)






myPortfolio = PortFolio()
NetWorthAfterEachTrade = []

#First Get the Data
data = "DATA"
Data = GetData(data)
PartitionedData, DateToIndex= PartitionData(Data)

prices = []
#Start processing from the (T+1)th Day(among the ones recorded in the Data)
for i in range(PartitionData[DateToIndex[int(today)] - T + 1], PartitionData[DateToIndex[int(today)] + 1]):
    # Change the Prices to the ith Term
    for k in range(0, 30):
        prices.append(i["adjcp"][k])
    # Get NetWorth and store in list
        NetWorthAfterEachTrade.append(myPortfolio.CalculateNetWorth(prices[k]))
    # Check if you need to rebalance Portfolio's Today
    if i in range(PartitionData[DateToIndex[int(today)] -T + 1], PartitionData[DateToIndex[int(today)] + 1], P):
        myPortfolio.RebalancePortfolio()
    # Check if you need to switch stocks today



