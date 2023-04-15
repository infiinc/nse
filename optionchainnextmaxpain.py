import time
import pandas as pd
from flask import Flask, render_template

def process_data():
    # Read the data from a CSV file
    data = pd.read_csv('sorted_data.csv')
    data = data.sort_values(by='Strike Price', ascending=False)
    
    # Calculate the change in open interest and price for Call and Put sides separately
    data['Call OI Change'] = data['Call ChgOpeni']
    data['Call Price Change'] = data['Call per.chg']
    data['Put OI Change'] = data['Put ChgOpeni']
    data['Put Price Change'] = data['Put per.chg']
    # Calculate the total change in open interest for Call and Put sides
    data['Total Call OI Change'] = data['Call ChgOpeni'].sum()
    data['Total Put OI Change'] = data['Put ChgOpeni'].sum()
    # Identify short covering, long build-up, long unwinding, and short build-up for Call and Put sides separately
    data['Call Signal'] = ''
    data.loc[(data['Call ChgOpeni'] < 0) & (data['Call per.chg'] > 0), 'Call Signal'] = 'Short Covering'
    data.loc[(data['Call ChgOpeni'] > 0) & (data['Call per.chg'] > 0), 'Call Signal'] = 'Long Build-up'
    data.loc[(data['Call ChgOpeni'] > 0) & (data['Call per.chg'] < 0), 'Call Signal'] = 'Long Unwinding'
    data.loc[(data['Call ChgOpeni'] < 0) & (data['Call per.chg'] < 0), 'Call Signal'] = 'Short Build-up'

    data['Put Signal'] = ''
    data.loc[(data['Put ChgOpeni'] < 0) & (data['Put per.chg'] > 0), 'Put Signal'] = 'Short Covering'
    data.loc[(data['Put ChgOpeni'] > 0) & (data['Put per.chg'] > 0), 'Put Signal'] = 'Long Build-up'
    data.loc[(data['Put ChgOpeni'] > 0) & (data['Put per.chg'] < 0), 'Put Signal'] = 'Long Unwinding'
    data.loc[(data['Put ChgOpeni'] < 0) & (data['Put per.chg'] < 0), 'Put Signal'] = 'Short Build-up'
    
    # Calculate the total change in open interest for Call and Put sides
    data['Total Call OI Change'] = data['Call ChgOpeni'].sum()
    data['Total Put OI Change'] = data['Put ChgOpeni'].sum()
    # Combine the Call and Put signals
    data['Signal'] = data['Call Signal'] + ' ' + data['Put Signal']
    return data
def calculate_max_pain(df):
    # Calculate max pain for each strike price
    df['put_pain'] = df.apply(lambda row: max(row['Strike Price'] - df.loc[df['Strike Price'] <= row['Strike Price'], 'Put LTP'].index) * row['Put Volume'], axis=1)
    df['call_pain'] = df.apply(lambda row: max(df.loc[df['Strike Price'] >= row['Strike Price'], 'Call LTP'].index - row['Strike Price']) * row['Call Volume'], axis=1)
    df['total_pain'] = df['put_pain'] + df['call_pain']
     # Find strike price with minimum total pain
    max_pain_strike = df.loc[df['total_pain'] == df['total_pain'].min(), 'Strike Price'].iloc[0]
    return max_pain_strike
# Read the data from a CSV file
data = pd.read_csv('nextsorted_data.csv')
def calculate__next_max_pain(df):
    # Calculate max pain for each strike price
    df['put_pain'] = df.apply(lambda row: max(row['Strike Price'] - df.loc[df['Strike Price'] <= row['Strike Price'], 'Put LTP'].index) * row['Put Volume'], axis=1)
    df['call_pain'] = df.apply(lambda row: max(df.loc[df['Strike Price'] >= row['Strike Price'], 'Call LTP'].index - row['Strike Price']) * row['Call Volume'], axis=1)
    df['total_pain'] = df['put_pain'] + df['call_pain']
    
    # Find strike price with minimum total pain
    nextsorted_data = pd.read_csv('nextsorted_data.csv')
    nextsorted_data['Strike Price'] = nextsorted_data['Strike Price'].astype(float)
    df['Strike Price'] = df['Strike Price'].astype(float)
    merged_data = pd.merge(df, nextsorted_data, on='Strike Price')
    next_max_pain_strike = merged_data.loc[merged_data['total_pain'] == merged_data['total_pain'].max(), 'Strike Price'].iloc[0]
    
    return next_max_pain_strike

# Create a Flask web application
app = Flask(__name__)

# Define a route to display the data in a table format
@app.route('/')

def index():
    # Refresh the data every 10 seconds
    time.sleep(10)
    data = process_data()
    spot_value = data.loc[0, 'Spot']
    max_pain_strike = calculate_max_pain(data)
    # Calculate the sum of change in open interest for call and put options
    call_oi_change = data['Call ChgOpeni'].sum()
    put_oi_change = data['Put ChgOpeni'].sum()
    #prev_highest_call_strike = session.get('prev_highest_call_strike', 'None')
    #prev_highest_put_strike = session.get('prev_highest_put_strike', 'None')
    max_call_oi_strike = data.loc[data['Call Openi'] == data['Call Openi'].max(), 'Strike Price'].iloc[0]
    max_put_oi_strike = data.loc[data['Put Openi'] == data['Put Openi'].max(), 'Strike Price'].iloc[0]
    
    # load data from nextsorted_data.csv
    nextsorted_data = pd.read_csv('nextsorted_data.csv')
    # find the strike price with maximum Call Open Interest
    next_max_call_oi_strike = nextsorted_data.loc[nextsorted_data['Call Openi'] == nextsorted_data['Call Openi'].max(), 'Strike Price'].iloc[0]

    # find the strike price with maximum Put Open Interest
    next_max_put_oi_strike = nextsorted_data.loc[nextsorted_data['Put Openi'] == nextsorted_data['Put Openi'].max(), 'Strike Price'].iloc[0]

    # Find the strike price with the maximum total pain
    next_max_pain_strike = calculate__next_max_pain(nextsorted_data)
    
    # Check if the spot value is near the highest open interest call strike price or the highest open interest put strike price
    threshold = 100
    alert_message = None
    
    if abs(spot_value - max_call_oi_strike) < threshold:
        alert_message = f'Spot value is near the highest open interest call strike price {max_call_oi_strike}'
        
    elif abs(spot_value - max_put_oi_strike) < threshold:
        alert_message = f'Spot value is near the highest open interest put strike price {max_put_oi_strike}'
        
              
    return render_template('index.html', data=data, spot_value=spot_value, max_pain=max_pain_strike,
                           highest_call_strike=max_call_oi_strike, highest_put_strike=max_put_oi_strike,
                           #prev_highest_call_strike=prev_highest_call_strike, prev_highest_put_strike=prev_highest_put_strike,
                           call_oi_change=call_oi_change, put_oi_change=put_oi_change,Next_max_pain=next_max_pain_strike,next_highest_call_strike=next_max_call_oi_strike,next_highest_put_strike=next_max_put_oi_strike, alert_message=alert_message)
if __name__ == '__main__':
    app.run(debug=True)
