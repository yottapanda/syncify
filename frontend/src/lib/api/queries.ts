import { SyncRequest, User } from "./types.ts";

export async function enqueueJob() {
  const response = await fetch("/api/v1/jobs", {
    method: "PUT",
    headers: {
      "Content-Type": "application/json",
      Accept: "application/json, application/problem+json",
    },
  });
  if (!response.ok) {
    throw new Error((await response.json()).detail);
  }
}

export async function getJobs() {
  const response = await fetch("/api/v1/jobs");
  if (!response.ok) {
    throw new Error((await response.json()).detail);
  }
  return (await response.json()) as SyncRequest[];
}

export async function getUser(): Promise<User> {
  const response = await fetch("/api/v1/auth/user", {
    headers: { "Content-Type": "application/json" },
  });
  if (!response.ok) {
    throw new Error((await response.json()).detail);
  }
  return await response.json();
}

export async function hasActiveSubscription(): Promise<boolean> {
  const response = await fetch("/api/v1/stripe/has_active_subscription");
  if (response.ok) {
    return await response.json();
  } else {
    throw new Error((await response.json()).detail);
  }
}

export async function subscribe() {
  const response = await fetch("/api/v1/stripe/subscribe");
  if (response.ok) {
    window.location.assign(await response.json());
  } else {
    throw new Error((await response.json()).detail);
  }
}

export async function manageSubscription() {
  const response = await fetch("/api/v1/stripe/manage");
  if (response.ok) {
    window.location.assign(await response.json());
  } else {
    throw new Error((await response.json()).detail);
  }
}

export async function handleLogin() {
  const response = await fetch("/api/v1/auth/login");
  if (response.ok) {
    window.location.assign(await response.json());
  } else {
    throw new Error((await response.json()).detail);
  }
}

export async function handleLogout() {
  const response = await fetch("/api/v1/auth/logout");
  if (response.ok) {
    window.location.reload();
  } else {
    throw new Error((await response.json()).detail);
  }
}
