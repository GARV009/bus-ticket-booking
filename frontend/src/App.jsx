import React, { useEffect, useState } from "react";
import { fetchTrips, login } from "./api";
import SeatMap from "./components/SeatMap";
import TripCreateForm from "./components/TripCreateForm.jsx";

function App() {
  const [trips, setTrips] = useState([]);
  const [selectedTrip, setSelectedTrip] = useState(null);
  const [token, setToken] = useState(null);

  async function loadTrips() {
    const data = await fetchTrips();
    setTrips(data);
  }

  useEffect(() => {
    loadTrips();
  }, []);

  async function handleLogin() {
    const username = prompt("Username:");
    const password = prompt("Password:");
    const resp = await login(username, password);
    if (resp.access) {
      setToken(resp.access);
      alert("✅ Logged in");
    } else {
      alert("❌ Login failed");
    }
  }

  // ✅ Add back button support here
  if (selectedTrip) {
    return <SeatMap tripId={selectedTrip} onBack={() => setSelectedTrip(null)} />;
  }

  return (
  <div style={{ padding: 20 }}>
    <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
      <h1>Bus-Ticket_booking</h1>
      <div>
        <button onClick={handleLogin} style={{ marginRight: 10 }}>Login</button>
        <span>👤 <strong>user:</strong> <code>org1</code> | <strong>pass:</strong> <code>ine@2025</code></span>
      </div>
    </div>

    {token && (
      <TripCreateForm token={token} onCreated={loadTrips} />
    )}

    <ul>
      {trips.map((t) => (
        <li key={t.id}>
          {t.title} — {t.origin} → {t.destination}{" "}
          <button onClick={() => setSelectedTrip(t.id)}>View Seats</button>
        </li>
      ))}
    </ul>
  </div>
);

}

export default App;
