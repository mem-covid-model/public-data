import requests, json, csv
import pandas as pd

fips_dict = {"AL": "01", "AK": "02", "AZ": "04", "AR": "05", "CA": "06", 
             "CO": "08", "CT": "09", "DE": "10", "DC": "11", "FL": "12",
             "GA": "13", "HI": "15", "ID": "16", "IL": "17", "IN": "18",
             "IA": "19", "KS": "20", "KY": "21", "LA": "22", "ME": "23",
             "MD": "24", "MA": "25", "MI": "26", "MN": "27", "MS": "28",
             "MO": "29", "MT": "30", "NE": "31", "NV": "32", "NH": "33",
             "NJ": "34", "NM": "35", "NY": "36", "NC": "37", "ND": "38",
             "OH": "39", "OK": "40", "OR": "41", "PA": "42", "RI": "44",
             "SC" :"45", "SD": "46", "TN": "47", "TX": "48", "UT": "49",
             "VT" :"50", "VA": "51", "WA": "53", "WV": "54", "WI": "55",
             "WY" :"56"}

# Function for getting data from Unacast
def get_data(level="state",states=["AR","MS","TN"]):
    """
    Pulls state or county data from the UnaCast COVID-19
    Social Distancing Scoreboard. "state" returns data for all 50
    states + DC; "county" returns data for all counties in the 
    "states" list. "states" must be referenced using two-letter
    abbreviations.

    Keyword Arguments:
        level {str}: state or county (default: {"state"})
        states {list}: States containing counties of interest (default: {["AR","MS","TN"]})
    """
    # Handle state case
    if level == "state":
        r = requests.get("https://covid19-scoreboard-api.unacastapis.com/api/search/covidstateaggregates_v3?size=1000")
        response = r.json()
    # Handle county case
    elif level == "county":
        # Initialize response variable
        response = {}
        # Loop through states and save in response dict
        # TODO: Handle bad state abbreviations
        for state in states:
            fip = fips_dict[state]
            r_string = "https://covid19-scoreboard-api.unacastapis.com/api/search/covidcountyaggregates_v3?q=stateFips:"+fip+"&size=4000"
            r = requests.get(r_string)
            response[state] = r.json()
    # Handle something else getting input to 'level'
    else:
        raise SystemExit("Error: level was not set to 'state' or 'county'")
    return response

# Find counties of interest
def county_etl(data,counties={"TN": ["Shelby","Fayette","Tipton"],
                                "MS": ["DeSoto","Marshall","Tunica","Benton"],
                                "AR": ["Crittenden"]}, local_baseline=False):
    """Extracts and transforms county data for given counties in state-county pair. 
    Returns a pandas DataFrame of dates and "encountersMetric" by county.
    If 'local_baseline' is True, normalizes baseline using the first two weeks of data for each county.

    Arguments:
        data {dict} -- The JSON dict from get_data(level="county")

    Keyword Arguments:
        counties {dict} -- A dict containing the state abbreviation and a list of counties for each state
        local_baseline {bool} -- Whether to compute baseline locally
        """
    
    # Loop through and get counties of interest
    # This is awful practice, but it doesn't take long enough to warrant
    # cleaning up right now

    # Loop by state
    for state in counties:
        s_dict = data[state]["hits"]["hits"]
        # Loop by county
        for county in counties[state]:
            countyName = county + " " + "County"
            # Find county in dict and create dataframe
            for n in range(0,len(s_dict)):
                if s_dict[n]["_source"]["countyName"] == countyName:
                    c_df = pd.DataFrame(s_dict[n]["_source"]["data"])
                    # Reverse order, get just date + encountersMetric columns
                    c_encounters = (
                        c_df[::-1][["date","encountersMetric"]]
                        .reset_index()
                        .drop(columns="index")
                        )
                    break
            # If overall DataFrame does not exist, create it
            try:
                county_metrics
            except UnboundLocalError:
                county_metrics = c_encounters
                county_metrics.rename(columns={"encountersMetric":county+state}, inplace=True)
            else:
                county_metrics[county+state]=c_encounters.encountersMetric
    # Transform to scaling parameter
    if local_baseline == True:
        for col in county_metrics.columns:
            if col == "date":
                continue
            county_metrics[[col]] += 1
            county_metrics[[col]] = county_metrics[[col]] / county_metrics[[col]][0:13].mean()

    return county_metrics
                

def state_etl(data, states=None, local_baseline=False):
    """Extracts and transforms state data for given states (or all if none given).
    Returns a pandas DataFrame of dates and "encountersMetric" by state.
    If "local_baseline" is True, normalizes baseline using the first two weeks of data for each state.

    Arguments:
        data {dict} -- JSON dict passed from get_data(level="state")
    Keyword Arguments:
        states {list} -- List of state abbreviations. Defaults to all states. (default: {None})
        local_baseline {bool} -- Whether to compute baseline locally (default: {False})
    """
    # Select first two levels
    n_dict = data["hits"]["hits"]

    #? Using if structure before for loop to avoid repeated if tests. Harder to read
    #? but more efficient, right?

    # Get data for all states
    if states == None:
        for n in range(0,len(n_dict)):
            stateCode = n_dict[n]["_source"]["stateCode"]
            s_df = pd.DataFrame(n_dict[n]["_source"]["data"])
            s_encounters = (
                s_df[::-1][["date","encountersMetric"]]
                .reset_index()
                .drop(columns="index")
            )
            try:
                state_metrics
            except UnboundLocalError:
                state_metrics = s_encounters.rename(columns={"encountersMetric":stateCode})
            else:
                state_metrics[stateCode] = s_encounters.encountersMetric
    else:
        for state in states:
            for n in range(0,len(n_dict)):
                stateCode = n_dict[n]["_source"]["stateCode"]
                if state == stateCode:
                    s_df = pd.DataFrame(n_dict[n]["_source"]["data"])
                    s_encounters = (
                        s_df[::-1][["date","encountersMetric"]]
                        .reset_index()
                        .drop(columns="index")
                    )
                    break
            try:
                state_metrics
            except UnboundLocalError:
                state_metrics = s_encounters.rename(columns={"encountersMetric":stateCode})
            else:
                state_metrics[stateCode] = s_encounters.encountersMetric
    
    # Translate into scaling parameter
    if local_baseline == True:
        for col in state_metrics.columns:
            if col == "date":
                continue
            state_metrics[[col]] += 1
            state_metrics[[col]] = state_metrics[[col]] / state_metrics[[col]][0:13].mean()
    else:
        for col in state_metrics.columns:
            if col == "date":
                continue
            state_metrics[[col]] = state_metrics[[col]] + 1
      
    return state_metrics