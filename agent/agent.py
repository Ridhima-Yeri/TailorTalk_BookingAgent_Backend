import parsedatetime
from datetime import datetime, timedelta
from calender.calender_utils import get_busy_slots, book_slot

cal = parsedatetime.Calendar()

# Add a simple state tracker (in-memory, per session)
conversation_state = {
    "awaiting_datetime": False,
    "pending_action": None,
    "suggested_time": None,
}

async def chat_with_agent(user_input: str) -> str:
    global conversation_state

    # Handle confirmation for suggested time
    if conversation_state.get("pending_action") == "confirm_suggested_time":
        if "yes" in user_input.lower():
            start_time = conversation_state["suggested_time"]
            end_time = start_time + timedelta(minutes=30)
            busy_slots = get_busy_slots(start_time, end_time)
            if not busy_slots:
                book_slot(start_time, end_time)
                conversation_state["pending_action"] = None
                conversation_state["suggested_time"] = None
                return f"✅ Great! You're booked for {start_time.strftime('%A, %d %B %Y at %I:%M %p')}."
            else:
                conversation_state["pending_action"] = None
                conversation_state["suggested_time"] = None
                return "❌ Sorry, that slot just got booked. Please suggest another time."
        elif "no" in user_input.lower():
            conversation_state["pending_action"] = None
            conversation_state["suggested_time"] = None
            conversation_state["awaiting_datetime"] = True
            return "No problem! Please tell me another date and time you'd like to book."
        else:
            return "Would you like to book the suggested slot? Please reply with 'yes' or 'no'."

    # If we are waiting for a date/time from the user
    if conversation_state["awaiting_datetime"]:
        time_struct, parse_status = cal.parse(user_input)
        if parse_status == 0:
            return "I couldn't understand the date or time. Please provide it in a format like 'July 5 2025 at 6pm'."
        start_time = datetime(*time_struct[:6])
        end_time = start_time + timedelta(minutes=30)
        busy_slots = get_busy_slots(start_time, end_time)
        if not busy_slots:
            book_slot(start_time, end_time)
            conversation_state["awaiting_datetime"] = False
            return f"✅ You're booked for {start_time.strftime('%A, %d %B %Y at %I:%M %p')}."
        else:
            new_start = start_time + timedelta(hours=1)
            conversation_state["pending_action"] = "confirm_suggested_time"
            conversation_state["suggested_time"] = new_start
            conversation_state["awaiting_datetime"] = False
            return (
                f"❌ Sorry, that time is already taken.\n"
                f"Would you like to book at {new_start.strftime('%A, %d %B %Y at %I:%M %p')} instead? (yes/no)"
            )

    # Try to parse date/time from the current input
    time_struct, parse_status = cal.parse(user_input)
    if parse_status == 0:
        # If user intent is to book but no date/time, ask for it
        if "book" in user_input.lower() or "appointment" in user_input.lower():
            conversation_state["awaiting_datetime"] = True
            return (
                "Sure! What date and time would you like to book your appointment?\n"
                "For example, you can say 'next Monday at 3pm' or 'July 5 2025 at 6pm'."
            )
        return (
            "Sorry, I couldn't understand your request.\n"
            "If you'd like to book an appointment, please say something like 'book an appointment'."
        )

    # If date/time is found, proceed as before
    start_time = datetime(*time_struct[:6])
    end_time = start_time + timedelta(minutes=30)
    busy_slots = get_busy_slots(start_time, end_time)
    if not busy_slots:
        book_slot(start_time, end_time)
        return f"✅ You're booked for {start_time.strftime('%A, %d %B %Y at %I:%M %p')}."
    else:
        new_start = start_time + timedelta(hours=1)
        conversation_state["pending_action"] = "confirm_suggested_time"
        conversation_state["suggested_time"] = new_start
        return (
            f"❌ Sorry, that time is already taken.\n"
            f"Would you like to book at {new_start.strftime('%A, %d %B %Y at %I:%M %p')} instead? (yes/no)"
        )