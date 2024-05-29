-- Inserting threats
-- INSERT INTO threats (name, description) VALUES ('Threat 1', 'Description for Threat 1');
-- INSERT INTO threats (name, description) VALUES ('Threat 2', 'Description for Threat 2');
-- INSERT INTO threats (name, description) VALUES ('Threat 3', 'Description for Threat 3');
-- INSERT INTO threats (name, description) VALUES ('Threat 4', 'Description for Threat 4');
-- INSERT INTO threats (name, description) VALUES ('Threat 5', 'Description for Threat 5');

-- SELECT users.username FROM followers JOIN users ON followers.following_id = users.id WHERE follower_id=1;


-- INSERT INTO threats (name, description) VALUES ('Yosemite National Park, USA', 'Known for its iconic granite walls, including El Capitan and Half Dome, offering some of the best big wall climbing in the world.');
-- INSERT INTO threats (name, description) VALUES ('Chamonix, France', 'Nestled in the French Alps, it is a legendary climbing destination with stunning alpine routes and access to Mont Blanc.');
-- INSERT INTO threats (name, description) VALUES ('Patagonia, Argentina/Chile', 'Home to the dramatic peaks of Fitz Roy and Cerro Torre, offering challenging alpine climbing in a rugged wilderness.');
-- INSERT INTO threats (name, description) VALUES ('Red River Gorge, USA', 'Renowned for its steep sandstone cliffs and overhanging sport routes, making it a mecca for sport climbers.');
-- INSERT INTO threats (name, description) VALUES ('Kalymnos, Greece', 'Famous for its limestone crags and deep-water soloing, set against the beautiful backdrop of the Aegean Sea.');
-- INSERT INTO threats (name, description) VALUES ('Krabi, Thailand', 'Known for its stunning limestone karsts and beachside climbing, particularly around Railay and Tonsai.');
-- INSERT INTO threats (name, description) VALUES ('Mount Arapiles, Australia', 'A premier climbing destination with a diverse range of routes on high-quality sandstone rock.');
-- INSERT INTO threats (name, description) VALUES ('Bishop, USA', 'Offers world-class bouldering in the Buttermilks and nearby areas, set in the scenic Eastern Sierra.');
-- INSERT INTO threats (name, description) VALUES ('Dolomites, Italy', 'Characterized by its dramatic limestone towers and long multi-pitch routes, providing a classic alpine climbing experience.');
-- INSERT INTO threats (name, description) VALUES ('Fontainebleau, France', 'A historic bouldering area with thousands of problems set in a picturesque forest near Paris.');

INSERT INTO posts (title, body, threat_id, user_id) VALUES ('Half Dome Adventure', 'The cables were a bit tricky, but the view from the top was worth every effort!', 1, 2);
INSERT INTO posts (title, body, threat_id, user_id) VALUES ('Mont Blanc Summit', 'Challenging climb with unpredictable weather, but reaching the summit was exhilarating.', 1, 1);
INSERT INTO posts (title, body, threat_id, user_id) VALUES ('Fitz Roy Ascent', 'Battled fierce winds and freezing temperatures, but the climb was an unforgettable experience.', 2, 1);
INSERT INTO posts (title, body, threat_id, user_id) VALUES ('Cerro Torre Climb', 'The ice-covered peak tested our limits, but we conquered it in the end.', 2, 2);
INSERT INTO posts (title, body, threat_id, user_id) VALUES ('Red River Gorge Overhangs', 'The overhangs here are some of the toughest I have faced, but the climbs are amazing.', 3, 1);
INSERT INTO posts (title, body, threat_id, user_id) VALUES ('Kalymnos Limestone Fun', 'Deep-water soloing in Kalymnos was the highlight of my trip, can not wait to go back!', 4, 2);
INSERT INTO posts (title, body, threat_id, user_id) VALUES ('Railay Beach Climbing', 'Climbing with the sea breeze and stunning views was a dream come true.', 5, 1);
INSERT INTO posts (title, body, threat_id, user_id) VALUES ('Tonsai Route', 'Spent the day navigating some challenging routes on Tonsai, absolutely loved it.', 5, 2);
INSERT INTO posts (title, body, threat_id, user_id) VALUES ('Mount Arapiles Adventure', 'The diversity of routes here is incredible, spent a week exploring and climbing.', 6, 1);
INSERT INTO posts (title, body, threat_id, user_id) VALUES ('Buttermilks Bouldering', 'Spent a perfect weekend bouldering in the Buttermilks, can not wait to return.', 7, 2);
INSERT INTO posts (title, body, threat_id, user_id) VALUES ('Eastern Sierra Climb', 'The routes here offer a mix of difficulty and beautiful scenery, a great climbing spot.', 7, 1);
INSERT INTO posts (title, body, threat_id, user_id) VALUES ('Dolomites Multi-pitch', 'The long routes and breathtaking views in the Dolomites make it a must-visit.', 8, 2);
INSERT INTO posts (title, body, threat_id, user_id) VALUES ('Limestone Towers', 'Climbing the limestone towers was an unforgettable experience, highly recommended.', 8, 1);
INSERT INTO posts (title, body, threat_id, user_id) VALUES ('Fontainebleau Forest', 'Thousands of bouldering problems to tackle, each more fun than the last.', 9, 2);
INSERT INTO posts (title, body, threat_id, user_id) VALUES ('Bouldering Challenges', 'Spent a day in the Fontainebleau forest, the problems here are unique and challenging.', 9, 1);
INSERT INTO posts (title, body, threat_id, user_id) VALUES ('El Capitan Free Solo', 'Free soloed El Capitan in a single push, an exhilarating and terrifying experience.', 0, 1);
INSERT INTO posts (title, body, threat_id, user_id) VALUES ('Half Dome Cables', 'Navigating the cables on Half Dome was tricky but reaching the top was worth it.', 1, 2);
INSERT INTO posts (title, body, threat_id, user_id) VALUES ('Chamonix Glacier', 'Climbing on the glaciers in Chamonix was a new and exciting challenge for me.', 1, 1);
INSERT INTO posts (title, body, threat_id, user_id) VALUES ('Patagonia Ice Climbing', 'Ice climbing in Patagonia is as tough as it is beautiful, a real test of skill.', 2, 2);
INSERT INTO posts (title, body, threat_id, user_id) VALUES ('Red River Sandstone', 'The sandstone cliffs here offer some of the best sport climbing routes I have tried.', 3, 1);
INSERT INTO posts (title, body, threat_id, user_id) VALUES ('Kalymnos Sport Routes', 'Kalymnos is a sport climbers paradise, the routes are varied and the views spectacular.', 4, 2);
INSERT INTO posts (title, body, threat_id, user_id) VALUES ('Krabi Karsts', 'Climbing the limestone karsts in Krabi was an unforgettable experience.', 5, 1);
INSERT INTO posts (title, body, threat_id, user_id) VALUES ('Arapiles Sandstone', 'Spent a week exploring the diverse sandstone routes at Mount Arapiles.', 6, 2);
INSERT INTO posts (title, body, threat_id, user_id) VALUES ('Bishop Boulders', 'The bouldering problems in Bishop are some of the best I have encountered.', 7, 1);
INSERT INTO posts (title, body, threat_id, user_id) VALUES ('Dolomites Climbing', 'Climbing in the Dolomites was a dream come true, the scenery is simply breathtaking.', 8, 2);
