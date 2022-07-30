import pandas as pd
import numpy as np
import datetime
import matplotlib.pyplot as plt
import math

#Declaring the Hyperparameters

N = 50
T = 7
R = 0.8
M = 5
F = 0.0005   # 0.5% Brokerage fee

def GetData(NameOfFile):
    data = pd.read_csv(f"../{NameOfFile}.csv", usecols=['datadate', 'adjcp', 'tic'])

    return data  # pd.DataFrame Object

data = "DATA"
dataframe = GetData(data)


def PartitionData(Data):
  
    dates = Data.datadate.unique()
    DateToIndex = {dates[key]:key for key in range(0, len(dates))}
    partitioned_data = []
    for i in range(0, len(dates)):
        df = Data[Data["datadate"] == dates[i]]
        partitioned_data.append(df)


    return partitioned_data, DateToIndex  # List containing of the Data Partitioned according to Date, and the Dictionary mapping Dates to their index in the list




def GetMomentumBasedPriority(PartitionedDataFrameList, DateToIndex ,today):
    # PartitionedDataFrameList : Pandas DataFrame, The Output of your last function
    # DateToIndex : Dictionary mapping dates to their index in the PartitionedDataFrameList
    # today :  Today's date (string) In Format: YYYYMMDD


    #NdaysAgo is a datatime.date() object contining the required data, you need to convert it to a string and then check if its
    #actually there in the Data you have or will you have to get going using some other nearest date

    NdaysAgo = datetime.date(int(today[0:4]),int(today[4:6]),int(today[6:])) + datetime.timedelta(days = -N)
    NdaysAgostr = NdaysAgo.strftime("%Y%m%d")

    tic_list = []
    for i in range(0, 30): #creating list with all the ticket names
        tic_list.append(PartitionedDataFrameList[0]["tic"][i])
    


    mean_list = []
    final_values = []
    alt_Ndaysago = NdaysAgostr
    if int(NdaysAgostr) in DateToIndex: #calculating momentum
        for j in range(0,30):  #calculating mean values of each ticket
                sum = 0
                for i in range(DateToIndex[int(NdaysAgostr)], DateToIndex[int(today)] + 1):
                    sum += PartitionedDataFrameList[i]["adjcp"].iloc[j]

                sum = sum/50
                mean_list.append(sum)
                j += 1

        for i in range(0, 30):
            momentum = PartitionedDataFrameList[DateToIndex[int(today)]]["adjcp"].iloc[i] - PartitionedDataFrameList[DateToIndex[int(NdaysAgostr)]]["adjcp"].iloc[i]
            final_val = momentum/mean_list[i]
            final_values.append(final_val)

    else:
        j = 1
        while int(alt_Ndaysago) not in DateToIndex:
            if alt_Ndaysago%100 <25:
                alt_Ndaysago += 1
            else:
                alt_Ndaysago -= 1
            j+=1
        
        for i in range(0, 30):
            momentum = PartitionedDataFrameList[DateToIndex[int(today)]]["adjcp"].iloc[i] - PartitionedDataFrameList[DateToIndex[int(alt_Ndaysago)]]["adjcp"].iloc[i]
            for j in range(0,30):  #calculating mean values of each ticket
                sum = 0
                for i in range(DateToIndex[int(alt_Ndaysago)], DateToIndex[int(today)] + 1):
                    sum += PartitionedDataFrameList[i]["adjcp"].iloc[j]

                sum = sum/(DateToIndex[int(today)] + 1 - DateToIndex[int(alt_Ndaysago)])
                mean_list.append(sum)
                j += 1
            final_val = momentum/mean_list[i]
            final_values.append(final_val)



    return np.array([tic_list, final_values])  #Numpy Array containing the Momentum divided by mean(in the N-day period considered) of all the 30 tickers, i


today = "2020" + datetime.date.today().strftime("%m%d")
date_to_index_dict = PartitionData(dataframe)[1]
partitioned_data_list = PartitionData(dataframe)[0]


price_list = []
today_date_index = date_to_index_dict[int(today)]
for i in range(0, 30): #creating list with all the prices of tickets
    price_list.append(partitioned_data_list[today_date_index]["adjcp"].iloc[i])


weights = GetMomentumBasedPriority(partitioned_data_list, date_to_index_dict, today)
ticket_names = weights[0].tolist()
ticket_weights = weights[1].tolist()
indexes_top5 = []
top5_weights = []
top5_names = []
for k in range(0, 5):
    max = 0
    for i in range(0,30):
        if float(ticket_weights[i]) > max:
            max = float(ticket_weights[i])

    top5_weights.append(max)
    for i in range(0, 30):
        if str(max) == ticket_weights[i]:
            index = i

    top5_names.append(ticket_names[index])
    ticket_weights[index] = -100
    indexes_top5.append(index)
array_weights_top5 = np.array([top5_names, top5_weights])
print(indexes_top5)


def GetBalanced(prices, weights,balance):
    # prices : Numpy array containing Prices of all the 30 Stocks
    # weights : Multi-hot Numpy Array : The Elements corresponding to stocks which are to be bought(Top M Stocks with positive Momentum Indicator) are set to their priority, All other elements are set to zero.
    # Returns Numpy array containing the number of shares to buy for each stock!
    sum = 0
    for i in range(0, len(weights[1])):
        sum += float(weights[1][i])
    number = []
    for j in range(0, len(weights[1])):
        number_of_stocks = math.floor(((weights[1][j]/sum)*balance*(R))/prices[indexes_top5[j]]) 
        number.append(number_of_stocks)

    return number




class PortFolio:


    def __init__(self):
        self.initial_balance
        self.current_balance = 100000
        self.stocks_owned = []
        self.stock_prices = price_list


    def SellStock(self, index):
        #index : The index of the Stock to sell (0-29)
        amount = (self.stocks_owned[index])*(self.stock_prices[index])
        self.current_balance += amount*(1-F)
        self.stocks_owned[index] = 0
        
  
    def BuyStock(self, index, number):
        #index : The index of the Stock to buy (0-29) 
        #number : Number of shares to buy (float)
        amount = (self.stock_prices[index])*(number)
        self.current_balance -= amount(1+F)
        self.stocks_owned[index] += number


    def CalculateNetWorth(self, prices):
        #Return Net Worth (All Shares' costs+ Balance)
        cost = 0
        for i in range(0,30):
            cost += (self.stocks_owned[i])*(prices[i])

        return cost + self.current_balance
        


    def ChangePricesTo(self, newPriceVector):
        # newPriceVector : Numpy array containing the prices of all the stocks for the current day
        self.stock_prices = newPriceVector


    def RebalancePortFolio(self, newWeights):  
        # newWeights : Numpy array containing Momentum/Mean for all stocks in the N-day period
        # First sell all your pre-owned Stock (make sure to take transaction fee into account!)
        # This would change your total balance
        # Then take the top M(/might be less than M, if >(30-M) had negative Momentum) and send them to the GetBalanced() Function
        # Then take that output and pass them to the BuyStocks function!

        for i in range(0, 30):  #selling all the stocks owned
            amount = (self.stocks_owned[i])*(self.stock_prices[i])
            self.current_balance += amount*(1-F)
            self.stocks_owned[i] = 0

        list_of_stocks = GetBalanced(price_list, array_weights_top5, self.current_balace)
        for i in range(0, M):
            self.BuyStock(indexes_top5[i], list_of_stocks[i])





myPortfolio = PortFolio()
NetWorthAfterEachTrade = []


#First Get the Data
data = "DATA"
Data = GetData(data)
PartitionedData, DateToIndex= PartitionData(Data)


NdaysAgo = datetime.date(int(today[0:4]),int(today[4:6]),int(today[6:])) + datetime.timedelta(days = -N)
NdaysAgostr = NdaysAgo.strftime("%Y%m%d")
prices = []
#Start processing from the (N+1)th Day(among the ones recorded in the Data)
for i in range(PartitionData[DateToIndex[int(NdaysAgostr)] + 1], PartitionData[DateToIndex[int(today)] + 1]):
    # Change the Prices to the ith Term
    for k in range(0, 30):
        prices.append(i["adjcp"][k])
    
    # Get NetWorth and store in list
        NetWorthAfterEachTrade.append(myPortfolio.CalculateNetWorth(prices[k]))
    # Check if you need to rebalance Portfolio's Today
    if i in range(PartitionData[DateToIndex[int(NdaysAgostr)] + 1], PartitionData[DateToIndex[int(today)] + 1], T):
    # If so, do it by Calling first the GetMomentumBasedPriority function and then passing it to the rebalance function
        newWeights = GetMomentumBasedPriority(PartitionedData, DateToIndex, today)
        PortFolio.RebalancePortFolio(newWeights)


