-- This view will return the teams in 2024 that had a player or players in the top ten percent of run value and sprint speed along with the players who did so

CREATE VIEW teams_players_top_sprint_rv AS

WITH top_ten_percent_rv AS (
    SELECT player_id
    FROM (
        SELECT 
			rv.year, rv.player_id, rv.run_value,
			NTILE(10) OVER (ORDER BY rv.run_value DESC) AS percentile_rank
        FROM 
			run_value rv
    ) ranked_run_value
    WHERE percentile_rank = 1 AND year = 2024
),
top_ten_percent_sprint_speed AS (
    SELECT player_id
    FROM (
        SELECT 
			ss.year, ss.player_id, ss.sprint_speed,
			NTILE(10) OVER (ORDER BY ss.sprint_speed DESC) AS percentile_rank
        FROM 
			sprint_speed ss
    ) ranked_sprint_speed
    WHERE percentile_rank = 1 AND year = 2024
)
SELECT 
	t.team AS team_name, pa.player_id, pa.player_name, rv.run_value, ss.sprint_speed
FROM 
	players_available pa
JOIN 
    teams t
ON 
    pa.team_id = t.team_id
JOIN 
	run_value rv
ON 
	pa.player_id = rv.player_id
JOIN 
	sprint_speed ss
ON 
	pa.player_id = ss.player_id
WHERE 
    ss.year = 2024 AND rv.year = 2024
AND
    pa.player_id IN (SELECT player_id FROM top_ten_percent_rv)
AND 
    pa.player_id IN (SELECT player_id FROM top_ten_percent_sprint_speed);