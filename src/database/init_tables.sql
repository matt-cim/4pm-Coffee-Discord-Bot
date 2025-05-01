CREATE TABLE open_groups (
    id SERIAL PRIMARY KEY, -- Identifier
    game VARCHAR(30), -- Game the group is for (30 is arbitrary)
    username VARCHAR(32), -- Creator of the group (max length for Discord username is 32 characters)
    group_size SMALLINT, -- Using SMALLINT to save space
    people_needed SMALLINT, -- group_size - # of people joined
    description VARCHAR(300), -- Description of the lfg post
    members TEXT[], -- Array of users who've joined group (max up to 99)
    creation_time TIMESTAMP -- When the lfg post was created
);

CREATE TABLE open_voice_channels (
    open_groups_id SERIAL, -- Identifier, same as corresponding id in open_groups
    channel_id VARCHAR(25), -- Seems to be 19 chars, pad to be safe
    username VARCHAR(32), -- Creator of the group
    creation_time TIMESTAMP -- When the lfg post was created
);

CREATE TABLE user_ratings (
    username VARCHAR(32) UNIQUE, -- Creator of the group (max length for Discord username is 32 characters)
    rating_count INT DEFAULT 0, -- Number of ratings
    rating_sum INT DEFAULT 0, -- Total sum of all ratings
    average_rating NUMERIC(3, 2) DEFAULT 0.00 -- Store the true average rating [1,5]
);

CREATE TABLE game_ratings (
    game VARCHAR(30) UNIQUE, -- Game the rating is for (30 is arbitrary)
    rating_count INT DEFAULT 0, -- Number of ratings
    rating_sum INT DEFAULT 0, -- Total sum of all ratings
    average_rating NUMERIC(3, 2) DEFAULT 0.00 -- Store the true average rating [1,5]
);
