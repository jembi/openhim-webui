use interoperability_layer;

create table sites (
	id int PRIMARY KEY NOT NULL AUTO_INCREMENT,
	name text NOT NULL,
	implementation_id int
) CHARSET=UTF8;

LOCK TABLES sites WRITE;
insert into sites values ('1', 'Avega', '547');
insert into sites values ('2', 'Gishari', '354');
insert into sites values ('3', 'Karenge', '355');
insert into sites values ('4', 'Musha', '357');
insert into sites values ('5', 'Ruhunda', '363');
UNLOCK TABLES;


create table report (
	id int PRIMARY KEY NOT NULL AUTO_INCREMENT,
	report_date date NOT NULL,
	site int NOT NULL.
	transaction_id int NOT NULL,
	KEY `Report Date` (`report_date`),
	KEY `Report Site` (`site`),
	CONSTRAINT 'report site' FOREIGN KEY (site) REFERENCES sites (id),
	CONSTRAINT 'report transaction' FOREIGN KEY (transaction_id) REFERENCES transaction_log (id)	
) CHARSET=UTF8;


create table indicator (
	id int PRIMARY KEY NOT NULL AUTO_INCREMENT,
	report_id int NOT NULL,
	name text NOT NULL,
	KEY `Indicator Name` (`name`),
	CONSTRAINT 'indicator report' FOREIGN KEY (report_id) REFERENCES report (id)
) CHARSET=UTF8;

create table data_element (
	id int PRIMARY KEY NOT NULL AUTO_INCREMENT,
	indicator_id int NOT NULL,
	name text NOT NULL,
	value text NOT NULL,
	datatype text,
	units text,
	KEY `Data Element Name` (`name`),
	CONSTRAINT 'data element indicator' FOREIGN KEY (indicator_id) REFERENCES indicator (id)
) CHARSET=UTF8;

