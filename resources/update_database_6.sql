use interoperability_layer;

# ENSURE EXISTING TABLES ARE USING INNODB ENGINE RATHER THAN MYISAM.
# THERE ARE ISSUES CREATING THE FOREIGN KEYS IN THIS SCRIPT IF THE TRANSACTION_LOG TABLE USES THE MYISAM ENGINE.
ALTER TABLE roles ENGINE=INNODB;
ALTER TABLE status ENGINE=INNODB;
ALTER TABLE transaction_log ENGINE=INNODB;
ALTER TABLE users ENGINE=INNODB;
ALTER TABLE users_roles ENGINE=INNODB;

create table if not exists sites (
	id int PRIMARY KEY NOT NULL AUTO_INCREMENT,
	name varchar(255) NOT NULL,
	implementation_id int
) ENGINE=InnoDB CHARSET=UTF8;

LOCK TABLES sites WRITE;
insert into sites values ('1', 'Avega', '547');
insert into sites values ('2', 'Gishari', '354');
insert into sites values ('3', 'Karenge', '355');
insert into sites values ('4', 'Musha', '357');
insert into sites values ('5', 'Ruhunda', '363');
UNLOCK TABLES;

create table if not exists report (
	id int PRIMARY KEY NOT NULL AUTO_INCREMENT,
	report_date date NOT NULL,
	site int NOT NULL,
	transaction_id int NOT NULL,
	KEY report_date (report_date),
	KEY report_site (site),
	CONSTRAINT report_site FOREIGN KEY (site) REFERENCES sites (id),
	CONSTRAINT report_transaction FOREIGN KEY (transaction_id) REFERENCES transaction_log (id)	
) ENGINE=InnoDB CHARSET=UTF8;

create table if not exists indicator (
	id int PRIMARY KEY NOT NULL AUTO_INCREMENT,
	report_id int NOT NULL,
	name varchar(255) NOT NULL,
	KEY indicator_name (name),
	CONSTRAINT indicator_report FOREIGN KEY (report_id) REFERENCES report (id)
) ENGINE=InnoDB CHARSET=UTF8;

create table if not exists data_element (
	id int PRIMARY KEY NOT NULL AUTO_INCREMENT,
	indicator_id int NOT NULL,
	name varchar(255) NOT NULL,
	value varchar(255) NOT NULL,
	datatype varchar(255),
	units varchar(255),
	KEY data_element_name (name),
	CONSTRAINT data_element_indicator FOREIGN KEY (indicator_id) REFERENCES indicator (id)
) ENGINE=InnoDB CHARSET=UTF8;

