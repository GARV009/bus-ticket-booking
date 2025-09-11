import React, { useState } from "react";
import { createTrip } from "../api";

export default function TripCreateForm({ token, onCreated }) {
  const [form, setForm] = useState({
    title: "",
    origin: "",
    destination: "",
    depart_at: "",
    arrive_at: "",
    bus_type: "Standard",
    booking_opens_at: "",
    booking_closes_at: "",
    rows: 4,
    cols: 4,
    seat_price: 500,
  });

  function handleChange(e) {
    setForm({ ...form, [e.target.name]: e.target.value });
  }

  async function handleSubmit(e) {
    e.preventDefault();
    const resp = await createTrip(token, form);
    if (resp.id) {
      alert("✅ Trip created: " + resp.title);
      onCreated(); // reload trips
    } else {
      alert("❌ Failed: " + JSON.stringify(resp));
    }
  }

  return (
    <form onSubmit={handleSubmit} style={{ margin: "20px 0", padding: "20px", border: "1px solid #ccc", borderRadius: 8, maxWidth: 500 }}>
      <h2>Create Trip</h2>

      {[
        { label: "Trip Title", name: "title", type: "text" },
        { label: "Origin", name: "origin", type: "text" },
        { label: "Destination", name: "destination", type: "text" },
        { label: "Departure Time", name: "depart_at", type: "datetime-local" },
        { label: "Arrival Time", name: "arrive_at", type: "datetime-local" },
        { label: "Bus Type", name: "bus_type", type: "text" },
        { label: "Booking Opens At", name: "booking_opens_at", type: "datetime-local" },
        { label: "Booking Closes At", name: "booking_closes_at", type: "datetime-local" },
        { label: "Number of Rows", name: "rows", type: "number" },
        { label: "Number of Columns", name: "cols", type: "number" },
        { label: "Seat Price", name: "seat_price", type: "number" },
      ].map(({ label, name, type }) => (
        <div key={name} style={{ marginBottom: 12 }}>
          <label style={{ display: "block", fontWeight: "bold", marginBottom: 4 }}>{label}</label>
          <input
            name={name}
            type={type}
            value={form[name]}
            onChange={handleChange}
            style={{ width: "100%", padding: "8px", borderRadius: 4, border: "1px solid #ccc" }}
          />
        </div>
      ))}

      <button type="submit" style={{ padding: "10px 20px", borderRadius: 4, background: "#007bff", color: "white", border: "none" }}>
        Create Trip
      </button>
    </form>
  );
}
