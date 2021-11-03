#!/usr/bin/env python3
import argparse
import json
import sys
import csv
from datetime import datetime
from collections import defaultdict

parser = argparse.ArgumentParser()

parser.add_argument("data", metavar="csv", type=str, help="CSV file with the flights data")
parser.add_argument("origin", metavar="origin", type=str, help="origin airport code")
parser.add_argument("destination", metavar="destination", type=str, help="destination airport code")
parser.add_argument("--bags", default=0, type=int,
                    help="number of requested bags (if negative, turned to 0)")
parser.add_argument("--return", dest="ret", action='store_true', help="return flight")
parser.add_argument("--days_in_destination",dest="days", default=1, type=int, choices=range(1,32),
                    help="minimal time between return and departure in days")

class FlightEncoder(json.JSONEncoder):
    """Tells JSON how to serialize Flight class instance"""
    def default(self, o):
        if isinstance(o, Flight):
            datetime_format = "%Y-%m-%dT%H:%M:%S"
            json_flight = {}
            json_flight["flight_no"] = o.flight_no
            json_flight["origin"] = o.origin
            json_flight["destination"] = o.destination
            json_flight["departure"] = datetime.strftime(o.departure, datetime_format)
            json_flight["arrival"] = datetime.strftime(o.arrival, datetime_format)
            json_flight["base_price"] = o.base_price
            json_flight["bag_price"] = o.bag_price
            json_flight["bags_allowed"] = o.bags_allowed

            return json_flight

        return json.JSONEncoder.default(self, o)

class Flight:
    """
    A class to represent a flight.

    Attributes
    ----------
    flight_no : str
        flight number
    origin : str
        airport code of origin
    destination : int
        airport code of destination
    departure : datetime
        date and time of departure
    arrival : datetime
        date and time of arrival
    base_price : float
        price of the ticket
    bag_price : float
        price of one piece of baggage
    bags_allowed : int
        number of allowed pieces of baggage for the flight
    """

    def __init__(self, flight_no, origin, destination, departure, arrival, base_price, bag_price, bags_allowed):
        """
        Constructs attributes for the Flight object

        Parameters
        ----------
        flight_no : str
            flight number
        origin : str
            airport code of origin
        destination : str
            airport code of destination
        departure : str
            date and time of departure in format yyyy'-'MM'-'dd'T'HH':'mm':'ss
        arrival : str
            date and time of arrival in format yyyy'-'MM'-'dd'T'HH':'mm':'ss
        base_price : str
            price of the ticket
        bag_price : str
            price of one piece of baggage
        bags_allowed : str
            number of allowed pieces of baggage for the flight
        """
        datetime_format = "%Y-%m-%dT%H:%M:%S"
        self.flight_no = flight_no
        self.origin = origin
        self.destination = destination
        try:
            self.departure = datetime.strptime(departure, datetime_format)
            self.arrival = datetime.strptime(arrival, datetime_format)
        except:
            print("Error: date in provided csv file has incorrect format or contains incorrect values (expected: "+datetime_format+")")
            sys.exit(1)
        try:
            self.base_price = float(base_price)
            self.bag_price = float(bag_price)
        except:
            print("Error: prices (base_price, bag_price) should be float, got string")
            sys.exit(1)
        try:
            self.bags_allowed = int(bags_allowed)
            if self.bags_allowed < 0:
               raise
        except:
            print("Error: bags_allowed should be non-negative int")
            sys.exit(1)

class Data:
    """
    A class to represent flights data.

    Attributes
    ----------
    airports : set of str
        set of airport codes
    flights : defaultdict
        keeps flights from specific airports
        key: airport code (str)
        value: list of flights from 'key' airport (list of Flight)

    Methods
    -------
    add_airport(self, code):
        Prints the person's name and age.
    """

    def __init__(self):
        """Constructs attributes for the Data object"""
        self.airports = set()
        self.flights = defaultdict(list)

    def add_airport(self, code):
        """
        Adds airport to the airports attribute.

        Parameters
        ----------
        code : str
            code of the airport being added

        Returns
        -------
        None
        """

        self.airports.add(code)

    def add_flight(self, flight: Flight):
        """
        Adds flight to the flights attribute.

        Parameters
        ----------
        flight : Flight
            Flight object being added

        Returns
        -------
        None
        """

        self.flights[flight.origin].append(flight)

    def __dfs_flight_search(self, curr, destination, bags, visited, trip):
        """
        Performs dfs-like search, i.e. visits accesible airports via flights
        that satisfy given conditions (airport not yet visited,
        [min_transfer_time, max_transfer_time] hours for transfer,
        sufficient number of bags allowed)

        Parameters
        ----------
        curr : str
            airport code of current airport (node)
        destination : str
            airport code of destination airport (final node)
        bags : int
            number of bags that have to be allowed for the flight
        visited : [str]
            list of codes of airports that have been already visited
        trip : [Flight]
            list of flights on the trip so far (from origin node to curr) (edges)

        Returns
        -------
        list : list of possible flights (trip)
        """

        min_transfer_time = 1 # min time between following-up flights in hours
        max_transfer_time = 6 # max time between following-up flights in hours

        if curr == destination: # trip is over
            return trip

        for next_flight in self.flights[curr]:
            time_between = next_flight.departure - trip[-1].arrival # time for transfer
            if (next_flight.destination not in visited
                    and time_between.days == 0
                    and time_between.seconds >= min_transfer_time*3600
                    and time_between.seconds <= max_transfer_time*3600
                    and next_flight.bags_allowed >= bags):
                return self.__dfs_flight_search(next_flight.destination, destination, bags, visited | {curr}, trip + [next_flight])
        return []

    def search_flights(self, origin, destination, bags):
        """
        Searches for flights from origin to destination,
        starst dfs-like search from all airports that can be
        reached from origin airport.

        Parameters
        ----------
        origin : str
            airport code of origin airport (root node)
        destination : str
            airport code of destination airport (final node)
        bags : int
            number of bags that have to be allowed for the flight

        Returns
        -------
        list : list of lists of possible flights (all trips)
        """

        trips = [] # list of possible trips (paths)
        for next_flight in self.flights[origin]:
            if next_flight.bags_allowed >= bags:
                trips.append(self.__dfs_flight_search(next_flight.destination, destination, bags, {origin}, [next_flight]))
        return trips

    def search_flights_return(self, origin, destination, bags, days_in_destination):
        """
        Performs search from origin to destination and
        from destination to the origin. Pairs all trips that satisfy
        given conditions (between arrival on first trip and departre on trip back
        is days_in_destination time)

        Parameters
        ----------
        origin : str
            airport code of origin airport (root node)
        destination : str
            airport code of destination airport (final node)
        bags : int
            number of bags that have to be allowed for the flight
        days_in_destination : int
            number of days between trip to and back from the destination

        Returns
        -------
        list : list of lists of possible flights (all trips)
        """

        paths_to = list(filter(None, self.search_flights(origin, destination, bags)))
        paths_from = list(filter(None, self.search_flights(destination, origin, bags)))

        if len(paths_to) == 0 or len(paths_from) == 0:
            return []

        paths = []
        for trip_to in paths_to:
            for trip_back in paths_from:
                time_between = trip_back[0].departure - trip_to[-1].arrival
                # this return trip is possible only if there is sufficient time between arrival of to and departure of from
                if time_between.days >= days_in_destination:
                    paths.append(trip_to + trip_back)
        return paths

def load_data(file):
    """
    Loads data object from csv file.

    Parameters
    ----------
    file : str
        name of the file that is to be opened

    Returns
    -------
    Data : Data object with csv parsed
    """
    data = Data()
    try:
        with open(file, newline='', encoding="utf-8") as csvfile:
            flights_reader = csv.reader(csvfile)
            next(flights_reader) # skip header of csv

            for row in flights_reader:
                flight = Flight(*row)
                data.add_airport(flight.origin)
                data.add_airport(flight.destination)
                data.add_flight(flight)
    except:
        print("Error: csv not parsed correctly, aborting...")
        sys.exit(1)

    return data

def timedelta_to_hourminsec(timedelta):
    """
    Converts timedelta object to HH':'mm':'ss string.

    Parameters
    ----------
    timedelta : timedelta
        timedelta object (difference of two datetime objects)

    Returns
    -------
    str : string in format HH':'mm':'ss
    """
    days, seconds = timedelta.days, timedelta.seconds
    hours = days * 24 + seconds // 3600
    minutes = (seconds % 3600) // 60
    seconds = seconds % 60

    return f"{hours}:{minutes:02d}:{seconds:02d}"

def main(args: argparse.Namespace):
    """
    Performs the whole routine based on args:
        - loads data from csv file,
        - searches for flights based on given rules,
        - serializes output of search to json,
        - prints output to stdout

    Parameters
    ----------
    args : argparse.Namespace
        arguments by parse.argparse

    Returns
    -------
    None
    """

    # load data
    data = load_data(args.data)

    # search flights
    if args.ret: # return
        flights = list(filter(None, data.search_flights_return(args.origin, args.destination, args.bags, args.days)))
    else:
        flights = list(filter(None, data.search_flights(args.origin, args.destination, args.bags)))

    # json serialization
    results = []
    for flight in flights:
        trip = {}
        trip["flights"] = flight
        trip["bags_allowed"] = min(flight, key=lambda x: x.bags_allowed).bags_allowed
        trip["bags_count"] = args.bags
        trip["destination"] = args.destination
        trip["origin"] = args.origin
        trip["total_price"] = sum([fl.base_price + fl.bag_price * args.bags for fl in flight])

        if args.ret:
            flight_to_destination = next(x for x in flight if x.destination == args.destination)
            flight_from_destination = next(x for x in flight if x.origin == args.destination)
            time_in_destination = flight_from_destination.departure - flight_to_destination.arrival
            trip["travel_time"] = timedelta_to_hourminsec(flight[-1].arrival - flight[0].departure - time_in_destination)
        else:
            trip["travel_time"] = timedelta_to_hourminsec(flight[-1].arrival - flight[0].departure)

        results.append(trip)

    results.sort(key=lambda x: x["total_price"])

    # output
    print(json.dumps(results, indent=4, cls=FlightEncoder))

if __name__ == "__main__":
    args = parser.parse_args()
    # if negative number of mags inserted, make it 0
    if args.bags < 0:
        args.bags = 0
    main(args)
