import { createFileRoute, useNavigate } from "@tanstack/react-router";
import { Button } from "@/components/ui/button.tsx";
import { getUser, handleLogin } from "@/lib/api/queries.ts";
import { useEffect } from "react";

export const Route = createFileRoute("/")({
  component: Index,
});

function Index() {
  const navigate = useNavigate();

  useEffect(() => {
    getUser()
      .then((user) => {
        if (user) {
          navigate({ to: "/dashboard" }).then();
        }
      })
      .catch();
  }, []);

  return (
    <div className="flex justify-center items-center min-h-screen">
      <div className="flex flex-col gap-4 items-center">
        <h1 className="text-3xl font-bold">Syncify</h1>
        <p>Sync your Spotify 'Liked Songs' playlist to a sharable one.</p>
        <Button onClick={handleLogin}>Login with Spotify</Button>
      </div>
    </div>
  );
}
