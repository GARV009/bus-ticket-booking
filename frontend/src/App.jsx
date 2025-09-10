import React, { useEffect, useState } from "react";
import { fetchTrips } from "./api";
import SeatMap from "./components/SeatMap";

function App() {
  const [trips, setTrips] = useState([]);
  const [selectedTrip, setSelectedTrip] = useState(null);

  useEffect(() => {
    fetchTrips().then(setTrips);
  }, []);

  if (selectedTrip) {
    return <SeatMap tripId={selectedTrip} />;
  }

  return (
    <div style={{ padding: 20 }}>
      <h1>Bus Trips</h1>
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
