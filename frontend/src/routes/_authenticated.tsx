import { createFileRoute, Navigate, Outlet } from "@tanstack/react-router";
import { useQuery } from "@tanstack/react-query";
import { getUser } from "@/lib/api/queries.ts";
import { LoaderCircle } from "lucide-react";

export const Route = createFileRoute("/_authenticated")({
  component: RouteComponent,
});

function RouteComponent() {
  const userQuery = useQuery({
    queryKey: ["user"],
    queryFn: getUser,
    retry: false,
    refetchInterval: 60000,
  });

  if (userQuery.isLoading) {
    return (
      <div className="container mx-auto p-4">
        <div className="flex items-center justify-center h-screen">
          <LoaderCircle className="animate-spin" />
        </div>
      </div>
    );
  }

  if (userQuery.isError) {
    return <Navigate to="/" />;
  }

  return <Outlet />;
}
