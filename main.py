# Tutorial: https://www.youtube.com/watch?v=_o31SB3NLFk

import os
import pytz
from datetime import datetime
from supabase import create_client
from dotenv import load_dotenv
from fasthtml.common import *

# Load environment variables
load_dotenv()

MAX_NAME_CHAR=15
MAX_MESSAGE_CHAR=50
TIMESTAMP_FMT = "%Y-%m-%d %I:%M:%S %p CET"

# Initialize Supabase client
supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))

app,rt = fast_app()

def get_cet_time():
    cet_tz = pytz.timezone("CET")
    return datetime.now(cet_tz)

def add_message(name, message):
    timestamp = get_cet_time().strftime(TIMESTAMP_FMT)
    supabase.table("guestbook").insert(
        {"name": name, "message": message, "timestamp": timestamp}
    ).execute()

def get_messages():
    # Sort by 'id' in descending order go get the latest entries first
    response = supabase.table("guestbook").select("*").order("id", desc=True).execute()
    return response.data

def render_message(entry):
    return Article(
            Header(f"Name: {entry['name']}"),
            P(entry['message']),
            Footer(Small(Em(f"Posted: {entry['timestamp']}")))
        )

def render_message_list():
    messages = get_messages()

    return Div(
        *[render_message(entry) for entry in messages],
        id="message-list",
    )

def render_content():
    form = Form(
        Fieldset(
            Input(
                type="text",
                name="name",
                placeholder="Name",
                required=True,
                maxlength=MAX_NAME_CHAR
            ),
            Input(
                type="text",
                name="message",
                placeholder="Message",
                required=True,
                maxlength=MAX_MESSAGE_CHAR
            ),
            Button("Submit", type="submit"),
            role="group"
        ),
        method="post", 
        hx_post="/submit-message", # Send a POST request to the /submit-message endpoint
        hx_target="#message-list", # Only swap the message list
        hx_swap="outerHTML", # Replace the entire content of the target element with the response
        hx_on__after_request="this.reset()", # Reset the form after submission
    )

    return Div(
        P(Em("Write something nice!")),
        form,
        Div("Made with love by ", A("Chris", href="http://cnn.com", target="_blank")),
        Hr(),
        render_message_list()
    )

@rt('/')
def get(): return Titled("My Guestbook", render_content())

@rt('/submit-message', methods=["POST"])
def post(name: str, message: str):
    add_message(name, message)
    return render_message_list()

serve()