const API_URL = import.meta.env.VITE_BACKEND_API_URL ?? "http://egoai-api.duckdns.org";

function getAuthHeaders() {
  const token = localStorage.getItem("access_token");
  const headers: Record<string, string> = { "Content-Type": "application/json" };
  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }
  return headers;
}

export async function fetchEvents() {
  const res = await fetch(`${API_URL}/api/v1/calendar/get_tasks`, {
    headers: getAuthHeaders(),
    credentials: "include",
  });
  if (!res.ok) throw new Error("Failed to fetch events");
  return res.json();
}

export async function createEvent(event: any) {
  // Map frontend event fields to backend expected fields
  const payload = {
    title: event.title,
    description: event.description,
    start_time: event.start || event.start_time,
    end_time: event.end || event.end_time,
    all_day: event.all_day ?? false,
    location: event.location ?? "",
    type: event.type
  };
  const res = await fetch(`${API_URL}/api/v1/calendar/set_task`, {
    method: "POST",
    headers: getAuthHeaders(),
    body: JSON.stringify(payload),
    credentials: "include",
  });
  if (!res.ok) throw new Error("Failed to create event");
  return res.json();
}

export async function deleteEvent(eventId: string) {
  const res = await fetch(`${API_URL}/api/v1/calendar/delete_task?event_id=${encodeURIComponent(eventId)}`, {
    method: "DELETE",
    headers: getAuthHeaders(),
    credentials: "include",
  });
  if (!res.ok) throw new Error("Failed to delete event");
  return res;
}
