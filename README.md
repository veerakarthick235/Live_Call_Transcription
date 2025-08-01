# Live Call Transcription 📞➡️✍️

This project provides a real-time transcription service for live phone calls. When a user dials a configured phone number, their speech is converted to text by an AI service and displayed live on a web page. This serves as a foundational component for more advanced AI-driven call analysis solutions.

## Features

* **Real-time Audio Streaming:** Ingests live audio from a phone call using Twilio.
* **Live Speech-to-Text:** Transcribes speech in real-time using AssemblyAI.
* **Instant Frontend Updates:** Uses WebSockets to display the transcribed text on a webpage instantly.

## Tech Stack

* **Backend:** Python 3, FastAPI, Uvicorn
* **Telephony & Voice:** Twilio
* **Speech-to-Text:** AssemblyAI
* **Real-time Communication:** WebSockets
* **Frontend:** HTML, CSS, JavaScript
* **Tunneling (for local development):** `ngrok`

## Get API Keys & Accounts
You will need accounts for the following services:

Twilio: Sign up at twilio.com. You will need to:

Upgrade your account with a minimum payment to purchase a number.

Buy a phone number (a US number is recommended for best availability).

AssemblyAI: Sign up at assemblyai.com to get your free API key.

## Get API Keys & Accounts
You will need accounts for the following services:

Twilio: Sign up at twilio.com. You will need to:

Upgrade your account with a minimum payment to purchase a number.

Buy a phone number (a US number is recommended for best availability).

AssemblyAI: Sign up at assemblyai.com to get your free API key.


## How to Run the Project
This project requires three main components to be running simultaneously: the Python server, ngrok, and the web browser.

Step 1: Start the Backend Server
Open a terminal, navigate to the backend folder, and run the following command:
   ## python -m uvicorn main:app --reload
Keep this terminal running.

Step 2: Start ngrok
ngrok exposes your local server to the internet so Twilio can connect to it.

Open a new, separate terminal. On Windows, you must run it as an Administrator.

Run the following command:
##   ngrok http 8000

ngrok will display a Forwarding URL (e.g., https://random-string.ngrok-free.app). Copy this https URL.

Keep this terminal running.

Step 3: Configure the Twilio Webhook
Log in to your Twilio account.

Go to Phone Numbers > Manage > Active Numbers and click on your number.

Scroll down to the Voice Configuration section.

For the A CALL COMES IN webhook, paste your ngrok Forwarding URL and add /twilio at the end.

Example: https://random-string.ngrok-free.app/twilio

Ensure the method is set to HTTP POST and click Save.

## How to Test
Open the Frontend: In your web browser, navigate to http://localhost:8000. The page should load and the status should say "Connected. Waiting for call...".

Make the Call: Using another phone (e.g., Skype on your computer), call your Twilio phone number.

Observe: You will hear an automated message, "Transcription has started." Your spoken words will then appear live on the webpage.

