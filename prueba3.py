from fastapi import HTTPException, Request, status,APIRouter
from twilio.twiml.messaging_response import MessagingResponse
from service.bot2 import BotService 
import os
from twilio.rest import Client
from dotenv import load_dotenv
from models.session import Session
from config.Redis.redisClient import redis_client
# Cargar las variables de entorno
load_dotenv('variables.env')

TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER")

# Inicializar el cliente de Twilio
client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

bot_service = BotService(twilio_phone_number=TWILIO_PHONE_NUMBER)
router = APIRouter()




@router.post("/whatsapp")
async def bot_webhook(request: Request):
    data = await request.form()
    from_number = data.get('From')
    message_body = data.get('Body')
    
    if not from_number or not message_body:
        raise HTTPException(status_code=400, detail="Datos incompletos")
    
    
    message_body = message_body.strip().lower()
    response = MessagingResponse()
    
    # 1. Recuperar sesión desde Redis
    session_data = redis_client.get_session(from_number=from_number)
    session = Session.from_dict(session_data)
    
    
    # 2. Lógica del bot 
    if session.stage == "greet":
        bot_service.handle_greet_stage(session=session, response=response)
    elif session.stage == "ask_email":
        bot_service.handle_ask_email_stage(session=session, response=response, message_body=message_body)
    elif session.stage == "register_user":
        await bot_service.handle_register_user_stage(session=session, response=response, message_body=message_body, from_number=from_number)
    elif session.stage == "select_doctor":
        await bot_service.handle_select_doctor_stage(session=session, response=response, message_body=message_body, from_number=from_number)
    elif session.stage == "choose_day":  # 🚨 ¡NUEVA CONDICIÓN!
        await bot_service.handle_select_doctor_stage(session=session, response=response, message_body=message_body, from_number=from_number)
    elif session.stage == "choose_slot": # 🚨 ¡NUEVA CONDICIÓN!
        await bot_service.handle_select_doctor_stage(session=session, response=response, message_body=message_body, from_number=from_number)  
    elif session.stage == "choose_schedule":
        bot_service.handle_choose_schedule_stage(session=session, response=response, message_body=message_body)
    
    # user_sessions[from_number] = session
    
    # 3. Guardar la sesión actualizada en Redis (TTL de 24 horas)
    redis_client.save_session(from_number, session.to_dict())
    
    message_text = str(response) #.split('<Message>')[1].split('</Message>')[0]
    
    # Enviar el mensaje usando Twilio
    bot_service.send_twilio_message(from_number, message_text)
    
    
    return {"status": "ok"}
    
    
    