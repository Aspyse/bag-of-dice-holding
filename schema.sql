CREATE TABLE dice(
    user text,
    alias text,
    command text,
    emoji text,
    PRIMARY KEY (user, alias)
);