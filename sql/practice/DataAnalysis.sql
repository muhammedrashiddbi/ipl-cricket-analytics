1. Find the top 10 grounds by number of matches
Query
SELECT
    venue AS ground,
    COUNT(DISTINCT match_id) AS matches
FROM matches
WHERE venue IS NOT NULL
GROUP BY venue
ORDER BY matches DESC
LIMIT 10;
Answer

This returns the 10 grounds/venues where the highest number of IPL matches were played.

Explanation
GROUP BY venue → groups matches by ground.
COUNT(DISTINCT match_id) → counts each match only once.
ORDER BY matches DESC → highest number first.
LIMIT 10 → displays only the top 10.




2. Grounds with average innings score above 165, minimum 25 matches

For this, we need the total score of each innings from deliveries.

Query
WITH innings_scores AS (
    SELECT
        match_id,
        inning,
        SUM(total_runs) AS innings_score
    FROM deliveries
    GROUP BY match_id, inning
)
SELECT
    m.venue AS ground,
    COUNT(DISTINCT m.match_id) AS matches,
    ROUND(AVG(i.innings_score), 2) AS average_innings_score
FROM matches m
JOIN innings_scores i
    ON m.match_id = i.match_id
WHERE m.venue IS NOT NULL
GROUP BY m.venue
HAVING COUNT(DISTINCT m.match_id) >= 25
   AND AVG(i.innings_score) > 165
ORDER BY average_innings_score DESC;
Answer

This gives grounds where:

At least 25 matches were played.
The average innings score is above 165.
Explanation

First, the WITH section calculates the total runs for every innings:

SUM(total_runs)

Then we join those innings scores with the matches table to get the venue.

HAVING COUNT(DISTINCT m.match_id) >= 25

ensures that only grounds with at least 25 matches are considered.

AVG(i.innings_score) > 165

selects grounds with an average innings score above 165.




3. Calculate chase win percentage for grounds with at least 50 matches

Here we treat a chase win as a match where the winner batted second.

Query
WITH match_results AS (
    SELECT
        m.match_id,
        m.venue,
        m.winner,
        m.inning,
        MAX(CASE
            WHEN d.inning = 2
             AND d.batting_team = m.winner
            THEN 1
            ELSE 0
        END) AS chase_win
    FROM matches m
    JOIN deliveries d
        ON m.match_id = d.match_id
    WHERE m.venue IS NOT NULL
    GROUP BY m.match_id, m.venue, m.winner
)
SELECT
    venue AS ground,
    COUNT(*) AS matches,
    SUM(chase_win) AS chase_wins,
    ROUND(100.0 * SUM(chase_win) / COUNT(*), 2) AS chase_win_percentage
FROM match_results
GROUP BY venue
HAVING COUNT(*) >= 50
ORDER BY chase_win_percentage DESC;
Answer

This produces:

Ground	Matches	Chase Wins	Chase Win %
Ground 1	...	...	...
Ground 2	...	...	...
Explanation

A chase win means the team that won the match was batting in the second innings.

d.inning = 2
AND d.batting_team = m.winner

identifies that situation.

Then:

100.0 * SUM(chase_win) / COUNT(*)

calculates the percentage.

The 100.0 makes SQLite perform decimal division instead of integer division.




4. Count the number of unique cleaned venues

If your table has a cleaned venue column such as venue_cleaned:

Query
SELECT COUNT(DISTINCT venue_cleaned) AS unique_cleaned_venues
FROM matches
WHERE venue_cleaned IS NOT NULL
  AND TRIM(venue_cleaned) <> '';
Answer

The result is the number of different cleaned venue names in the dataset.

Explanation
COUNT(DISTINCT venue_cleaned)

counts each unique venue only once.

TRIM(venue_cleaned) <> ''

removes blank values from consideration.

If your column is simply venue

Use:

SELECT COUNT(DISTINCT TRIM(venue)) AS unique_cleaned_venues
FROM matches
WHERE venue IS NOT NULL
  AND TRIM(venue) <> '';




  5. Find the five grounds with the lowest powerplay run rate

Assuming phase = 'Powerplay' and is_legal identifies legal deliveries:

Query
SELECT
    m.venue AS ground,
    ROUND(
        6.0 * SUM(d.total_runs) / SUM(d.is_legal),
        2
    ) AS powerplay_run_rate
FROM matches m
JOIN deliveries d
    ON m.match_id = d.match_id
WHERE m.venue IS NOT NULL
  AND d.phase = 'Powerplay'
GROUP BY m.venue
HAVING SUM(d.is_legal) > 0
ORDER BY powerplay_run_rate ASC
LIMIT 5;
Answer

This returns the 5 grounds with the lowest Powerplay run rate.

Explanation

Cricket run rate is:

Runs / Overs

Since one over contains 6 legal balls:

Run Rate = Runs × 6 / Legal Balls

Therefore:

6.0 * SUM(d.total_runs) / SUM(d.is_legal)

calculates the Powerplay run rate.

ORDER BY powerplay_run_rate ASC

puts the lowest run rate first.




6. Why is COUNT(DISTINCT match_id) safer than COUNT(*) after a JOIN?
Example

Suppose the matches table contains:

match_id	venue
1	Eden Gardens

But the deliveries table contains hundreds of rows for match 1.

After:

SELECT *
FROM matches m
JOIN deliveries d
ON m.match_id = d.match_id;

one match becomes many rows because every delivery is joined to that match.

So:

COUNT(*)

would count the number of joined delivery rows, not the number of matches.

Instead:

COUNT(DISTINCT match_id)

counts the match only once.

Simple answer for record

COUNT(DISTINCT match_id) is safer after a JOIN because a single match can produce many rows due to multiple deliveries. COUNT(*) may count the same match repeatedly, while COUNT(DISTINCT match_id) counts each match only once.




7. Why can't the day/night question be answered from match_date alone?
Answer

match_date tells us the date on which the match was played, but it does not tell us the time at which the match started.

For example:

match_date = 2024-04-10

only tells us the date.

It doesn't tell us whether the match started:

3:30 PM → Day match

or

7:30 PM → Night match

Both could have the same match_date.