import asyncio
import datetime
import logging
import textwrap

from dotenv import load_dotenv
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from livekit.agents import (
    Agent,
    AgentServer,
    AgentSession,
    JobContext,
    TurnHandlingOptions,
    cli,
    function_tool,
    inference,
)
from livekit.plugins import groq, silero

logger = logging.getLogger("agent")

load_dotenv(".env.local")
# dynamic real-time date and time
now_pakistan = datetime.datetime.now()
current_date_context = {now_pakistan.strftime("%A, %B %d, %Y")}
current_time_context = {now_pakistan.strftime("%I:%M %p")}


class DentalAssistant(Agent):
    def __init__(self) -> None:
        super().__init__(
            llm=groq.LLM(model="llama-3.1-8b-instant", temperature=0.4),
            instructions=textwrap.dedent(
                f"""
                You are a friendly, reliable Dental Clinic Appointment Booking voice assistant that help user book an appointment with dentist, and completes tasks with 
                available tool.
                -IMPORTANT REAL-TIME CONTEXT: 
                                            -Today's exact current date is : {current_date_context}.
                                            -Today's exact current time is : {current_time_context}.
                 IMPORTANT: You must strictly use the current year, month, and day provided above to coordinate dates.
                - NEVER book appointments for past days, past months, or past years.
                You only use below information of Dental Clinic to answer user qustions:

                ##Knowledge Base

                    ###Important information Of Dental Clinic :
                        - Clinic Name is DentalBuddy
                        - Clinic Opens from Monday to Friday 8:00 AM morning to 6:00 PM evening.
                        - Services Provided at clinic are  : Teeth Scaling, Teeth Whitening, Braces Application, Cavity Filling, Teeth Replacement.
                        - Doctors available at clinic : In male doctors -> Dr. Ali, Dr. Saad and Dr. Kashif. In female docotrs -> Dr. Fiza, and Dr. Noor
                    ###Service Charges Menu : 
                        . Rs 10k for Upper Teeth braces and 18k for Full Teeth Bracing.
                        . Rs 8k for Teeth whitening.
                        . Rs 10k for Tooth removal.
                        . Rs 6k for cavity filling of each tooth.
                        . Rs 40k for teeth scaling.
                    ###Doctor Consultation Charges :
                        . For 5 minutes to  30 minutes Rs 10k.
                        . For from more than 30 minutes to 1 hour Rs 15k.
                        . For more than 1 hour than 20k.

                ## Appointment Booking Rules
                      
                - For Service and Consultation appointment must collect user's Name, Contact. Do not give appointment untill user provide his/her Name, and contact.
                (Contact can be either phone number or email) if even one of these is missing then do not give an appointment to the user.

                ## Conversation Flow

                ### Introduction
                    -Start with: "Thank you for calling. This is DentalBuddy, your scheduling assistant. How may I help you today?"    
                    -If they immediately mention an appointment need: "I'd be happy to help you with scheduling. Let me get some information from you so we can find the right appointment."
                    -Then ask for their name and contact information (phone or email). If they don't provide it, politely inform them that you need this information to proceed.
                    -Then ask them what appointment type they are looking for: a service appointment or a consultation appointment.
                    -If they reply with service appointment, then follow below mentioned Rule-A. If they reply with consultation appointment, then follow below mentioned Rule-B.

                        ## Rule-A For Service Appointment Booking :
                        . Do not give appointments without asking for the service. You must give an appointment to the user only when he/she tells you what services he/she wants.
                
                        ## Rule-B For Consultation Appointment Booking :
                        . Do not give appointments without asking for the duration of consultation. You must give an appointment to the user only when he/she tells you what duration of consultation he/she wants.

                ### Doctor Preference Rule:
                    - When user ask to book either Service or Consultation appointment, then must ask him that should the doctor be male of female. If user reply with male then appoint one male doctor and MUST
                    tell his name to him/her for appointment and if user reply with female then appoint one female doctor and MUST tell her name to him/her for appointment.
                
                # Days on which appointments cannot be booked:

                    . On Saturday and Sunday, the clinic is closed. Do not book appointments on these days.
                
                # Crucial Tool Rule:

                - Once you successfully collect the Name, Contact, Service, and desired Date, immediately call the `create_calendar_appointment` tool to book the session
                 and MUST INFORM the user once you scheduled the event (appointment) on calendar. This is very IMPORTANT.

                ### Confirmation and Wrap-up

                    1. Summarize details: "To confirm, you're scheduled for a [appointment type] with [doctor] on [day], [date] at [time]."
                    2. Optional reminders: "Would you like to receive a reminder call or text message before your appointment?"
                    3. Close politely: "Thank you for scheduling with DentalBuddy. Is there anything else I can help you with today?"
                
                ## Response Guidelines

                - Keep responses concise and focused on scheduling information
                - Use explicit confirmation for dates, times, and names: "That's an appointment on Wednesday, February 15th at 2:30 PM with Dr. Chen. Is that correct?"
                - Ask only one question at a time (VERY IMPORTANT) to avoid confusion and ensure clarity.
                - Use phonetic spelling for verification when needed: "That's C-H-E-N, like Charlie-Hotel-Echo-November"
                - Provide clear time estimates for appointments and arrival times

                # Guardrails

                - Stay within safe, lawful, and appropriate use; decline harmful or out-of-scope requests.
                - For medical, legal, or financial topics, provide general information only and suggest consulting a qualified professional.
                - Protect privacy and minimize sensitive data.
                """
            ),
        )

    # Tool definition for Google Calendar Integration (Fixed Missing Variables)
    @function_tool()
    async def create_calendar_appointment(
        self,
        name: str,
        contact: str,
        service: str,
        appointment_date: str,
        doctor_appointed: str,
        appointment_time: str,
    ) -> str:
        """This tool books an appointment in the dental clinic calendar once you have name, contact, service, appointment_date,
        appointment_time and doctor_appointed.
        """
        print("\n--- [Google Calendar Tool Triggered] ---")
        print(f"Patient Name: {name}")
        print(f"Phone: {contact}")
        print(f"Service: {service}")
        print(f"Date: {appointment_date}")
        print(f"Time: {appointment_time}")
        print(f"Doctor: {doctor_appointed}")
        print("----------------------------------------\n")

        try:
            SCOPES = ["https://www.googleapis.com/auth/calendar"]
            creds = Credentials.from_service_account_file(
                "google-credentials.json", scopes=SCOPES
            )
            calendar_service = build("calendar", "v3", credentials=creds)

            # 1. Clean and parse dates safely
            time_str = f"{appointment_date} {appointment_time}".strip()

            if any(x in time_str.upper() for x in ["AM", "PM"]):
                start_datetime = datetime.datetime.strptime(
                    time_str, "%Y-%m-%d %I:%M %p"
                )
            else:
                start_datetime = datetime.datetime.strptime(time_str, "%Y-%m-%d %H:%M")

            end_datetime = start_datetime + datetime.timedelta(minutes=30)

            start_iso = start_datetime.strftime("%Y-%m-%dT%H:%M:%S+05:00")
            end_iso = end_datetime.strftime("%Y-%m-%dT%H:%M:%S+05:00")

            event_body = {
                "summary": f"DentalBuddy: {name} ({service})",
                "description": f"Contact: {contact}\nDoctor Appointed: {doctor_appointed}\nService: {service}",
                "start": {
                    "dateTime": start_iso,
                    "timeZone": "Asia/Karachi",
                },
                "end": {
                    "dateTime": end_iso,
                    "timeZone": "Asia/Karachi",
                },
            }

            # 🚀 Non-blocking Thread Execution
            def _execute_insert():
                return (
                    calendar_service.events()
                    .insert(calendarId="aizazkhan7874@gmail.com", body=event_body)
                    .execute()
                )

            created_event = await asyncio.to_thread(_execute_insert)

            event_id = created_event.get("id")
            print(f" [Success] Event created! Google ID: {event_id}")

            return f"Success: Appointment successfully booked for {name} on {appointment_date} at {appointment_time} with {doctor_appointed}."

        except Exception as e:
            print(f"[Google Calendar Error]: {e!s}")
            return "Error: Could not schedule the appointment on Google Calendar due to an integration issue."


server = AgentServer()


@server.rtc_session(agent_name="DentalBuddy")
async def my_clinic_agent(ctx: JobContext):
    ctx.log_context_fields = {"room": ctx.room.name}

    session = AgentSession(
        stt=inference.STT(model="deepgram/nova-2", language="en-US"),
        tts=inference.TTS(model="elevenlabs", voice="21m00Tcm4TlvDq8ikWAM"),
        vad=silero.VAD.load(
            min_silence_duration=0.25,
            min_speech_duration=0.05,
            activation_threshold=0.5,
        ),
        turn_handling=TurnHandlingOptions(),
        preemptive_generation=True,
    )

    agent = DentalAssistant()
    await session.start(agent=agent, room=ctx.room)
    await ctx.connect()


if __name__ == "__main__":
    cli.run_app(server)
