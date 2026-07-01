import { useEffect } from "react";
import { Button } from "@/components/ui/button";
import { ThemeToggle } from "@/components/core/theme-toggle";

import {
  useSession,
  useAgent,
} from "@livekit/components-react";

import { TokenSource } from "livekit-client";

import { AgentSessionProvider } from "@/components/agents-ui/agent-session-provider";
import { AgentAudioVisualizerBar } from "@/components/agents-ui/agent-audio-visualizer-bar";

const backendTokenUrl = import.meta.env.VITE_API_URL;
const TOKEN_SOURCE = TokenSource.endpoint(backendTokenUrl);

export default function App() {
  const session = useSession(TOKEN_SOURCE, {
    roomName: "quickbite-support",
  });

  useEffect(() => {
    let mounted = true;

    const connect = async () => {
      try {
        await session.start();
        console.log("Connected!");
      } catch (err) {
        console.error("Failed to start session:", err);
      }
    };

    if (mounted) {
      connect();
    }

    return () => {
      mounted = false;
      session.end();
    };
  }, [session]);

  return (
    <AgentSessionProvider session={session}>
      <AgentScreen />
    </AgentSessionProvider>
  );
}

function AgentScreen() {
  const { audioTrack,microphoneTrack, state } = useAgent();

  return (
    <div className="flex min-h-screen items-center justify-center p-6">
      <div className="flex w-full max-w-md flex-col gap-6 rounded-xl border p-6">

        <div className="flex items-center justify-between">
          <h1 className="text-2xl font-semibold">
            QuickBite Support
          </h1>

          <ThemeToggle />
        </div>

        <p className="text-muted-foreground">
          Connected to your LiveKit voice agent.
        </p>

        <AgentAudioVisualizerBar
          size="lg"
          barCount={5}
          state={state}
          audioTrack={microphoneTrack}
        />

        <Button>
          Get Started
        </Button>

        <div className="font-mono text-xs text-muted-foreground">
          Press <kbd>d</kbd> to toggle dark mode
        </div>

      </div>
    </div>
  );
}