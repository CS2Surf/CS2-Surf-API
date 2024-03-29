############
## Map.cs ##
############
sql_getMapInfo = "SELECT * FROM Maps WHERE name='{}';"
sql_insertMap = """INSERT INTO Maps (name, author, tier, stages, bonuses, ranked, date_added, last_played) 
                VALUES ('{}', '{}', {}, {}, {}, {}, {}, {});"""
sql_updateMap = """UPDATE Maps SET last_played={}, stages={}, bonuses={} WHERE id={};"""
sql_getMapRunsData = """SELECT MapTimes.*, Player.name FROM MapTimes
                    JOIN Player ON MapTimes.player_id = Player.id
                    WHERE MapTimes.map_id = {} AND MapTimes.style = {} AND MapTimes.type = {}
                    ORDER BY MapTimes.run_time ASC;"""
sql_getMapCheckpointsData = "SELECT * FROM `Checkpoints` WHERE `maptime_id` = {};"
sql_getMapRecordAndTotals = """SELECT MapTimes.*, Player.name
                            FROM MapTimes
                            JOIN Player ON MapTimes.player_id = Player.id
                            WHERE MapTimes.map_id = {} AND MapTimes.style = {}
                            ORDER BY MapTimes.run_time ASC;"""


####################
## PlayerStats.cs ##
####################
sql_getPlayerMapData = """SELECT mainquery.*, (SELECT COUNT(*) FROM `MapTimes` AS subquery 
                        WHERE subquery.`map_id` = mainquery.`map_id` AND subquery.`style` = mainquery.`style` 
                        AND subquery.`run_time` <= mainquery.`run_time`) AS `rank` FROM `MapTimes` AS mainquery 
                        WHERE mainquery.`player_id` = {} AND mainquery.`map_id` = {};"""

####################
## CurrentRun.cs ##
####################
sql_insertMapTime = """INSERT INTO `MapTimes` 
                    (`player_id`, `map_id`, `style`, `type`, `stage`, `run_time`, `start_vel_x`, `start_vel_y`, `start_vel_z`, `end_vel_x`, `end_vel_y`, `end_vel_z`, `run_date`, `replay_frames`) 
                    VALUES ({}, {}, {}, {}, {}, {}, 
                    {}, {}, {}, {}, {}, {}, {}, '{}') 
                    ON DUPLICATE KEY UPDATE run_time=VALUES(run_time), start_vel_x=VALUES(start_vel_x), start_vel_y=VALUES(start_vel_y), 
                    start_vel_z=VALUES(start_vel_z), end_vel_x=VALUES(end_vel_x), end_vel_y=VALUES(end_vel_y), end_vel_z=VALUES(end_vel_z), run_date=VALUES(run_date), replay_frames=VALUES(replay_frames);"""
sql_insertCheckpoint = """INSERT INTO `Checkpoints` 
                    (`maptime_id`, `cp`, `run_time`, `start_vel_x`, `start_vel_y`, `start_vel_z`, 
                    `end_vel_x`, `end_vel_y`, `end_vel_z`, `attempts`, `end_touch`) 
                    VALUES ({}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}) 
                    ON DUPLICATE KEY UPDATE 
                    run_time=VALUES(run_time), start_vel_x=VALUES(start_vel_x), start_vel_y=VALUES(start_vel_y), start_vel_z=VALUES(start_vel_z), 
                    end_vel_x=VALUES(end_vel_x), end_vel_y=VALUES(end_vel_y), end_vel_z=VALUES(end_vel_z), attempts=VALUES(attempts), end_touch=VALUES(end_touch);"""


####################
##   Players.cs   ##
####################
sql_getPlayerProfileData = "SELECT * FROM `Player` WHERE `steam_id` = {} LIMIT 1;"
sql_insertPlayerProfile = """INSERT INTO `Player` (`name`, `steam_id`, `country`, `join_date`, `last_seen`, `connections`) 
                            VALUES ('{MySqlHelper.EscapeString(name)}', {}, '{}', {}, {}, {});"""
sql_updatePlayerProfile = """UPDATE `Player` SET country = '{}', 
                            `last_seen` = {}, `connections` = `connections` + 1 
                            WHERE `id` = {};"""