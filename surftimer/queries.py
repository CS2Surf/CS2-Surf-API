############
## Map.cs ##
############
sql_getMapInfo = "SELECT * FROM Maps WHERE name='{}';"
sql_insertMap = """INSERT INTO Maps (name, author, tier, stages, ranked, date_added, last_played) 
                    VALUES ('{}', '{}', {}, {}, {}, {}, {});"""
sql_updateMap = """UPDATE Maps SET last_played={}, stages={}, bonuses={} WHERE id={};"""
sql_getMapRunsData = """SELECT MapTimes.*, Player.name FROM MapTimes
                    JOIN Player ON MapTimes.player_id = Player.id
                    WHERE MapTimes.map_id = {} AND MapTimes.style = {} AND MapTimes.type = {}
                    ORDER BY MapTimes.run_time ASC;"""
sql_getMapCheckpointsData = "SELECT * FROM `Checkpoints` WHERE `maptime_id` = {};"

####################
## PlayerStats.cs ##
####################
sql_getPlayerMapData = """SELECT mainquery.*, (SELECT COUNT(*) FROM `MapTimes` AS subquery 
                          WHERE subquery.`map_id` = mainquery.`map_id` AND subquery.`style` = mainquery.`style` 
                          AND subquery.`run_time` <= mainquery.`run_time`) AS `rank` FROM `MapTimes` AS mainquery 
                          WHERE mainquery.`player_id` = {} AND mainquery.`map_id` = {};"""
