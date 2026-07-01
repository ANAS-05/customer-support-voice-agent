import logging
from dotenv import load_dotenv
from livekit import agents
from livekit.agents import Agent, AgentServer, AgentSession, room_io, JobContext
from livekit.plugins import cartesia, deepgram, groq, noise_cancellation, silero
from livekit.plugins.turn_detector.multilingual import MultilingualModel

from prompts import system_prompt

load_dotenv()
server = AgentServer()


class CustomerSupportAssistant(Agent):
    def __init__(self):
        super().__init__(
            instructions=system_prompt
        )

@server.rtc_session(agent_name="customer-support-assistant")
async def my_agent(context: JobContext):
    
    transcripts = []
    session = AgentSession(
        stt=deepgram.STT(model="nova-3-general"),
        llm=groq.LLM(model="openai/gpt-oss-120b"),
        tts=cartesia.TTS(model="sonic-3"),
        vad=silero.VAD.load(),
        turn_detection=MultilingualModel(),
    )

    @session.on("conversation_item_added")
    def on_item_added(event):
        item = event.item
        if item.text_content:
            transcripts.append({"role": item.role, "content": item.text_content})

    @session.on("close")
    def on_session_close():
        print("==================================")
        print(transcripts)
        print("==================================")

    await session.start(
        agent=CustomerSupportAssistant(),
        room=context.room,
        room_options=room_io.RoomOptions(
            audio_input=room_io.AudioInputOptions(
                # Background voice cancellation
                noise_cancellation=noise_cancellation.BVC(),
            )
        ),
    )

    await session.generate_reply(
        instructions="""
            Greet the customer warmly and introduce yourself as their QuickBite support agent.
            Keep the greeting brief (2 sentences max) and immediately invite them to share what you can help them with today.
            Sound friendly and natural — this is a voice call, not a chat window.
            Example tone: "Hi there, thanks for calling QuickBite support! I'm here to help — what can I do for you today?"
        """
    )

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    agents.cli.run_app(server)