use interoperability_layer;

DELIMITER |
DROP TRIGGER IF EXISTS update_reviewed;
CREATE TRIGGER update_reviewed 
BEFORE UPDATE ON `transaction_log` 
FOR EACH ROW 
BEGIN 
IF NEW.status = 3 AND OLD.status = 1 THEN	
SET NEW.reviewed = 0;
END IF; 
END;
|
DELIMITER ;