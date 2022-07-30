import pandas as pd
import mplfinance as mplf

df = pd.read_csv("C:/ISHAANVI/SOC/AAPL.csv")
df.Date = pd.to_datetime(df.Date)
del df['Adj Close']


def plot_chart(period, train):
    global df

    if train == True:
        i = 0
    else:
        i= 1000

    while i < 1000:
        buffer_df = df.loc[i : i + period - 1]
        buffer_df = buffer_df.set_index('Date')

        if (df['Close'][i] - df['Close'][i + period - 1]) <= 0:
            mplf.plot(buffer_df, figratio = (50, 50), type = 'candle', volume = False, 
            style = 'yahoo', savefig = f'C:/ISHAANVI/SOC/train/sell/chart-{period}days-{int(i/period)}.png')
        
        else:
            mplf.plot(buffer_df, figratio = (50, 50), type = 'candle', volume = False, 
            style = 'yahoo', savefig = f'C:/ISHAANVI/SOC/train/buy/chart-{period}days-{int(i/period)}.png')

        i = i + period

    while i>=1000 and i + period - 1 < 1257:
        buffer_df = df.loc[i : i + period - 1]
        buffer_df = buffer_df.set_index('Date')

        if (df['Close'][i] - df['Close'][i + period - 1]) <= 0:
            mplf.plot(buffer_df, figratio = (50, 50), type = 'candle', volume = False, 
            style = 'yahoo', savefig = f'C:/ISHAANVI/SOC/test/sell/chart-{period}days-{int((i-1000)/period)}.png')

        else:
            mplf.plot(buffer_df, figratio = (50, 50), type = 'candle', volume = False, 
            style = 'yahoo', savefig = f'C:/ISHAANVI/SOC/test/buy/chart-{period}days-{int((i-1000)/period)}.png')

        i = i + period


plot_chart(20, True)
plot_chart(10, True)
plot_chart(5, True)

plot_chart(20, False)
plot_chart(10, False)
plot_chart(5, False)
