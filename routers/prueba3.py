from fastapi import HTTPException, Request, status,APIRouter
from twilio.twiml.messaging_response import MessagingResponse
from service.bot2 import BotService 
import os
from twilio.rest import Client
from dotenv import load_dotenv
from models.session import Session
from config.Redis.redisClient import redis_client
from models.stage import BotStage
import asyncio
import inspect
# Cargar las variables de entorno
load_dotenv('variables.env')

TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER")

# Inicializar el cliente de Twilio
client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

bot_service = BotService(twilio_phone_number=TWILIO_PHONE_NUMBER)
router = APIRouter()


STAGE_HANDLERS = {
    BotStage.GREET: bot_service.handle_greet_stage,
    BotStage.CHOOSE_ACTION: bot_service.handle_choose_action,
    BotStage.ASK_DNI_FOR_APPOINTMENTS: bot_service.handle_ask_dni_for_appointments,
    BotStage.ASK_DNI: bot_service.handle_ask_dni_stage,
    BotStage.ASK_EMAIL: bot_service.handle_ask_email_stage,
    BotStage.REGISTER_USER: bot_service.handle_register_user_stage,
    BotStage.SELECT_DOCTOR: bot_service.handle_select_doctor_stage,
    BotStage.CHOOSE_DAY: bot_service.handle_select_doctor_stage,
    BotStage.CHOOSE_SLOT: bot_service.handle_select_doctor_stage,
    BotStage.CONFIRM_SLOT: bot_service.handle_confirm_slot,
    BotStage.GET_REASON: bot_service.get_reason,
    BotStage.CONFIRM_APPOINTMENT: bot_service.save_appointment,
}

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
    
    
    # 2. Llamar al handler correspondiente según el stage
    handler = STAGE_HANDLERS.get(session.stage)
    
    try:
        handler_signature = inspect.signature(handler)
        handler_params = handler_signature.parameters

        handler_kwargs = {"session": session, "response": response}
        if "from_number" in handler_params:
            handler_kwargs["from_number"] = from_number
            
        if "message_body" in handler_params:
            handler_kwargs["message_body"] = message_body

        if asyncio.iscoroutinefunction(handler):
            await handler(**handler_kwargs)
        else:
            handler(**handler_kwargs)

    except Exception as e:
        response.message("Lo siento, ocurrió un error. Inténtalo de nuevo más tarde.")
        print(f"Error en el bot: {e}")
        
        
    # 3. Guardar la sesión actualizada en Redis (TTL de 24 horas)
    redis_client.save_session(from_number, session.to_dict())
    
    message_text = str(response).split('<Message>')[1].split('</Message>')[0]
    
    # Enviar el mensaje usando Twilio
    bot_service.send_twilio_message(from_number, message_text)
    
    
    return {"status": "ok"}
    

    
    
    