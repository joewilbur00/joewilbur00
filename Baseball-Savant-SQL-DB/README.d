# Baseball Savant SQL Analysis

This project demonstrates end-to-end database design and analysis using data scraped from MLB's Baseball Savant platform. The data was structured and normalized into a MySQL database and analyzed using advanced SQL queries and custom views to extract meaningful insights on player performance and team strategy.

---

## Key Components

### 1. Database Creation (`savant_data.sql`)
- Built a MySQL database called `savant_data`
- Defined structured tables for players, teams, batter performance, sprint speed, and run value
- Ensured normalization and primary/foreign key integrity

---

### 2. Analytical Views

Each view showcases a specific insight drawn from the structured database:

#### `players_available_by_age_view.sql`
Shows the count of players available for signing or trade by age group (20–24, 25–29, etc.), useful for team roster planning.

#### `top_power_hitters_by_position_view.sql`
Identifies the top 5 power hitters at each position based on slugging percentage over the last three years, for players with at least 800 plate appearances.

#### `teams_players_top_sprint_rv_view.sql`
Returns teams with players in the top 10% for both sprint speed and run value in the 2024 season. Useful for identifying high-impact, high-speed contributors.

---

## Project Objective

To showcase data modeling, query design, and baseball-specific analytics through:
- Advanced SQL techniques (`CTE`, `ROW_NUMBER()`, `NTILE`, `JOIN`)
- Real-world player performance analysis
- View creation to support decision-making scenarios (e.g., scouting, trade strategy)
