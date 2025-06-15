-- This View will show the players available for signing or trade by age group 

CREATE VIEW players_available_by_age AS 

SELECT 
SUM(
CASE WHEN age BETWEEN 20 AND 24
THEN 1 ELSE 0 END) as '20-24',
SUM(
CASE WHEN age BETWEEN 25 AND 29
THEN 1 ELSE 0 END) as '25-29',
SUM(
CASE WHEN age BETWEEN 30 AND 34
THEN 1 ELSE 0 END) as '30-24',
SUM(
CASE WHEN age BETWEEN 35 AND 40
THEN 1 ELSE 0 END) as '35-40'
FROM players_available 