import { createFileRoute } from "@tanstack/react-router";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import {
  enqueueJob,
  getJobs,
  handleLogout,
  hasActiveSubscription,
  manageSubscription,
  subscribe,
  deleteJob,
} from "@/lib/api/queries.ts";
import { Button } from "@/components/ui/button.tsx";
import { User } from "@/lib/api/types.ts";
import { LoaderCircle, RefreshCcw, X } from "lucide-react";
import { toast } from "sonner";
import { Progress } from "@/components/ui/progress.tsx";
import { formatDistanceToNow } from "date-fns";
import {
  Dialog,
  DialogClose,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog.tsx";
import { useState } from "react";

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

  const subscriptionQuery = useQuery({
    queryKey: ["subscription"],
    queryFn: async () => {
      return await hasActiveSubscription().catch((e) => {
        toast(e.message);
        return false;
      });
    },
  });

  const [manageLoading, setManageLoading] = useState(false);
  const [subscribeLoading, setSubscribeLoading] = useState(false);

  // Helper function to format dates as relative time
  const formatRelativeTime = (date: Date) =>
    formatDistanceToNow(date, { addSuffix: true });

  async function handleDelete(jobId: number) {
    await deleteJob(jobId).catch((e) => toast(e.message));
    await queryClient.invalidateQueries({ queryKey: ["jobs"] });
  }

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
      <div className="flex flex-wrap items-center justify-end gap-4">
        {subscriptionQuery.isLoading && (
          <LoaderCircle className="animate-spin" />
        )}
        {!subscriptionQuery.isLoading && subscriptionQuery.data && (
          <Button
            variant="link"
            disabled={manageLoading}
            onClick={() => {
              setManageLoading(true);
              manageSubscription()
                .catch((e) => toast(e.message))
                .finally(() => setManageLoading(false));
            }}
          >
            Syncing every 24 hours
          </Button>
        )}
        {!subscriptionQuery.isLoading && !subscriptionQuery.data && (
          <Dialog>
            <DialogTrigger asChild>
              <Button>Sync every 24 hours</Button>
            </DialogTrigger>
            <DialogContent>
              <DialogHeader>
                <DialogTitle>Purchase a Syncify Subscription</DialogTitle>
                <DialogDescription>
                  Syncify will run a sync job for you every day
                </DialogDescription>
              </DialogHeader>
              <DialogClose />
              <DialogFooter>
                <Button
                  variant="outline"
                  disabled={subscribeLoading}
                  onClick={() => {
                    setSubscribeLoading(true);
                    subscribe()
                      .catch((e) => toast(e.message))
                      .finally(() => setSubscribeLoading(false));
                  }}
                >
                  Subscribe
                </Button>
                <DialogClose asChild>
                  <Button variant="ghost">Cancel</Button>
                </DialogClose>
              </DialogFooter>
            </DialogContent>
          </Dialog>
        )}
        <Button onClick={() => enqueueJobQuery.refetch()}>Enqueue Sync</Button>
        <Button
          variant="outline"
          disabled={jobsQuery.isFetching}
          onClick={() => jobsQuery.refetch()}
        >
          <RefreshCcw /> Refresh
        </Button>
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
              <th className="px-4 py-2 text-left">Actions</th>
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
                <td className="px-4 py-2">
                  {job.progress === 0 && (
                    <Button
                      variant="outline"
                      onClick={() => handleDelete(job.id)}
                    >
                      <X /> Cancel
                    </Button>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
