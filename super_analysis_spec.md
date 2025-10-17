# Superannuation Analysis Tool

The superannuation analysis application uses montecarlo simulation to calculate the best combination of strategic superannuation investments over a certain time period.

## Model Parameters

Investment Option a choice of the following:

- Growth
- Balanced
- Conservative Balanced
- Stable
- Secure

Each investment option has the following attributes:

- return target: a percentage return above inflation on a 10 year rolling average
- risk measure: negative returns expected every x years over a 20 year period

Global variables:

- inflation rate: the expected inflation rate on a 10 year rolling average
- negative return: the expected percentage of a negative return
- investment: the amount invested in superannuation
- timeperiod: the timeframe for the simulation

## Model Outcomes

Based on the attributes of each investment option, and the global parameters the model will determine the optimal investment option mix and provide the percentage of the investment that should be allocated to each investment option in the optimal investment option mix.

The number of combinations of investment options is large. The application should prefer speed over accuracy. Consider another variable that the user can set being the number of iterations of the montecarlo simulation model.

## Model UI

The model UI will allow the user to input the amount of investment and timeperiod. The other parameters will be held in a configuration file either in json or yaml format.

## Technology Stack

There are no preferences for the UI framework of development language. The application will run in a windows environment. Currently installed languages and frmeworks include python, node, flutter and dart.
