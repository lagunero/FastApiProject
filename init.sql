CREATE TABLE IF NOT EXISTS user (
    id BLOB NOT NULL PRIMARY KEY,
    birth_date DATE,
    created_at TIMESTAMP,
    email VARCHAR,
    first_name VARCHAR,
    last_name VARCHAR,
    updated_at TIMESTAMP,
    password VARCHAR,
    role VARCHAR,
    user_name VARCHAR
);

INSERT INTO user (id, user_name, password, role, first_name, last_name, email, created_at, updated_at)
VALUES (X'a55a8e8e9a5c4dbb8caf82c7a67a3037', 'admin', 'admin', 'ADMIN', 'Admin', 'User', 'admin@example.com', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP);

INSERT INTO user (id, user_name, password, role, first_name, last_name, email, created_at, updated_at)
VALUES (X'ee261edc3f894996a0c218eb562d40a5', 'user', 'user', 'USER', 'Regular', 'User', 'user@example.com', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP);
