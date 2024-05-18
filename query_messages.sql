--select * from chat_messages
--order by sent_at;

select message_id as id, sent_at as time, username as user, message as message
from chat_messages natural join users
where chat_messages.sender_id = users.user_id
order by sent_at;