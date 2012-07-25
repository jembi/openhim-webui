use interoperability_layer;

create table roles (
	id int PRIMARY KEY NOT NULL AUTO_INCREMENT,
	role text NOT NULL
) CHARSET=UTF8;

insert into roles values ('1', 'ADMIN');
insert into roles values ('2', 'USER');

create table users (
	id int PRIMARY KEY NOT NULL AUTO_INCREMENT,
	username text NOT NULL,
	password text NOT NULL,
	salt text NOT NULL
) CHARSET=UTF8;

insert into users values ('1', 'admin', '7f9956ae2906d44070725265185461d0', 'QxSRndIA6W');
insert into users values ('2', 'user', '048113e2846215a11f550301f723b6cf', 'QjmKaccAnN');

create table users_roles (
  users_id int NOT NULL,
  roles_id int NOT NULL,
  PRIMARY KEY  (users_id, roles_id),
  FOREIGN KEY (users_id) REFERENCES users(id),
  FOREIGN KEY (roles_id) REFERENCES roles(id)
) CHARSET=UTF8;

insert into users_roles values ('1', '1');
insert into users_roles values ('1', '2');
insert into users_roles values ('2', '2');

ALTER TABLE transaction_log ADD flagged BOOLEAN;
ALTER TABLE transaction_log ADD reviewed BOOLEAN;