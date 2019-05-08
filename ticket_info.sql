select id, state_id, ticket_id, create_time, history_type_id, create_by
from ticket_history
where ticket_id in {0}