import logging
from dotenv import load_dotenv
from livekit import agents
from livekit.agents import Agent, AgentServer, AgentSession, room_io, JobContext
from livekit.plugins import noise_cancellation
from livekit.agents import llm, stt, tts, inference


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

    # Configure the voice pipeline with STT, LLM, TTS, and VAD providers
    session = AgentSession(
        # LLM with fallback: OpenAI primary, Gemini backup
        llm=llm.FallbackAdapter(
            [
                inference.LLM(model="openai/gpt-4.1-mini"),
                inference.LLM(model="google/gemini-2.5-flash"),
            ]
        ),
        # STT with fallback: AssemblyAI primary, Deepgram backup
        stt=stt.FallbackAdapter(
            [
                inference.STT.from_model_string("assemblyai/universal-streaming:en"),
                inference.STT.from_model_string("deepgram/nova-3"),
            ]
        ),
        # TTS with fallback: Cartesia primary, Inworld backup
        tts=tts.FallbackAdapter(
            [
                inference.TTS.from_model_string("cartesia/sonic-3:9626c31c-bec5-4cca-baa8-f8ba9e84c8bc"),
                inference.TTS.from_model_string("inworld/inworld-tts-1"),
            ]
        ),
        turn_handling={
            "turn_detection": inference.TurnDetector(),
            "preemptive_generation": {"enabled": True},
        },
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