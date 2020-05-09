import unacast_data as ud
import pandas as pd
import pathlib

# Go ahead and get location of file for saving
path = str(pathlib.Path(__file__).parent.absolute()).replace("\\","/")

# Get state-level data
# level="state" is default, but including for clarity
s_data = ud.get_data(level="state")

# Wrangle with local baseline and national baseline; set date as index
# local_baseline=False is default
s_lb = ud.state_etl(s_data, local_baseline=True).set_index("date")
s_nb = ud.state_etl(s_data, local_baseline=False).set_index("date")

# Sort columns alphabetically for convenience
s_lb = s_lb.reindex(sorted(s_lb.columns), axis=1)
s_nb = s_nb.reindex(sorted(s_nb.columns), axis=1)

# Save as CSV
s_lb.to_csv(path + "/../unacast_state_lb.csv")
s_nb.to_csv(path + "/../unacast_state_nb.csv")

# Repeat process for Memphis metro counties

# Get county-level data
# These states are default, but including for clarity
c_data = ud.get_data(level="county",states={"TN","MS","AR"})

# Define counties of interest
# These counties are default, but including for clarity
counties = {"TN": ["Shelby","Fayette","Tipton"],
            "MS": ["DeSoto","Marshall","Tunica","Benton"],
            "AR": ["Crittenden"]}

# Wrangle with local baseline and national baseline; set date as index
# local_baseline=False is default
c_lb = ud.county_etl(c_data, counties=counties, local_baseline=True).set_index("date")
c_nb = ud.county_etl(c_data, counties=counties, local_baseline=False).set_index("date")

# Not sorting, since the shelby is already first

# Save as CSV
c_lb.to_csv(path + "/../unacast_county_lb.csv")
c_nb.to_csv(path + "/../unacast_county_nb.csv")