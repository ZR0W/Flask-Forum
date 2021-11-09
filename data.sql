CREATE TABLE user ( 
	id INTEGER  NOT NULL, 
	username VARCHAR(50)  NOT NULL,
	email VARCHAR(120)  NOT NULL,
	password VARCHAR(128)  NOT NULL,
	PRIMARY KEY (id)
); 
CREATE TABLE post ( 
	id INTEGER  NOT NULL, 
	body VARCHAR(250)  NOT NULL,
	title VARCHAR(80)  NOT NULL,
	timestamp datetime  NOT NULL,
	upvote INTEGER DEFAULT 0 NOT NULL, 
	downvote INTEGER DEFAULT 0 NOT NULL, 
	user_id INTEGER REFERENCES user (id),
	PRIMARY KEY (id)
); 
CREATE TABLE comment ( 
	id INTEGER  NOT NULL, 
	body VARCHAR(250)  NOT NULL,
	timestamp datetime  NOT NULL,
	upvote INTEGER DEFAULT 0 NOT NULL, 
	downvote INTEGER DEFAULT 0 NOT NULL, 
	post_id INTEGER REFERENCES post (id),
	PRIMARY KEY (id, post_id)
); 
CREATE TABLE message ( 
	body VARCHAR(250)  NOT NULL,
	timestamp datetime  NOT NULL,
	user_id1 INTEGER REFERENCES user (id),
	user_id2 INTEGER REFERENCES user (id),
	PRIMARY KEY (timestamp, user_id1, user_id2)
);