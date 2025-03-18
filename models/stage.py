from enum import Enum

class BotStage(Enum):
    GREET = "greet"
    CHOOSE_ACTION = "choose_action"
    ASK_DNI_FOR_APPOINTMENTS = "ask_dni_for_appointments"
    ASK_DNI = "ask_dni"
    ASK_EMAIL = "ask_email"
    REGISTER_USER = "register_user"
    SELECT_DOCTOR = "select_doctor"
    CHOOSE_DAY = "choose_day"
    CHOOSE_SLOT = "choose_slot"
    CONFIRM_SLOT = "confirm_slot"
    GET_REASON = "get_reason"
    CONFIRM_APPOINTMENT = "confirm_appointment"