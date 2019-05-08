SET @date_threshold = '{0} 00:00:00';
SELECT DISTINCT t.id FROM ticket t
LEFT JOIN ticket_history th ON t.id = th.ticket_id
WHERE t.create_time > @date_threshold
AND th.state_id in {1}