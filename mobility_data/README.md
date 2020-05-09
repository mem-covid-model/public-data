# Mobility Data

This folder contains data pulled from the [Unacast Social Distancing Scoreboard](https://www.unacast.com/covid19/social-distancing-scoreboard). It uses two variants of the the "Encounter Density" metric, described [here](https://www.unacast.com/post/rounding-out-the-social-distancing-scoreboard). There are four outputs, each with daily measurements starting Feb 24th and ending 3 days ago:

* **unacast_county_lb.csv**: Encounter densities for each county in the Memphis Metro Area, relative to a local baseline.
* **unacast_county_nb.csv**: Encounter densities for each county in the Memphis Metro Area, relative to a national baseline. This is the Unacast metric + 1.
* **unacast_state_lb.csv**: Encounter densities for each state + D.C., relative to a local baseline.
* **unacast_state_nb.csv**: Encounter densities for each state + D.C., relative to a national baseline. This is the Unacast metric + 1.

The first variant is transformed such that all values are positive and the baseline is 1, facilitating use as a scaling parameter. It retains the use of a national, rather than local, baseline (see the above link for details). This yields

M<sub>nb</sub> = encounters_per_km<sup>2</sup> / national_baseline

The second variant is similar, except it replaces the national baseline with a local one. This is done by averaging the above **M_nb** metric for 02/24 - 03/08, which is the stopping point that Unacast uses. This new baseline is then used to scale **M_{nb}**:

M_lb = M_nb / local_baseline

Each approach has strengths and weaknesses. Unacast uses the national baseline; as they point out, "What matters is how many people were in the same place at the same time, regardless of how much it changed from the past." However, if we use local data as a starting point, we may already implicitly adjust for local context (e.g., calculating the effective reproduction number). In this case, we would want to use a local baseline.