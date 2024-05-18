DROP TABLE IF EXISTS chat_messages;
DROP TABLE IF EXISTS users;

CREATE TABLE users (
    user_id SERIAL PRIMARY KEY,
    username VARCHAR(50) NOT NULL,
    email VARCHAR,
    password VARCHAR,
    CONSTRAINT unique_user_params UNIQUE (username)
);

CREATE TABLE chat_messages
(
  message_id SERIAL PRIMARY KEY,
  sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  sender_id INT NOT NULL,
  message TEXT NOT NULL,
  FOREIGN KEY (sender_id) REFERENCES users(user_id)
);

DROP PROCEDURE IF EXISTS insert_message(VARCHAR, VARCHAR);
CREATE OR REPLACE PROCEDURE insert_message(
	user_name VARCHAR,
	message_text VARCHAR)
LANGUAGE plpgsql
AS $$
DECLARE
  m_message_id integer;
  m_user_id integer;
  m_user_name varchar := trim(user_name);
BEGIN
  INSERT INTO users(username)
  VALUES(m_user_name)
  on conflict(username) do nothing;
  select user_id into m_user_id from users
  where users.username = m_user_name;

  INSERT INTO chat_messages(sender_id, message)
  VALUES(m_user_id, message_text)
  returning message_id into m_message_id;
END;
$$;