# File: stockMarketStimulator.py
# A program that simulates stock market trading!

from math import floor


def open_file(filename):
    """ Opens a file according to filename, returns the file object.
        Args:
            filename: A string for the filename to be opened.
        Returns:
            file object corresponding to filename provided.
    """
    infile = open(filename, "r")
    return infile


def read_file(file):
    """ Reads a file by lines.
        Args:
            file: A file object to be read.
        Returns:
            A list of lines where each line has been split by commas.
    """
    lines = file.readlines()  # contains list of lines
    lines[0] = lines[0].split(',')[:-1]  # splits by comma
    for i in range(len(lines[0])):
        lines[0][i] = lines[0][i].lower()  # labels in first row now lowercase
    # processes every line after first one
    for i in range(1, len(lines)):
        lines[i] = lines[i].split(',')  # splits by comma
        # first column is a string, no casting needed. others casted as needed
        for j in range(1, len(lines[i]) - 1):
            lines[i][j] = float(lines[i][j])
        lines[i][-1] = int(lines[i][-1])
    return lines


def access(data, col, day):
    """Accesses stock data @ specified column @ specified day
    Args:
        data: A list of list containing processed stock data
        col: A string of either "date", "open", "high", "low", "close",
             "volume", or "adj_close" for the column of stock market data to
             look into.
        day: An integer reflecting the absolute number of the day in the
             data to look up, e.g. day 1, 15, or 1200 is row 1, 15, or 1200
             in the file.
    Returns:
        column value @ specified day. Type is variable depending on column.
    """
    column = data[0].index(col)  # returns column # of label searched for
    value = data[day][column]
    return value


def transact(funds, stocks, qty, price, buy=False, sell=False):
    """A bookkeeping function to help make stock transactions.

       Args:
           funds: An account balance, a float; it is a value of how much money
           you have currently.

           stocks: An int, representing the number of stocks you currently own.

           qty: An int, representing how many stocks you wish to buy or sell.

           price: A float reflecting a price of a single stock.

           buy: This option parameter, if set to true, will initiate a buy.

           sell: This option parameter, if set to true, will initiate a sell.

       Returns:
           Two values *must* be returned. The first (a float) is the new
           account balance (funds) as the transaction is completed. The second
           is the number of stock now owned (an int) after the transaction is
           complete.

           Error condition #1: If the `buy` and `sell` keyword parameters
           are both set to true, or both false. You *must* print an error
           message, and then return the `funds` and `stocks` parameters
           unaltered. This is an ambiguous transaction request!

           Error condition #2: If you buy, or sell without enough funds or
           stocks to sell, respectively.  You *must* print an error message,
           and then return the `funds` and `stocks` parameters unaltered. This
           is an ambiguous transaction request!
    """
    if buy == sell:
        # error condition 1
        return funds, stocks
    if buy is True:
        total_price = qty*price
        if total_price > funds:
            # error condition 2
            return funds, stocks
        else:
            # trade simulation
            funds = funds - total_price
            stocks = stocks + qty
            return funds, stocks

    else:
        # if not buy, must sell
        total_price = qty*price
        if qty > stocks:
            # error condition 2
            return funds, stocks
        else:
            # trade simluation
            funds = funds + total_price
            stocks = stocks - qty
            return funds, stocks


def alg_moving_average(filename):
    """This function implements the moving average stock trading algorithm.

    Algorithm:
    - Trading starts on day 21, taking the average of the previous 20 days.
    - Buy shares if current day price is 5%+ lower than moving average.
    - Sell shares if current day price is 5%+ higher than moving average.
    - We buy, or sell 10 stocks per transaction.
    - We choose open column of stock data

    Args:
        A filename, as a string.

    Returns:
        Two values, stocks and balance

    Prints:
        Nothing.
    """

    file = open_file(filename)
    lines = read_file(file)

    # Initializing cash balance and stock
    cash_balance = 1000
    stocks_owned = 0
    days = range(1, len(lines))  # Will iterate over this many days
    average = 0
    running_sum = 0
    current_day_price = 0
    for day in days:
        current_day_price = access(lines, "open", day)
        if day <= 20:
            # No trading before the 21st day
            running_sum = running_sum + current_day_price
            average = running_sum/day
        else:
            if day == len(lines) - 1:
                # Sell all stocks on the last day
                cash_balance, stocks_owned = transact(cash_balance,
                                                      stocks_owned,
                                                      stocks_owned,
                                                      current_day_price,
                                                      sell=True)
            else:
                if current_day_price <= 0.95*average:
                    # Buy if price is lower than 95% of average
                    cash_balance, stocks_owned = transact(cash_balance,
                                                          stocks_owned, 10,
                                                          current_day_price,
                                                          buy=True)
                elif current_day_price >= 1.05*average:
                    # Sell if price is higher than 105% of average
                    cash_balance, stocks_owned = transact(cash_balance,
                                                          stocks_owned, 10,
                                                          current_day_price,
                                                          sell=True)
                # Update average for every day
                running_sum = running_sum + current_day_price \
                    - access(lines, "open", day-20)
                average = running_sum/20
    return stocks_owned, cash_balance


def alg_mine(filename):
    """This function implements the student's custom trading algorithm.

    Using the CSV stock data that should be loaded into your program, use
    that data to make decisions using your own custome trading algorithm.

    Args:
        A filename, as a string.

    Algorithm:
        This algorithm leans on general market performance across different
        companies to make a trading decision. Simply put, MSFT and AAPL, being
        competitors in the same market, are likely to display some correlation
        between their stock performance - regardless of whether or not this
        correlation is causal.

        As such, this algorithm creates forecasts for the current day AAPL
        stock price by creating a linear regression relationship between AAPL
        and MSFT stock prices over a moving window of 30 days. AAPL (y) and
        MSFT (x) stock prices are hence expressed like this:
            y = ax + b  # 'a' and 'b' define the linear relationship

        Trading decisions are made according to this rubric:

            - If present day price is lower than forecasted price:
                Buy floor(1.25*(%difference) + 3.75) amount of stock or 10
                stocks, whichever is smaller
            - If present day price is higher than forecasted price:
                Sell floor(1.25*(%difference) + 3.75) amount of stock or 10
                stocks, whichever is smaller

        The equation to determine how many stocks to buy/sell simply scales
        the amount of stocks to the percentage difference (buy/sell more at
        larger margins)

    Returns:
        Two values, stocks and balance OF THE APPROPRIATE DATA TYPE.

    Prints:
        Nothing.
    """

    # Last thing to do, return two values: one for the number of stocks
    # owned after the simulation, and the amount of money you have after
    # the simulation.
    # Remember, all your stocks should be sold at the end!

    filename_2 = ""
    if filename == "AAPL.csv":
        filename_2 = "MSFT.csv"
    else:
        filename_2 = "AAPL.csv"
    file_1 = open_file(filename)
    lines_1 = read_file(file_1)
    file_2 = open_file(filename_2)
    lines_2 = read_file(file_2)

    # Initializing cash balance and stock
    cash_balance = 1000
    stocks_owned = 0
    # Will iterate over this many days
    days = range(1, len(lines_1))
    current_price_1 = 0
    current_price_2 = 0
    sum_1 = 0
    sum_2 = 0
    sum_square_1 = 0
    sum_square_2 = 0
    sum_product = 0
    window = 20
    # a & b define the linear regression
    a = 0
    b = 0
    # metrics used in the trading process
    predicted_price_1 = 0
    difference = 0
    trade_amount = 0
    for day in days:
        current_price_1 = access(lines_1, "open", day)
        current_price_2 = access(lines_2, "open", day)
        if day <= window:
            # No trading before the 21st day
            sum_1 += current_price_1
            sum_2 += current_price_2
            sum_square_1 += current_price_1 * current_price_1
            sum_square_2 += current_price_2 * current_price_2
            sum_product += current_price_1 * current_price_2
            a = (day * sum_product - sum_1 * sum_2)/(day * sum_square_2 -
                                                     sum_2 * sum_2 + 0.0001)
            b = (sum_1 * sum_square_2 - sum_2 * sum_product) / \
                (day * sum_square_2 - sum_2 * sum_2 + 0.0001)
        else:
            if day == len(lines_1) - 1:
                # Sell all stocks on the last day
                cash_balance, stocks_owned = transact(cash_balance,
                                                      stocks_owned,
                                                      stocks_owned,
                                                      current_price_1,
                                                      sell=True)
            else:
                predicted_price_1 = a * current_price_2 + b
                difference = abs(predicted_price_1 - current_price_1) / \
                    current_price_1 * 100
                trade_amount = min([10, floor(1.25 * difference + 3.75)])
                if current_price_1 < predicted_price_1:
                    # buy floor(1.25*(%diff) + 3.75) or 10, lower amt
                    cash_balance, stocks_owned = transact(cash_balance,
                                                          stocks_owned,
                                                          trade_amount,
                                                          current_price_1,
                                                          buy=True)
                elif current_price_1 > predicted_price_1:
                    # sell floor(1.25*(%diff) + 3.75) or 10, lower amt
                    cash_balance, stocks_owned = transact(cash_balance,
                                                          stocks_owned,
                                                          trade_amount,
                                                          current_price_1,
                                                          sell=True)

                # Update regression relationship every day
                sum_1 += current_price_1 - access(lines_1, "open", day - window)
                sum_2 += current_price_2 - access(lines_2, "open", day - window)
                sum_square_1 += current_price_1 * current_price_1 -     \
                    access(lines_1, "open", day - window)   \
                    * access(lines_1, "open", day - window)
                sum_square_2 += current_price_2 * current_price_2 -     \
                    access(lines_2, "open", day - window)   \
                    * access(lines_2, "open", day - window)
                sum_product += current_price_1 * current_price_2        \
                    - access(lines_1, "open", day - window) *\
                    access(lines_2, "open", day - window)
                a = (window * sum_product - sum_1 * sum_2) / \
                    (window * sum_square_2 - sum_2 * sum_2 + 0.0001)
                b = (sum_1 * sum_square_2 - sum_2 * sum_product) / \
                    (window * sum_square_2 - sum_2 * sum_2 + 0.0001)

    return stocks_owned, cash_balance


def main():
    # My testing will use AAPL.csv or MSFT.csv
    filename = input("Enter a filename for stock data (CSV format): ")

    # Call your moving average algorithm, with the filename to open.
    alg1_stocks, alg1_balance = alg_moving_average(filename)
    alg_mine_stocks, alg_mine_balance = alg_mine(filename)

    # Print results of the moving average algorithm, returned above:
    print("Cash balance: {0:0.2f}, Stocks owned: {1}".format(alg1_balance,
                                                             alg1_stocks))
    print("Cash balance: {0:0.2f}, Stocks owned: {1}".format(alg_mine_balance,
                                                             alg_mine_stocks))
if __name__ == '__main__':
    main()
