USE bank_db;

CREATE TABLE user(
    id INT NOT NULL AUTO_INCREMENT,
    username VARCHAR(200) NOT NULL,
    password_hash CHAR(64) NOT NULL,
    salt CHAR(10),
    credit INT NOT NULL DEFAULT 0,
    totp_secret CHAR(32),

    PRIMARY KEY (id)
);

INSERT INTO user VALUES
    (DEFAULT, 'admin', '8fa739341a60b677d3c85f42c469f5115344115549dfe84494f25a1446b489d9', 'eOvmaxkU7A', 10000000, NULL);
