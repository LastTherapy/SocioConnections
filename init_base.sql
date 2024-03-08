CREATE TABLE IF NOT EXISTS tags (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255)
);

CREATE TABLE IF NOT EXISTS images (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255),
    spoiler BOOL
);

CREATE TABLE image_tags (
    image_id INTEGER,
    tag_id INTEGER,
    FOREIGN KEY (image_id) REFERENCES images(id),
    FOREIGN KEY (tag_id) REFERENCES tags(id)
);

CREATE TABLE IF NOT EXISTS chats (
    id SERIAL PRIMARY KEY,
    chat_id BIGINT NOT NULL UNIQUE,
    type VARCHAR(50),
    name VARCHAR(255),
    photo VARCHAR(255),
    update_date DATE
);

CREATE TABLE IF NOT EXISTS persons (
    id SERIAL PRIMARY KEY,
    person_id BIGINT NOT NULL UNIQUE,
    name VARCHAR(255),
    lastname VARCHAR(255),
    username VARCHAR(255),
    update_date DATE
);

CREATE TABLE IF NOT EXISTS messages (
    id SERIAL PRIMARY KEY,
    message_id BIGINT NOT NULL UNIQUE,
    chat_id BIGINT NOT NULL,
    from_user_id BIGINT NOT NULL,
    reply_to_message BIGINT,
    quote TEXT,
    type VARCHAR(50),
    text VARCHAR(4096),
    media_id VARCHAR(255),
    update_date DATE,
    FOREIGN KEY (chat_id) REFERENCES chats(chat_id),
    FOREIGN KEY (from_user_id) REFERENCES persons(person_id)
);

CREATE TABLE IF NOT EXISTS reaction (
    id SERIAL PRIMARY KEY,
    name VARCHAR(10)
);

CREATE TABLE IF NOT EXISTS reaction_messages (
    id SERIAL PRIMARY KEY,
    message_id BIGINT NOT NULL,
    reaction_id INT NOT NULL,
    user_id BIGINT NOT NULL,
    FOREIGN KEY (message_id) REFERENCES messages(message_id),
    FOREIGN KEY (reaction_id) REFERENCES reaction(id),
    FOREIGN KEY (user_id) REFERENCES persons(person_id)
);

CREATE TABLE IF NOT EXISTS persons_chats (
    id SERIAL PRIMARY KEY,
    person_id BIGINT NOT NULL,
    chat_id BIGINT NOT NULL,
    anon_posting BOOL,
    FOREIGN KEY (person_id) REFERENCES persons(person_id),
    FOREIGN KEY (chat_id) REFERENCES chats(chat_id)
);

CREATE TABLE IF NOT EXISTS chats_private_tags (
    id SERIAL PRIMARY KEY,
    chat_id BIGINT NOT NULL,
    tag_id BIGINT not null,
    FOREIGN KEY (chat_id) REFERENCES  chats(chat_id),
    FOREIGN KEY (tag_id) REFERENCES  tags(id)
);