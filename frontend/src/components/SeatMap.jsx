import React, { useEffect, useState, useRef } from "react";
import { fetchTrip, holdSeats, purchase } from "../api";
import { v4 as uuidv4 } from "uuid";

export default function SeatMap({ tripId }) {
  const [trip, setTrip] = useState(null);
  const [selected, setSelected] = useState([]);
  const [holdInfo, setHoldInfo] = useState(null);
  const [countdown, setCountdown] = useState(null);
  const wsRef = useRef(null);
  const clientIdRef = useRef(uuidv4());

  useEffect(() => {
    fetchTrip(tripId).then(setTrip);

    const ws = new WebSocket(`ws://localhost:8000/ws/trip/${tripId}/`);
    ws.onmessage = (ev) => {
      const msg = JSON.parse(ev.data);
      if (msg.type === "seat_event") {
        fetchTrip(tripId).then(setTrip);
      }
    };
    wsRef.current = ws;
    return () => ws.close();
  }, [tripId]);

  useEffect(() => {
    if (holdInfo) {
      setCountdown(holdInfo.ttl);
      const iv = setInterval(() => {
        setCountdown((c) => {
          if (!c) return c;
          if (c <= 1) {
            clearInterval(iv);
            setHoldInfo(null);
            setSelected([]);
            return null;
          }
          return c - 1;
        });
      }, 1000);
      return () => clearInterval(iv);
    }
  }, [holdInfo]);

  function toggleSeat(seatId) {
    setSelected((s) =>
      s.includes(seatId) ? s.filter((id) => id !== seatId) : [...s, seatId]
    );
  }

  async function onHold() {
    if (selected.length === 0) return alert("Select seats first");
    const resp = await holdSeats(tripId, selected, clientIdRef.current);
    if (resp.held && resp.held.length > 0) {
      setHoldInfo({ hold_token: resp.hold_token, held: resp.held, ttl: resp.ttl });
    } else {
      alert("Failed to hold: " + JSON.stringify(resp.failed || []));
      fetchTrip(tripId).then(setTrip);
    }
  }

  async function onPurchase() {
    if (!holdInfo) return alert("No active hold");
    const email = prompt("Enter buyer email:");
    const resp = await purchase(tripId, holdInfo.held, holdInfo.hold_token, email);
    if (resp.booking_id) {
      alert("✅ Purchased booking #" + resp.booking_id);
      setHoldInfo(null);
      setSelected([]);
      fetchTrip(tripId).then(setTrip);
    } else {
      alert("❌ Purchase failed: " + JSON.stringify(resp));
    }
  }

  if (!trip) return <div>Loading...</div>;

  const rows = {};
  trip.seats.forEach((s) => {
    if (!rows[s.row]) rows[s.row] = [];
    rows[s.row].push(s);
  });

  return (
    <div style={{ padding: 20 }}>
      <h2>{trip.title} — {trip.origin} → {trip.destination}</h2>
      {Object.keys(rows).sort((a, b) => a - b).map((rowNum) => (
        <div key={rowNum} style={{ display: "flex", gap: 8, marginBottom: 8 }}>
          {rows[rowNum].map((s) => {
            const isSelected = selected.includes(s.id);
            const bg = s.is_sold ? "#f44336" : isSelected ? "#ffeb3b" : "#8bc34a";
            return (
              <div
                key={s.id}
                style={{
                  padding: 8,
                  background: bg,
                  cursor: s.is_sold ? "not-allowed" : "pointer",
                }}
                onClick={() => !s.is_sold && toggleSeat(s.id)}
              >
                {s.seat_label} — ₹{s.price}
              </div>
            );
          })}
        </div>
      ))}
      <div style={{ marginTop: 16 }}>
        <button onClick={onHold}>Hold</button>
        <button onClick={onPurchase}>Purchase</button>
      </div>
      {holdInfo && (
        <div style={{ marginTop: 16 }}>
          Held: {holdInfo.held.join(", ")} — expires in {countdown}s
        </div>
      )}
    </div>
  );
}
