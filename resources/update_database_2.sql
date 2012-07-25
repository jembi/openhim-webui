use interoperability_layer;

alter table transaction_log add index `recieved_timestamp` (`recieved_timestamp`);
