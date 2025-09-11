const API_BASE = "/api"; // vite proxy will forward to backend

export async function fetchTrips() {
  const r = await fetch(`${API_BASE}/trips/`);
  return r.json();
}

export async function fetchTrip(tripId) {
  const r = await fetch(`${API_BASE}/trips/${tripId}/`);
  return r.json();
}

export async function holdSeats(tripId, seatIds, clientId) {
  const r = await fetch(`${API_BASE}/hold/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ trip_id: tripId, seat_ids: seatIds, client_id: clientId }),
  });
  return r.json();
}

export async function purchase(tripId, seatIds, holdToken, buyerEmail) {
  const r = await fetch(`${API_BASE}/purchase/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      trip_id: tripId,
      seat_ids: seatIds,
      hold_token: holdToken,
      buyer_email: buyerEmail,
    }),
  });
  return r.json();
}

// 🔹 NEW: release seats
export async function releaseSeats(tripId, seatIds, holdToken) {
  const r = await fetch(`${API_BASE}/release/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      trip_id: tripId,
      seat_ids: seatIds,
      hold_token: holdToken,
    }),
  });
  return r.json();
}

export async function login(username, password) {
  const r = await fetch(`${API_BASE}/auth/login/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ username, password }),
  });
  return r.json();
}

export async function createTrip(token, tripData) {
  const r = await fetch(`${API_BASE}/trips/create/`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`,
    },
    body: JSON.stringify(tripData),
  });
  return r.json();
}
