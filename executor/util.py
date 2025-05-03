import requests
from executor.db_operations import get_telegram_account
async def send_message_to_telegram(message, data):
    """
    Simulate sending a message to a Telegram account.
    """
    if isinstance(message, dict):
        message = str(message)
        
    account = await get_telegram_account(data.get("data").get("accountId"))
    
    chat_id = data.get("data").get("chatId")
    if not chat_id.startswith("@"):
        chat_id = int(chat_id)
    
    response = requests.post(f"https://api.telegram.org/bot{account['token']}/sendMessage", 
                             data={
                                "chat_id": chat_id,
                                "text": message   
                                }
                )
    
    print("Telegram response:", response.status_code, response.text)
    return True