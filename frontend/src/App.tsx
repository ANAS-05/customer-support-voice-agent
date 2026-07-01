import { useEffect, useRef } from "react";
import { ThemeToggle } from "@/components/core/theme-toggle";

import {
  useSession,
  useAgent,
  ControlBar,
  BarVisualizer,
} from "@livekit/components-react";
import "@livekit/components-styles";

import { TokenSource } from "livekit-client";

import { AgentSessionProvider } from "@/components/agents-ui/agent-session-provider";

const backendTokenUrl = import.meta.env.VITE_TOKEN_ENDPOINT;
const TOKEN_SOURCE = TokenSource.endpoint(backendTokenUrl);
const SESSION_OPTIONS = { roomName: "quickbite-support1" };

export default function App() {
  const session = useSession(TOKEN_SOURCE, SESSION_OPTIONS);

  const sessionRef = useRef(session);
  sessionRef.current = session;

  useEffect(() => {
    const handleUnload = () => {
      sessionRef.current.end();
    };
    window.addEventListener("beforeunload", handleUnload);
    return () => {
      window.removeEventListener("beforeunload", handleUnload);
    };
  }, []);

  return (
    <AgentSessionProvider session={session}>
      <AgentScreen session={session} />
    </AgentSessionProvider>
  );
}

function AgentScreen({ session }: { session: ReturnType<typeof useSession> }) {
  const agent = useAgent();
  const { state, audioTrack, microphoneTrack, canListen } = agent;
  const connected = session.isConnected;
  const startingRef = useRef(false);

  const handleConnect = () => {
    if (startingRef.current || connected) return;
    startingRef.current = true;

    session
      .start()
      .then(() => console.log("Connected!"))
      .catch((err) => console.error("Failed to start session:", err))
      .finally(() => {
        startingRef.current = false;
      });
  };

  return (
    <div data-lk-theme="default" className="flex min-h-screen items-center justify-center p-6">
      <div className="flex w-full max-w-md flex-col gap-6 rounded-xl border p-6">
        <div className="flex items-center justify-between">
          <h1 className="text-2xl font-semibold">QuickBite Support</h1>
          <ThemeToggle />
        </div>

        <p className="text-muted-foreground">
          Connected to your LiveKit voice agent.
        </p>

        {connected ? (
          <>
            <p className="font-mono text-xs text-muted-foreground">
              Agent state: {state}
            </p>
            {canListen && microphoneTrack && (
              <BarVisualizer
                track={microphoneTrack}
                state={state}
                barCount={5}
                style={{ height: "120px" }}
              />
            )}
            {audioTrack && <p className="text-xs text-muted-foreground">Agent speaking...</p>}
            <ControlBar
              controls={{ microphone: true, camera: false, screenShare: false, chat: false, leave: true }}
            />
          </>
        ) : (
          <button
            onClick={handleConnect}
            className="rounded-md bg-primary px-4 py-2 text-primary-foreground hover:opacity-90"
          >
            Start call
          </button>
        )}

        <div className="font-mono text-xs text-muted-foreground">
          Press <kbd>d</kbd> to toggle dark mode
        </div>
      </div>
    </div>
  );
}
