import httpx
from twilio.rest import Client
from typing import List
from twilio.twiml.messaging_response import MessagingResponse
from datetime import datetime, timedelta
from models.session import Session
from fastapi import HTTPException

class BotService:
    def __init__(self,twilio_phone_number):
        self.client = Client()
        self.twilio_phone_number = twilio_phone_number

    def handle_greet_stage(self, session:Session, response: MessagingResponse) -> None:
        response.message("Hola, ¿cómo te llamas?")
        session.stage = "ask_email"
        
    def handle_ask_email_stage(self, session: Session, response: MessagingResponse, message_body: str) -> None:
        session.name = message_body
        response.message(f"Gracias, {message_body}. Por favor, envíame tu correo electrónico.")
        session.stage = "register_user"

    async def handle_register_user_stage(self, session: Session, response: MessagingResponse, message_body: str, from_number: str) -> None:
        session.email = message_body
        user_data = {"name": session.name, "email": session.email}
        
        async with httpx.AsyncClient() as http_client:
            r = await http_client.post("http://localhost:8000/users/create", json=user_data)
            
            if r.status_code == 200:
                user_response = r.json()
                user_id = user_response.get("id")
                session.user_id = user_id
                response.message("Usuario registrado con éxito.")
                session.stage = "select_doctor"
                self.send_twilio_message(from_number, "Usuario registrado con éxito.")
                await self.send_doctor_list(response, from_number)
            else:
                self.send_twilio_message(from_number, f"Error al registrar el usuario: {r.text}")
                session.stage = "greet"

    async def send_doctor_list(self, response, from_number: str) -> None:
        async with httpx.AsyncClient() as http_client:
            r_doctors = await http_client.get("http://localhost:8000/doctors/")
            if r_doctors.status_code == 200:
                doctors = r_doctors.json()
                doctor_list = "\n".join([f"{i+1}. {doc['name']} (ID: {doc['id']})" for i, doc in enumerate(doctors)])
                self.send_twilio_message(from_number, f"Doctores disponibles:\n{doctor_list}\nPor favor, responde con el ID del doctor que deseas seleccionar.")
            else:
                self.send_twilio_message(from_number, f"Error al obtener la lista de doctores: {r_doctors.text}")

    
    async def handle_select_doctor_stage(self, session: Session, response: MessagingResponse, message_body: str, from_number: str) -> None:
        try:
            # Obtener el stage actual
            current_stage = session.stage

            if current_stage == "choose_day":
                await self.handle_day_selection(session, response, message_body, from_number)
            elif current_stage == "choose_slot":
                await self.handle_slot_selection(session, response, message_body, from_number)
            else:
                await self.handle_doctor_selection(session, response, message_body, from_number)
                

        except ValueError:
            response.message("Por favor, responde con un número válido.")
        except Exception as e:
            print(f"Error: {e}")
            response.message("Ocurrió un error al procesar tu solicitud.")

    async def handle_choose_schedule_stage(self, session: dict, response: MessagingResponse, message_body: str) -> None:
        try:
            schedule_choice = int(message_body) - 1
            schedules = session.get("schedules", [])
            if 0 <= schedule_choice < len(schedules):
                chosen_schedule = schedules[schedule_choice]
                appointment_data = {
                    "user_id": session["user_id"],
                    "doctor_id": session["doctor_id"],
                    "date": chosen_schedule["start_time"],
                    "reason": session.get("reason", "")
                }

                async with httpx.AsyncClient() as http_client:
                    r = await http_client.post("http://localhost:8000/appointments/create", json=appointment_data)
                    
                    if r.status_code == 200:
                        appointment = r.json()
                        response.message(f"Cita confirmada para el {appointment['date']} con el Doctor ID: {appointment['doctor_id']}.")
                        session["stage"] = "greet"  # Reiniciar la conversación
                    else:
                        response.message(f"Error al crear la cita: {r.text}")
            else:
                response.message("Por favor, selecciona un número de horario válido.")
        except (ValueError, IndexError):
            response.message("Por favor, selecciona un número de horario válido.")

    def send_twilio_message(self, to_number: str, message_body: str) -> None:
        self.client.messages.create(  
            to=to_number,
            from_=self.twilio_phone_number,
            body=message_body
        )
        

    def generate_time_slots(self, start_time: datetime, end_time: datetime, slot_duration_minutes: int = 30) -> List[str]:
        slots = []
        current_time = start_time
        while current_time < end_time:
            next_time = current_time + timedelta(minutes=slot_duration_minutes)
            slots.append(f"{current_time.strftime('%H:%M')} - {next_time.strftime('%H:%M')}")
            current_time = next_time
        print(f"Generando slots desde {start_time} hasta {end_time}: {slots}")
        return slots
    
    
    
    
    
    async def handle_doctor_selection(self, session: Session, response: MessagingResponse, message_body: str, from_number: str) -> None:
        """Maneja la selección del doctor."""
        doctor_id = int(message_body)
        session.doctor_id = doctor_id

        async with httpx.AsyncClient() as http_client:
            r_schedules = await http_client.get(f"http://localhost:8000/schedules/doctor/{doctor_id}")

            if r_schedules.status_code == 200:
                schedules = r_schedules.json()
                days_text = "\n".join([f"{i+1}. {schedule['day']}" for i, schedule in enumerate(schedules)])
                response.message(f"Horarios disponibles para el Doctor {doctor_id}:\n{days_text}\nPor favor, responde con el número del día que deseas.")
                session.stage = "choose_day"
                session.schedules = schedules  # ATENCION POSIBLES ERRORES
                print(schedules)
            else:
                response.message(f"Error al obtener los horarios: {r_schedules.text}")


    async def handle_day_selection(self, session: Session, response: MessagingResponse, message_body: str,from_number: str) -> None:
        try:
            if not message_body.isdigit():
                response.message("⚠️ Por favor, responde con el número del día.")
                return

            selected_day_index = int(message_body) - 1  # Índice base 0

            # Validar que hay schedules disponibles
            if not session.schedules:
                response.message("❌ No hay horarios disponibles para este doctor.")
                session.stage = "greet"
                return

            # Validar índice del día
            if selected_day_index < 0 or selected_day_index >= len(session.schedules):
                response.message("❌ Número de día no válido.")
                return

            # Obtener el horario seleccionado
            selected_schedule = session.schedules[selected_day_index]
            session.selected_schedule = selected_schedule  # 🚨 Guardar en la sesión

            # Generar slots de tiempo (30 minutos)
            start_time = datetime.fromisoformat(selected_schedule["start_time"])
            end_time = datetime.fromisoformat(selected_schedule["end_time"])
            slots = self.generate_time_slots(start_time, end_time)

            if not slots:
                response.message("❌ No hay slots disponibles para este día.")
                return

            session.slots = slots  
            session.stage = "choose_slot"  

            print(f"Selected Schedule: {selected_schedule}")
            print(f"Slots generados: {slots}")

            # Construir mensaje con los slots
            slots_text = "\n".join([f"{i+1}. {slot}" for i, slot in enumerate(slots)])
            response.message(f"🕒 Slots disponibles para el {selected_schedule['day']}:\n{slots_text}\nResponde con el número del slot que deseas.")

        except Exception as e:
            print(f"Error en handle_day_selection: {str(e)}")
            response.message("❌ Ocurrió un error. Por favor, intenta de nuevo.")


    async def handle_slot_selection(self, session: Session, response: MessagingResponse, message_body: str, from_number: str) -> None:
        """Maneja la selección del slot."""
        if message_body.isdigit():
            selected_slot_index = int(message_body) - 1
            slots = session.slots

            if 0 <= selected_slot_index < len(slots):
                selected_slot = slots[selected_slot_index]
                session.selected_slot = selected_slot
                session.stage = "confirm_appointment"
                response.message(f"Has seleccionado el slot: {selected_slot}.")
            else:
                response.message("Número de slot no válido. Por favor, intenta de nuevo.")
        else:
            response.message("Por favor, responde con el número del slot que deseas.")



    def format_appointment_message(self, appointment: dict) -> str:
        appointment_date = datetime.fromisoformat(appointment["date"])
        formatted_date = appointment_date.strftime("%d/%m/%Y a las %I:%M %p")  # Ejemplo: 07/01/2025 a las 06:30 AM

        # Crear el mensaje formateado
        message = (
            "✅ *Cita confirmada* ✅\n\n"
            f"📅 *Fecha y hora:* {formatted_date}\n"
            f"🆔 *ID de la cita:* {appointment['id']}\n"
            f"📝 *Motivo:* {appointment['reason']}"
        )

        return message
        


    async def save_appointment(self, session: Session,response: MessagingResponse) -> None:
            try:
                # obtengo los datos necesarios para crear un appointment
                user_id = session.user_id
                doctor_id = session.doctor_id
                selected_slot = session.selected_slot # Ejemplo: "06:00 - 06:30"
                selected_schedule = session.selected_schedule # Contiene el día y horario entre otras cosas
                
                if not all([user_id, doctor_id, selected_slot, selected_schedule]):
                    raise ValueError("Faltan datos para crear la cita.")
                
                
                # saco la fecha de selected_schedule
                appointment_date = datetime.fromisoformat(selected_schedule["start_time"]).date()
                
                # convierto el slot a datetime
                start_time_str = selected_slot.split(" - ")[0]
                start_time = datetime.strptime(start_time_str, "%H:%M").time()
                
                # combino fecha y hora 
                appointment_datetime = datetime.combine(appointment_date,start_time)
                
                
                # creo el json para el endpoint
                appointment_data = {
                    "user_id": user_id,
                    "date":appointment_datetime.isoformat(),
                    "doctor_id": doctor_id,
                    "reason": "consulta nashe"
                }
                
                
                print(f"Cita a crear: {appointment_data}") # imprimo el json para ver si esta bien appointment_data
                
                # llamo al endpoint
                async with httpx.AsyncClient() as http_client:
                    response_endpoint = await http_client.post(
                    "http://localhost:8000/appointments/create",
                    json=appointment_data
                    )
                    
                    
                    if response_endpoint.status_code == 409:
                        raise HTTPException(status_code=409,detail=response.json()["detail"])
                    response_endpoint.raise_for_status()
                    
                    session.appointments = response_endpoint.json()
                    
                    
                    confirmation_message = self.format_appointment_message(session.appointments)
                    
                    response.message(confirmation_message)
                
                
            except HTTPException as e:
                response.message(f"❌ Error: {e.detail}")
            except Exception as e:
                print(f"Error no esperado: {e}")  
                response.message("❌ Ocurrió un error al confirmar la cita.")
                    
                
                    
                    