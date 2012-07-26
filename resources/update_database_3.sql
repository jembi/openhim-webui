use interoperability_layer;

ALTER TABLE transaction_log ADD flagged BOOLEAN;
ALTER TABLE transaction_log ADD reviewed BOOLEAN;

DELIMITER |
CREATE TRIGGER update_reviewed 
BEFORE INSERT ON `transaction_log` 
FOR EACH ROW 
BEGIN 
IF NEW.status = 3 THEN	
SET NEW.reviewed = 0;
END IF; 
END;
|
DELIMITER ;
