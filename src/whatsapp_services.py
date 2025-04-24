# from twilio.rest import Client
# from src.config import config

# class WhatsAppNotifier:
#     """Class for sending WhatsApp notifications"""
    
#     def __init__(self):
#         """Initialize Twilio client with credentials from config"""
#         self.client = Client(config.account_sid, config.auth_token)
#         self.from_number = 'whatsapp:+14155238886'  # Default Twilio WhatsApp number, update as needed
    
#     def send_notification(self, to_number, message):
#         """
#         Send a WhatsApp notification
        
#         Args:
#             to_number: Phone number to send the notification to (should include country code)
#             message: Message to send
            
#         Returns:
#             str: SID of the sent message
#         """
#         try:
#             # Format the to_number to WhatsApp format if not already
#             if not to_number.startswith('whatsapp:'):
#                 to_number = f'whatsapp:{to_number}'
                
#             message = self.client.messages.create(
#                 body=message,
#                 from_=self.from_number,
#                 to=to_number
#             )
            
#             return message.sid
#         except Exception as e:
#             print(f"Error sending WhatsApp notification: {str(e)}")
#             raise