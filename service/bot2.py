import httpx
from twilio.rest import Client
from typing import List
from twilio.twiml.messaging_response import MessagingResponse
from datetime import datetime, timedelta
from models.session import Session
from fastapi import HTTPException
from models.stage import BotStage
from config.Redis.redisClient import redis_client

class BotService:
    def __init__(self,twilio_phone_number):
        self.client = Client()
        self.twilio_phone_number = twilio_phone_number

    def handle_greet_stage(self, session:Session, response: MessagingResponse) -> None:
        response.message(
            "Hola, soy tu asistente virtual. ¿Qué deseas hacer?\n"
            "1. Sacar un nuevo turno.\n"
            "2. Ver mis turnos.\n"
            "3. Cancelar un turno"
        )
        session.stage = BotStage.CHOOSE_ACTION
        
        
    def handle_choose_action(self, session: Session, response: MessagingResponse, message_body: str) -> None:
        if message_body.strip() == "1":
            response.message("Vamos a sacar un nuevo turno. Por favor, envíame tu nombre completo.")
            session.stage = BotStage.ASK_DNI
        elif message_body.strip() == "2":
            response.message("Vamos a ver tus futuros turnos. Por favor, envíame tu DNI (solo los 8 números).")
            session.stage = BotStage.ASK_DNI_FOR_APPOINTMENTS
        elif message_body.strip() == "3":
            response.message("Vamos a cancelar un turno. Por favor, envíame tu DNI (solo los 8 números).")
            session.stage = BotStage.ASK_DNI_FOR_CANCEL # no existe
        else:
            response.message("Opción no válida. Por favor, responde con '1' o '2'.")
            
            
    async def get_user_id_by_dni(self, dni: str) -> int:
        async with httpx.AsyncClient() as http_client:
            r_user = await http_client.get(f"http://localhost:8000/users/dni/{dni}")
            if r_user.status_code == 200:
                user_data = r_user.json()
                return user_data.get("id")
            else:
                raise HTTPException(status_code=404, detail=f"Usuario con DNI {dni} no encontrado.")
            
            
            
    async def handle_ask_dni_for_appointments(self, session: Session, response: MessagingResponse, message_body: str) -> None:
        dni = message_body.strip()
        
        # Validar que el DNI tenga 8 dígitos
        if dni.isdigit() and len(dni) == 8:
            try:
                session.dni = dni
                # Obtener el user_id asociado al DNI
                user_id = await self.get_user_id_by_dni(dni)
                session.user_id = user_id
                
                
                # Obtener las citas futuras usando el endpoint
                async with httpx.AsyncClient() as http_client:
                    r_appointments = await http_client.get(f"http://localhost:8000/appointments/id/{user_id}")
                    
                    if r_appointments.status_code == 200:
                        appointments = r_appointments.json()
                        session.appointments = appointments
                        if appointments:
                            # Obtener los nombres de los doctores para cada cita
                            appointments_with_doctor_names = []
                            for appointment in appointments:
                                r_doctor = await http_client.get(f"http://localhost:8000/doctors/{appointment['doctor_id']}")
                                if r_doctor.status_code == 200:
                                    doctor_data = r_doctor.json()
                                    appointment["doctor_name"] = doctor_data.get("name", "Desconocido")
                                else:
                                    appointment["doctor_name"] = "Desconocido"
                                appointments_with_doctor_names.append(appointment)

                            # Formatear las citas para mostrarlas al usuario
                            appointments_text = "\n".join([
                                f"📅 Cita {i+1}:\n"
                                f"📅 Fecha: {appointment['date']}\n"
                                f"👨🏼‍⚕️ Doctor: {appointment['doctor_name']}\n"
                                f"📝 Motivo: {appointment['reason']}\n"
                                for i, appointment in enumerate(appointments_with_doctor_names)
                            ])
                            response.message(f"Tus citas futuras:\n{appointments_text}")
                            response.message("Gracias por usar nuestro servicio.")
                            session.stage = BotStage.GREET
                        else:
                            response.message("No tienes citas futuras.")
                            session.stage = BotStage.GREET
                    else:
                        response.message("Error al obtener las citas. Por favor, intenta de nuevo.")
            except HTTPException as e:
                response.message(f"❌ {e.detail}")
            except Exception as e:
                response.message("❌ Ocurrió un error. Por favor, intenta de nuevo.")
        else:
            response.message("El DNI debe tener exactamente 8 dígitos. Por favor, inténtalo de nuevo.")
            
    async def handle_ask_dni_for_cancel_appointments(self, session: Session, response: MessagingResponse, message_body: str) -> None:
        dni = message_body.strip()

        # Validar que el DNI tenga 8 dígitos
        if dni.isdigit() and len(dni) == 8:
            try:
                session.dni = dni
                # Obtener el user_id asociado al DNI
                user_id = await self.get_user_id_by_dni(dni)
                session.user_id = user_id
                
                
                
                # Obtener las citas futuras usando el endpoint
                async with httpx.AsyncClient() as http_client:
                    r_appointments = await http_client.get(f"http://localhost:8000/appointments/id/{user_id}")
                    
                    
                    
                    if r_appointments.status_code == 200:
                        appointments = r_appointments.json()
                        session.appointments = appointments
                        if appointments:
                            # Obtener los nombres de los doctores para cada cita
                            appointments_with_doctor_names = []
                            for appointment in appointments:
                                r_doctor = await http_client.get(f"http://localhost:8000/doctors/{appointment['doctor_id']}")
                                if r_doctor.status_code == 200:
                                    doctor_data = r_doctor.json()
                                    appointment["doctor_name"] = doctor_data.get("name", "Desconocido")
                                else:
                                    appointment["doctor_name"] = "Desconocido"
                                appointments_with_doctor_names.append(appointment)

                            # Formatear las citas para mostrarlas al usuario
                            appointments_text = "\n".join([
                                f"📅 Cita {i+1}:\n"
                                f"📅 Fecha: {appointment['date']}\n"
                                f"👨🏼‍⚕️ Doctor: {appointment['doctor_name']}\n"
                                f"📝 Motivo: {appointment['reason']}\n"
                                for i, appointment in enumerate(appointments_with_doctor_names)
                            ])
                            response.message(f"Turnos:\n{appointments_text}")
                            response.message("indique el numero de la cita que desea cancelar.")
                            session.stage = BotStage.SELECT_APPOINTMENT_TO_CANCEL 
                        else:
                            response.message("Error al obtener citas.")
                            session.stage = BotStage.GREET
                    elif r_appointments.status_code == 404:
                        response.message("No tienes citas futuras.")
                        session.stage = BotStage.GREET
            except HTTPException as e:
                response.message(f"❌ {e.detail}")
            except Exception as e:
                response.message("❌ Ocurrió un error. Por favor, intenta de nuevo.")
        else:
            response.message("El DNI debe tener exactamente 8 dígitos. Por favor, inténtalo de nuevo.")
            

    async def handle_select_appointment_to_cancel(self, session: Session, response: MessagingResponse, message_body: str) -> None:
        """Handles the selection of an appointment to cancel."""
        try:
            if not message_body.isdigit():
                response.message("⚠️ Por favor, responde con el número de la cita que deseas cancelar.")
                return

            appointment_index = int(message_body) - 1  # Convert to 0-based index
            
            # Get user's appointments from session or API
            
            appointments = session.appointments
            if appointments:
                    # Validate appointment index
                    if 0 <= appointment_index < len(appointments):
                        selected_appointment = appointments[appointment_index]
                        session.selected_appointment_id = selected_appointment['id'] # TENER CUIDADO WE
                        
                        # Get doctor details for confirmation message
                        async with httpx.AsyncClient() as http_client:
                            r_doctor = await http_client.get(f"http://localhost:8000/doctors/{selected_appointment['doctor_id']}")
                            doctor_name = r_doctor.json().get('name', 'Desconocido') if r_doctor.status_code == 200 else 'Desconocido'
                            
                            response.message(
                                f"⚠️ ¿Estás seguro que deseas cancelar esta cita?\n\n"
                                f"📅 Fecha: {selected_appointment['date']}\n"
                                f"👨‍⚕️ Doctor: {doctor_name}\n"
                                f"📝 Motivo: {selected_appointment['reason']}\n\n"
                                "Responde 'SÍ' para confirmar o 'NO' para volver atrás."
                            )
                            session.stage = BotStage.CONFIRM_CANCELATION
                    else:
                        response.message("❌ Número de cita inválido. Por favor, elige un número de la lista.")
            else:
                response.message("❌ Error al obtener tus citas. Por favor, intenta de nuevo.")
                session.stage = BotStage.GREET
                    
        except Exception as e:
            print(f"Error in handle_select_appointment_to_cancel: {str(e)}")
            response.message("❌ Ocurrió un error. Por favor, intenta de nuevo.")
            session.stage = BotStage.GREET
            
            
    async def handle_confirm_cancellation(self, session: Session, response: MessagingResponse, message_body: str) -> None:
        """Handles the actual cancellation of the selected appointment."""
        try:
            user_response = message_body.strip().lower()
            
            if user_response in ['sí', 'si', 's']:
                if not hasattr(session, 'selected_appointment_id'):
                    response.message("❌ No se encontró la cita seleccionada.")
                    session.stage = BotStage.GREET
                    return
                    
                    
                # get appointment from database
                async with httpx.AsyncClient() as http_client:
                    r_appointment = await http_client.get(f"http://localhost:8000/appointments/{session.selected_appointment_id}")
                    
                    if r_appointment.status_code == 200:
                        
                        appointment_data = r_appointment.json()
                        appointment_date = datetime.fromisoformat(appointment_data['date']).date()
                        slot_start = datetime.fromisoformat(appointment_data['date']).strftime("%H:%M")
                        slot_end = (datetime.fromisoformat(appointment_data['date']) + timedelta(minutes=30)).strftime("%H:%M")
                        slot = f"{slot_start} - {slot_end}"
                        
                        redis_client.remove_occupied_slot(
                            doctor_id=appointment_data['doctor_id'],
                            date=appointment_date.isoformat(),
                            slot=slot
                        )        
                    
                # Delete appointment from database
                async with httpx.AsyncClient() as http_client:
                    delete_response = await http_client.delete(
                        f"http://localhost:8000/appointments/delete/{session.selected_appointment_id}"
                    )
                    
                    
                    if delete_response.status_code == 200:
                        response.message("✅ Tu cita ha sido cancelada exitosamente.")
                    else:
                        response.message(f"❌ Error al cancelar la cita: {delete_response.text}")
            elif user_response in ['no', 'n']:
                response.message("✅ La cancelación ha sido cancelada. No se realizaron cambios.")
            else:
                response.message("⚠️ Por favor, responde 'SÍ' para confirmar o 'NO' para cancelar.")
                return
                
            session.stage = BotStage.GREET
            
            
        except Exception as e:
            print(f"Error in handle_confirm_cancellation: {str(e)}")
            response.message("❌ Ocurrió un error al procesar la cancelación.")
            session.stage = BotStage.GREET
            
            
        
    def handle_ask_dni_stage(self, session: Session, response: MessagingResponse, message_body: str) -> None:
        session.name = message_body.strip()  
        response.message(f"Gracias, {session.name}. Por favor, envíame tu DNI (solo los 8 números).")
        session.stage = BotStage.ASK_EMAIL
        
    def handle_ask_email_stage(self, session: Session, response: MessagingResponse, message_body: str) -> None:
        dni = message_body.strip()
    
        # Validar que el DNI tenga 8 dígitos
        if dni.isdigit() and len(dni) == 8:
            session.dni = dni  
            response.message("Por favor, envíame tu correo electrónico.")
            session.stage = BotStage.REGISTER_USER 
        else:
            response.message("El DNI debe tener exactamente 8 dígitos. Por favor, inténtalo de nuevo.")

    async def handle_register_user_stage(self, session: Session, response: MessagingResponse, message_body: str, from_number: str) -> None:
        session.email = message_body.strip().lower()
        
        user_data = {
        "name": session.name,
        "email": session.email,
        "dni": session.dni
        }
        
        async with httpx.AsyncClient() as http_client:
            r = await http_client.post("http://localhost:8000/users/create", json=user_data)
            
            if r.status_code == 200:
                user_response = r.json()
                user_id = user_response.get("id")
                session.user_id = user_id
                response.message("Usuario registrado con éxito. Ahora elige un médico.")
                session.stage = BotStage.SELECT_DOCTOR
                self.send_twilio_message(from_number, "Usuario registrado con éxito.")
                await self.send_doctor_list(response, from_number)
            elif r.status_code == 400:
            # Error en la validación (DNI ya registrado pero email no coincide)
                error_message = r.json().get("detail", "Error al registrar el usuario. Por favor, ingresa el email nuevamente.")
                response.message(error_message)
                session.stage = BotStage.ASK_EMAIL  # Volver a pedir el email
            else:
                response.message("Hubo un error al procesar tu solicitud. Por favor, inténtalo de nuevo más tarde.")
                session.stage = BotStage.GREET  # Reiniciar el proceso

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

            if current_stage == BotStage.CHOOSE_DAY:
                await self.handle_day_selection(session, response, message_body)
            elif current_stage == BotStage.CHOOSE_SLOT:
                await self.handle_slot_selection(session, response, message_body)
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
                        # session["stage"] = "greet"  
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
                session.stage = BotStage.CHOOSE_DAY
                session.schedules = schedules  
                print(schedules)
            elif r_schedules.status_code == 404:
                response.message(f"El Doctor {doctor_id} no tiene horarios disponibles o no existe, elija nuevamente.")
                await self.send_doctor_list(response, from_number)
                self.handle_select_doctor_stage(session, response, message_body, from_number)
            else:
                response.message(f"Error al obtener los horarios: {r_schedules.text}")


    async def handle_day_selection(self, session: Session, response: MessagingResponse, message_body: str) -> None:
        try:
            if not message_body.isdigit():
                response.message("⚠️ Por favor, responde con el número del día.")
                return

            selected_day_index = int(message_body) - 1  # Índice base 0

            # Validar que hay schedules disponibles
            if not session.schedules:
                response.message("❌ No hay horarios disponibles para este doctor.")
                session.stage = BotStage.GREET
                return

            # Validar índice del día
            if selected_day_index < 0 or selected_day_index >= len(session.schedules):
                response.message("❌ Número de día no válido.")
                return

            # Obtener el horario seleccionado
            selected_schedule = session.schedules[selected_day_index]
            session.selected_schedule = selected_schedule
            
            # Obtener los slots ocupados desde Redis
            occupied_slots_redis = redis_client.get_occupied_slots(
                doctor_id=session.doctor_id,                                                 
                date=selected_schedule["start_time"][:10]  # Extraer la fecha (YYYY-MM-DD)
            )

            # Obtener los slots ocupados en la DB
            async with httpx.AsyncClient() as http_client:
                r_appointments = await http_client.get(
                    f"http://localhost:8000/appointments/doctor_id/{session.doctor_id}"
                )
                if r_appointments.status_code == 200:
                    appointments = r_appointments.json()
                    # Extraer las horas de las citas y convertirlas al formato de slot
                    occupied_slots_db = set()
                    for appointment in appointments:                                                   
                        appointment_time = datetime.fromisoformat(appointment["date"])
                        slot_start = appointment_time.strftime("%H:%M")
                        slot_end = (appointment_time + timedelta(minutes=30)).strftime("%H:%M")
                        slot = f"{slot_start} - {slot_end}"
                        occupied_slots_db.add(slot)
                else:
                    occupied_slots_db = set()
            
            
            
            
            # Generar slots de tiempo (30 minutos)
            start_time = datetime.fromisoformat(selected_schedule["start_time"])
            end_time = datetime.fromisoformat(selected_schedule["end_time"])
            slots = self.generate_time_slots(start_time, end_time)

            if not slots:
                response.message("❌ No hay horarios disponibles para este día.")
                return
            
            occupied_slots = occupied_slots_redis.union(occupied_slots_db)                               
            
            # Filtrar los slots ocupados
            available_slots = [slot for slot in slots if slot not in occupied_slots]                     

            if not available_slots:
                response.message("❌ No hay horarios disponibles para este día.")                         
                return
            

            session.slots = available_slots                                             
            session.stage = BotStage.CHOOSE_SLOT  

            print(f"Selected Schedule: {selected_schedule}")
            print(f"Slots generados: {slots}")

            # Construir mensaje con los slots
            slots_text = "\n".join([f"{i+1}. {slot}" for i, slot in enumerate(available_slots)])                     
            response.message(f"🕒 Horarios disponibles para el {selected_schedule['day']}:\n{slots_text}\nResponde con el número del horario que deseas.")

        except Exception as e:
            print(f"Error en handle_day_selection: {str(e)}")
            response.message("❌ Ocurrió un error. Por favor, intenta de nuevo.")


    async def handle_slot_selection(self, session: Session, response: MessagingResponse, message_body: str) -> None:
        """Maneja la selección del slot."""
        if message_body.isdigit():
            selected_slot_index = int(message_body) - 1
            slots = session.slots

            if 0 <= selected_slot_index < len(slots):
                selected_slot = slots[selected_slot_index]
                session.selected_slot = selected_slot
                response.message(f"Has seleccionado el slot: {selected_slot}. ¿Confirmas este horario? (Responde 'sí' o 'no').")
                session.stage = BotStage.CONFIRM_SLOT  
            else:
                response.message("Número de horario no válido. Por favor, intenta de nuevo.")
        else:
            response.message("Por favor, responde con el número del horario que deseas.")
            
            
    async def handle_confirm_slot(self, session: Session, response: MessagingResponse, message_body: str) -> None:
        """Maneja la confirmación del slot seleccionado."""
        if message_body.strip().lower() in ["sí", "si", "s"]:
            response.message("Horario confirmado. Por favor, indica el motivo de la cita.")
            session.stage = BotStage.GET_REASON  
        elif message_body.strip().lower() in ["no", "n"]:
            response.message("Por favor, selecciona otro Horario.")
            session.stage = BotStage.CHOOSE_SLOT  
        else:
            response.message("Respuesta no válida. Por favor, responde 'sí' o 'no'.")



    def format_appointment_message(self, appointment: dict) -> str:
        appointment_date = datetime.fromisoformat(appointment["date"])
        formatted_date = appointment_date.strftime("%d/%m/%Y a las %I:%M %p")  

        # Crear el mensaje formateado
        message = (
            "✅ *Cita confirmada* ✅\n\n"
            f"📅 *Fecha y hora:* {formatted_date}\n"
            f"🆔 *ID de la cita:* {appointment['id']}\n"
            f"📝 *Motivo:* {appointment['reason']}"
        )

        return message
        
    def get_reason(self, session: Session, response: MessagingResponse, message_body: str) -> None:
        """Maneja la obtención del motivo de la cita."""
        session.reason = message_body.strip()  
        response.message(f"Motivo de la cita registrado: {session.reason}.")
        session.stage = BotStage.CONFIRM_APPOINTMENT  

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
                    "reason": session.reason
                }
                
                
                print(f"Cita a crear: {appointment_data}") # imprimo el json para ver si esta bien appointment_data
                
                # llamo al endpoint
                async with httpx.AsyncClient() as http_client:
                    response_endpoint = await http_client.post(
                    "http://localhost:8000/appointments/create",
                    json=appointment_data
                    )
                    
                    if response_endpoint.status_code == 200:
                        appointment = response_endpoint.json()
                        session.appointments = appointment

                        # Guardar el slot ocupado en Redis
                        redis_client.save_occupied_slot(
                            doctor_id=doctor_id,
                            date=appointment_date.isoformat(),
                            slot=selected_slot
                        )
                        
                        confirmation_message = self.format_appointment_message(session.appointments)
                    
                        response.message(confirmation_message)
                
                        session.stage = BotStage.GREET
                    
                        response_endpoint.raise_for_status()
                    
                    if response_endpoint.status_code == 409:
                        session.stage = BotStage.GREET 
                        raise HTTPException(status_code=409,detail=response_endpoint.json()["detail"])
                    
            except HTTPException as e:
                response.message(f"❌ Error: {e.detail}")
            except Exception as e:
                print(f"Error no esperado: {e}")  
                response.message("❌ Ocurrió un error al confirmar la cita.")
                    
                
    
        