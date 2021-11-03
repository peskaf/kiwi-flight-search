# Kiwi flight search

This module (solution.py) is capable of searching flights according to specified parameters (rules). User has to specify csv file with flights data, airport code of origin and airport code of destination. Optionally there can be specified whether there should be a return flight, min. number of pieces of baggage that has to be allowed on the whole trip and how many days should be between trip to and back from the destination (when return flight is selected, otherwise, this information is ignored). More on arguments below (help message of the program):

```
usage: solution.py [-h] [--bags BAGS] [--return] [--days_in_destination {1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31}] csv origin destination

positional arguments:
  csv                   CSV file with the flights data
  origin                origin airport code
  destination           destination airport code

optional arguments:
  -h, --help            show this help message and exit
  --bags BAGS           number of requested bags (if negative, turned to 0)
  --return              return flight
  --days_in_destination {1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31}
                        minimal time between return and departure in days
```

I implicitly assumed that there has to be at least one day between the trip to and back from the destination (default value is therefore 1). When error occurs while csv file parsing (incorrect datetime format, incorrect type provided (no conversion exists), negative number instead of non-negative number provided,...), the program exists with error message - possibly what was wrong and that it happened while csv parsing. In case csv file is correct, no error should occur and the program should output valid JSON formatted text on stdout.

Searching of flight is made dfs-like -> airports are considered as nodes and individual flights as edges. If crossing the edge from current node is valid (no rule is violated), search is again performed from the node we just got into while the path to the node is still in the memory so it can be printed. As algorithm stops when it reaches the destination node or no other node can be expanded, it finds all paths from given root node (origin) to destination.

Usage example:
`
python -m solution .\example_csv\example0.csv RFZ WIW --bags=-3 --return --days_in_destination=2
`
Output:
```
[
    {
        "flights": [
            {
                "flight_no": "ZH214",
                "origin": "RFZ",
                "destination": "WIW",
                "departure": "2021-09-02T05:50:00",
                "arrival": "2021-09-02T10:20:00",  
                "base_price": 168.0,
                "bag_price": 12.0,
                "bags_allowed": 2
            },
            {
                "flight_no": "ZH214",
                "origin": "WIW",
                "destination": "RFZ",
                "departure": "2021-09-04T23:20:00",
                "arrival": "2021-09-05T03:50:00",
                "base_price": 168.0,
                "bag_price": 12.0,
                "bags_allowed": 2
            }
        ],
        "bags_allowed": 2,
        "bags_count": 0,
        "destination": "WIW",
        "origin": "RFZ",
        "total_price": 336.0,
        "travel_time": "9:00:00"
    },
    {
        "flights": [
            {
                "flight_no": "ZH214",
                "origin": "RFZ",
                "destination": "WIW",
                "departure": "2021-09-02T05:50:00",
                "arrival": "2021-09-02T10:20:00",
                "base_price": 168.0,
                "bag_price": 12.0,
                "bags_allowed": 2
            },
            {
                "flight_no": "ZH214",
                "origin": "WIW",
                "destination": "RFZ",
                "departure": "2021-09-09T23:20:00",
                "arrival": "2021-09-10T03:50:00",
                "base_price": 168.0,
                "bag_price": 12.0,
                "bags_allowed": 2
            }
        ],
        "bags_allowed": 2,
        "bags_count": 0,
        "destination": "WIW",
        "origin": "RFZ",
        "total_price": 336.0,
        "travel_time": "9:00:00"
    },
    {
        "flights": [
            {
                "flight_no": "ZH214",
                "origin": "RFZ",
                "destination": "WIW",
                "departure": "2021-09-05T05:50:00",
                "arrival": "2021-09-05T10:20:00",
                "base_price": 168.0,
                "bag_price": 12.0,
                "bags_allowed": 2
            },
            {
                "flight_no": "ZH214",
                "origin": "WIW",
                "destination": "RFZ",
                "departure": "2021-09-09T23:20:00",
                "arrival": "2021-09-10T03:50:00",
                "base_price": 168.0,
                "bag_price": 12.0,
                "bags_allowed": 2
            }
        ],
        "bags_allowed": 2,
        "bags_count": 0,
        "destination": "WIW",
        "origin": "RFZ",
        "total_price": 336.0,
        "travel_time": "9:00:00"
    }
]
```
