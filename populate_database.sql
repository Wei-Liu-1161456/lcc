-- Populate database for LCC Issue Tracker
-- This script will create:
-- * 20 visitors, 5 helpers, and 2 administrators
-- * 20 issues
-- * 20 comments

-- Users table data
INSERT INTO `users` (`username`, `password_hash`, `email`, `first_name`, `last_name`, `location`, `role`, `status`) VALUES
('visitor1', '$2b$12$YStUZcZZ0jg0RxF1RnUHDOGZ3qk33r3VQ1XMrqCtQGAk7aoTE3Rnu', 'visitor1@example.com', 'Visitor1', 'User', 'Lincoln', 'visitor', 'active'),
('visitor2', '$2b$12$LxcaYHa8NLLztD5AtFRHh.gSzAA.1q9Pw0cIGnH02AJ5eEt7UQQv2', 'visitor2@example.com', 'Visitor2', 'User', 'Christchurch', 'visitor', 'active'),
('visitor3', '$2b$12$vVSCI9riQ2AURDSdw8vfVuesHNvkzVw09qKyTiUwI8TLa.W5A79Wm', 'visitor3@example.com', 'Visitor3', 'User', 'Canterbury', 'visitor', 'active'),
('visitor4', '$2b$12$yYBaFECPdlXrT75lVRY7puhQ0P46sbnoMD5G.zrsWDZdxO00ATVFS', 'visitor4@example.com', 'Visitor4', 'User', 'Lincoln', 'visitor', 'active'),
('visitor5', '$2b$12$zq4LKTqusyUkNZpffqwaVuW40tyTsUXvcl16NXQD17S.3.DhdJtUK', 'visitor5@example.com', 'Visitor5', 'User', 'Christchurch', 'visitor', 'active'),
('visitor6', '$2b$12$anm0JwAKX.RLFwfsBChqietvlxe0A7YcXyPFi6rhVBuX08G7uBCC6', 'visitor6@example.com', 'Visitor6', 'User', 'Canterbury', 'visitor', 'active'),
('visitor7', '$2b$12$p8HbCrWT4saXQ8Ik.ZsCjODdaL9JHuchOhtBvAli7bvMTxB0GK26e', 'visitor7@example.com', 'Visitor7', 'User', 'Lincoln', 'visitor', 'active'),
('visitor8', '$2b$12$.qg45W7KO7loyfy1FFoj8OAsgGOF1xrFUObLOtANdQfawFinryFYm', 'visitor8@example.com', 'Visitor8', 'User', 'Christchurch', 'visitor', 'active'),
('visitor9', '$2b$12$LcP8CoipCHEjLv9GV1yW5.g6Wh/R8wDJnUJAj5NG1pdBssov9xKtu', 'visitor9@example.com', 'Visitor9', 'User', 'Canterbury', 'visitor', 'active'),
('visitor10', '$2b$12$9tN7U/X88xEKpQarIQe8mustNKtCRp5xFO5fTq6/qZYAhwwpHuRze', 'visitor10@example.com', 'Visitor10', 'User', 'Lincoln', 'visitor', 'active'),
('visitor11', '$2b$12$7hz82mnGmhJ4nD8UNlcAOOcwcHi5BkF9LDEz/Ut9MKyrMENcN6Oay', 'visitor11@example.com', 'Visitor11', 'User', 'Christchurch', 'visitor', 'active'),
('visitor12', '$2b$12$uRJ8gXZVCdM/d6F2NEblZ.WBRplPKdRyWsnvYLJxT9HdeEkbS7U3q', 'visitor12@example.com', 'Visitor12', 'User', 'Canterbury', 'visitor', 'active'),
('visitor13', '$2b$12$ecHtzOsGCNtrL3AO29hzNOlxJV1SvshGCJSV0cZnb1OJqsjh2mwjy', 'visitor13@example.com', 'Visitor13', 'User', 'Lincoln', 'visitor', 'active'),
('visitor14', '$2b$12$Sr52h1eergHmoEa.qfG4uujALEBfyzeu6XaJARsotp/6RjWYyxuKu', 'visitor14@example.com', 'Visitor14', 'User', 'Christchurch', 'visitor', 'active'),
('visitor15', '$2b$12$YfdpcmkFCp2o93N5i/aubO60OFzCOCmtUC/Go.EDv/GSs6/TeWe2O', 'visitor15@example.com', 'Visitor15', 'User', 'Canterbury', 'visitor', 'active'),
('visitor16', '$2b$12$N1xyzVDSW/DxAFDMBbmdQurEFnaeJKAJs4x91pIkNRazPIvOf1ioO', 'visitor16@example.com', 'Visitor16', 'User', 'Lincoln', 'visitor', 'active'),
('visitor17', '$2b$12$3l4PpQqdY/2.ZIWjfmIKpOxBKHTwDA/AoxjJnhuGkTLXtd9NR49GS', 'visitor17@example.com', 'Visitor17', 'User', 'Christchurch', 'visitor', 'active'),
('visitor18', '$2b$12$Z.rUo2QucaatT1ED3HiME.srEYnKp961PZRtz52cSTuo/WpgGcbLG', 'visitor18@example.com', 'Visitor18', 'User', 'Canterbury', 'visitor', 'active'),
('visitor19', '$2b$12$3QuXGaXYSA6802GnEPT.gOsZ3Jer6ZvVa0uFdbtd.eq4pctUpRvo2', 'visitor19@example.com', 'Visitor19', 'User', 'Lincoln', 'visitor', 'active'),
('visitor20', '$2b$12$wkaw5XKnO7uEXD1gO6ll3.9Q2VM7ABe8YRcrt7L5luTgL5Hnd5TeS', 'visitor20@example.com', 'Visitor20', 'User', 'Christchurch', 'visitor', 'active'),
('helper1', '$2b$12$AWT5iSi6Etq7eEhatXN7uONzq2Vpl5hFpjmb1WiD97qwflcGN/uQu', 'helper1@example.com', 'Helper1', 'User', 'Canterbury', 'helper', 'active'),
('helper2', '$2b$12$9EVs5fegeDbAVTa0HpmlOec5.9QhGkmIVOBlzuPCcyb.a6zmnIYmC', 'helper2@example.com', 'Helper2', 'User', 'Lincoln', 'helper', 'active'),
('helper3', '$2b$12$b7cX5doGboDUr00bc8zWH.C0gPi4HVtjM6WlCJFyo13uX2uz0E/3C', 'helper3@example.com', 'Helper3', 'User', 'Christchurch', 'helper', 'active'),
('helper4', '$2b$12$fGLNfa.4xmpC68Z23iFMmO2QmeokGsCscvlkNMFIQxc.2LLLDJVJu', 'helper4@example.com', 'Helper4', 'User', 'Canterbury', 'helper', 'active'),
('helper5', '$2b$12$rruI2yYM5t5Sp9v7VndmeuUKdbBo1qA.aU9AahjgXTbONTc6iSKwK', 'helper5@example.com', 'Helper5', 'User', 'Lincoln', 'helper', 'active'),
('admin1', '$2b$12$oHFTBWUBqcJ7Tf0R6zNIZOkPr/wbZ4y5ToCT.3ErZ3ha6tlFMnVr6', 'admin1@example.com', 'Admin6', 'User', 'Christchurch', 'admin', 'active'),
('admin2', '$2b$12$2rHmxqsTmYPtIabgSRYgdeyVsGEDj9CSJNpeZrkyrg96f8LgQKgke', 'admin2@example.com', 'Admin7', 'User', 'Canterbury', 'admin', 'active');

-- Issues table data
INSERT INTO `issues` (`user_id`, `summary`, `description`, `created_at`, `status`) VALUES
(1, 'Broken shower in men''s bathroom', 'The hot water in the men''s bathroom shower #2 isn''t working. Only cold water comes out.', '2024-02-01 08:30:00', 'new'),
(2, 'Wi-Fi not working in area B', 'Cannot connect to Wi-Fi in camping area B. The signal seems very weak or non-existent.', '2024-02-02 10:15:00', 'open'),
(3, 'Trash bins need emptying', 'The trash bins near the picnic area are overflowing and need to be emptied.', '2024-02-03 15:45:00', 'resolved'),
(4, 'Fallen tree blocking path', 'A large branch has fallen across the walking path to the lake after last night''s storm.', '2024-02-04 07:20:00', 'stalled'),
(5, 'BBQ grill missing parts', 'The BBQ grill at site #8 is missing the grate and seems to have some broken parts.', '2024-02-05 16:30:00', 'new'),
(6, 'Solar charging station not working', 'The solar charging station near the central pavilion isn''t working. The indicator lights are off.', '2024-02-06 11:45:00', 'open'),
(7, 'Water leak in women''s bathroom', 'There is a water leak coming from the sink in the women''s bathroom. Water is pooling on the floor.', '2024-02-07 09:10:00', 'resolved'),
(8, 'Picnic table damaged', 'The picnic table at site #12 has a broken bench. It looks unsafe to sit on.', '2024-02-08 14:25:00', 'stalled'),
(9, 'Loud noise from generator', 'The generator near the maintenance shed is making an unusually loud noise. It might need servicing.', '2024-02-09 18:00:00', 'new'),
(10, 'Fire pit filled with water', 'The fire pit at site #3 is filled with water from the rain and needs to be drained.', '2024-02-10 12:35:00', 'open'),
(11, 'Main gate won''t lock properly', 'The main entrance gate doesn''t lock properly. Security concern especially at night.', '2024-02-11 20:15:00', 'resolved'),
(12, 'Playground swing broken', 'One of the swings in the children''s playground has a broken chain and is unusable.', '2024-02-12 16:50:00', 'stalled'),
(13, 'Need more firewood', 'The communal firewood storage is empty. Could we get a delivery soon?', '2024-02-13 15:30:00', 'new'),
(14, 'Lost and found request', 'I lost my blue backpack somewhere near the fishing dock yesterday. Has anyone found it?', '2024-02-14 09:45:00', 'open'),
(15, 'RV dump station clogged', 'The RV waste dump station appears to be clogged and is backing up when used.', '2024-02-15 11:20:00', 'resolved'),
(16, 'Need new light bulbs', 'Several light bulbs are burnt out in the common area pavilion, making it too dark at night.', '2024-02-16 19:05:00', 'stalled'),
(17, 'Insect nest near site #6', 'There appears to be a large wasp or hornet nest in the tree adjacent to camping site #6.', '2024-02-17 14:40:00', 'new'),
(18, 'Water pressure issue', 'The water pressure at the dish washing station is very low, making it difficult to clean dishes properly.', '2024-02-18 08:15:00', 'open'),
(19, 'Need recycling information', 'Could we get better signs explaining what can be recycled and where the bins are located?', '2024-02-19 10:55:00', 'resolved'),
(20, 'Trail markers faded', 'The trail markers on the nature walk are faded and hard to follow. Some appear to be missing.', '2024-02-20 13:25:00', 'new');

-- Comments table data
INSERT INTO `comments` (`issue_id`, `user_id`, `content`, `created_at`) VALUES
(1, 22, 'I checked the shower and it looks like the mixing valve needs to be replaced. I''ve ordered the part.', '2024-02-01 10:45:00'),
(1, 1, 'Thank you for looking into this quickly!', '2024-02-01 11:30:00'),
(2, 23, 'I''ll bring the signal booster tomorrow and set it up in area B.', '2024-02-02 14:20:00'),
(3, 24, 'All trash bins have been emptied and new bags installed.', '2024-02-03 17:00:00'),
(3, 3, 'Thank you! The area looks much better now.', '2024-02-03 18:15:00'),
(4, 25, 'We need a chainsaw to remove this. Will try to borrow one from maintenance department.', '2024-02-04 09:30:00'),
(4, 26, 'Maintenance said the chainsaw is being repaired. We''ll have to wait until next week.', '2024-02-04 14:50:00'),
(5, 6, 'Has anyone had a chance to look at the BBQ grill yet?', '2024-02-06 09:15:00'),
(6, 27, 'The solar panel connections appear corroded. I''ve cleaned them and it''s working again.', '2024-02-06 15:40:00'),
(7, 22, 'Leak has been fixed. Had to replace the washer in the faucet.', '2024-02-07 13:25:00'),
(8, 23, 'We''ll need to order a new bench slat. In the meantime, I''ve taped off the table so no one uses it.', '2024-02-08 16:35:00'),
(9, 9, 'The noise is getting worse. Can someone please check this soon?', '2024-02-10 08:50:00'),
(10, 24, 'I''ve drained the fire pit and it should be usable now.', '2024-02-10 14:10:00'),
(11, 25, 'Gate lock has been replaced and is working properly now.', '2024-02-11 22:05:00'),
(12, 26, 'New swing parts are on backorder. Should arrive in about 2 weeks.', '2024-02-12 17:40:00'),
(13, 27, 'Firewood delivery scheduled for tomorrow morning.', '2024-02-13 16:55:00'),
(14, 14, 'Any update on my lost backpack? It has important medication in it.', '2024-02-15 10:30:00'),
(15, 22, 'Dump station has been unclogged and is operational again.', '2024-02-15 12:45:00'),
(16, 23, 'Light bulbs have been replaced in the pavilion.', '2024-02-17 09:20:00'),
(20, 25, 'I''ll repaint the trail markers this weekend if the weather permits.', '2024-02-20 15:15:00');

-- End of script