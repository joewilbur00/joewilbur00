-- This view will return the top 5 players at each position whose slugging percentage is greater than the average over the past three seasons
-- given that they have accumulated at least 800 plate appearances over that span 

CREATE VIEW top_five_power_hitters_by_position AS

WITH avg_slg AS (
    SELECT 
        p.position, AVG(b.slg) AS slg_avg
    FROM 
        batter_data b
    JOIN 
        players_available p
    ON 
        b.player_id = p.player_id
    WHERE 
        p.position IS NOT NULL AND b.year IN (2024, 2023, 2022)
    GROUP BY 
        p.position
),
ranked_players AS (
    SELECT 
        b.player_id, p.player_name, p.position, SUM(b.pa) as total_pa, ROUND(AVG(b.slg),3) AS player_slg_avg,
        ROW_NUMBER() OVER (PARTITION BY p.position ORDER BY AVG(b.slg) DESC) AS ranking
    FROM 
        batter_data b
    JOIN 
        players_available p
    ON 
        b.player_id = p.player_id
    WHERE 
        b.year IN (2024, 2023, 2022) 
    GROUP BY 
        b.player_id, p.player_name, p.position
	HAVING 
		SUM(b.pa) >= 800
),
filtered_players AS (
    SELECT 
        rp.player_id, rp.player_name, rp.position, rp.player_slg_avg, rp.ranking
    FROM 
        ranked_players rp
    JOIN 
        avg_slg a
    ON 
        rp.position = a.position
    WHERE 
        rp.player_slg_avg > a.slg_avg
)
SELECT 
    player_id, player_name, ranking, position, player_slg_avg
FROM 
    filtered_players
WHERE 
    ranking <= 5
ORDER BY 
    position, ranking;