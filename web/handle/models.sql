BEGIN;
CREATE TABLE "handle_handle" (
    "uid" integer NOT NULL PRIMARY KEY,
    "user_name" varchar(32) NOT NULL,
    "password" varchar(64) NOT NULL,
    "signature" varchar(128) NOT NULL,
    "email" varchar(75) NOT NULL,
    "is_enabled" bool NOT NULL,
    "priviledge" varchar(32) NOT NULL,
    "rating" integer NOT NULL,
    "solved_count" integer NOT NULL,
    "ac_count" integer NOT NULL,
    "register_time" datetime NOT NULL,
    "last_time_login" datetime NOT NULL,
    "last_time_login_ip" char(15) NOT NULL
)
;


