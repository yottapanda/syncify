import { createFileRoute } from "@tanstack/react-router";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { enqueueJob, getJobs, handleLogout } from "@/lib/api/queries.ts";
import { Button } from "@/components/ui/button.tsx";
import { User } from "@/lib/api/types.ts";
import { RefreshCcw } from "lucide-react";
import { toast } from "sonner";
import { Progress } from "@/components/ui/progress.tsx";
import { formatDistanceToNow } from "date-fns";

export const Route = createFileRoute("/_authenticated/dashboard")({
  component: Dashboard,
});

function Dashboard() {
  const queryClient = useQueryClient();
  const user: User | undefined = queryClient.getQueryData(["user"]);

  const jobsQuery = useQuery({
    queryKey: ["jobs"],
    queryFn: getJobs,
    refetchInterval: (q) => {
      const jobs = q.state.data ?? [];
      if (jobs.some((job) => !job.completed)) {
        return 1000;
      }
      return 30000;
    },
  });

  const enqueueJobQuery = useQuery({
    queryKey: ["enqueueJob"],
    queryFn: async () => {
      await enqueueJob().catch((reason) => {
        toast(reason.message);
      });
      await queryClient.invalidateQueries({ queryKey: ["jobs"] });
      return null;
    },
    retry: false,
    enabled: false,
  });

  // Helper function to format dates as relative time
  const formatRelativeTime = (date: Date) =>
    formatDistanceToNow(date, { addSuffix: true });

  return (
    <div className="flex flex-col gap-4">
      <div className="flex items-center justify-space-between">
        <h1 className="flex-1 text-3xl font-bold">Syncify</h1>
        <div className="flex items-center gap-4">
          {user && (
            <>
              <a
                className="text-primary"
                href={`https://open.spotify.com/user/${user.id}`}
                target="_blank"
              >
                {user.display_name}
              </a>
              <Button
                variant="ghost"
                onClick={async () => {
                  await handleLogout().catch(() => {
                    toast("Logout failed");
                  });
                  await queryClient.invalidateQueries({ queryKey: ["user"] });
                }}
              >
                Logout
              </Button>
            </>
          )}
        </div>
      </div>
      <div className="flex items-center justify-end gap-4">
        <Button
          variant="outline"
          disabled={jobsQuery.isFetching}
          onClick={() => jobsQuery.refetch()}
        >
          <RefreshCcw /> Refresh
        </Button>
        <Button onClick={() => enqueueJobQuery.refetch()}>Enqueue Sync</Button>
      </div>
      <div className="overflow-x-auto">
        <table className="table-auto w-full border-collapse">
          <thead>
            <tr className="border-b">
              <th className="px-4 py-2 text-left">ID</th>
              <th className="px-4 py-2 text-left">Created</th>
              <th className="px-4 py-2 text-left">Song Count</th>
              <th className="px-4 py-2 text-left">Progress</th>
              <th className="px-4 py-2 text-left">State</th>
            </tr>
          </thead>
          <tbody>
            {jobsQuery.data?.map((job) => (
              <tr key={job.id} className="border-b">
                <td className="px-4 py-2">{job.id}</td>
                <td className="px-4 py-2">
                  {formatRelativeTime(new Date(job.created))}
                </td>
                <td className="px-4 py-2">{job.song_count}</td>
                <td className="px-4 py-2">
                  <Progress
                    value={!!job.completed ? 100 : job.progress * 100}
                  />
                </td>
                <td className="px-4 py-2">
                  {!!job.completed
                    ? `Completed ${formatRelativeTime(new Date(job.completed))}`
                    : job.progress === 0
                    ? "Queued"
                    : "Running"}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
