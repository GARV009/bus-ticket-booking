// frontend/src/components/SeatMap.jsx
import React, { useEffect, useState, useRef } from "react";
import { fetchTrip, holdSeats, purchase, releaseSeats } from "../api";
import { v4 as uuidv4 } from "uuid";

export default function SeatMap({ tripId, onBack }) {
  const [trip, setTrip] = useState(null);
  const [selected, setSelected] = useState([]);
  const [holdInfo, setHoldInfo] = useState(null);
  const [countdown, setCountdown] = useState(null);
  const wsRef = useRef(null);
  const clientIdRef = useRef(uuidv4());

  // helper to normalize seats (add is_held flag)
  function normalizeTrip(raw) {
    if (!raw) return raw;
    return {
      ...raw,
      seats: raw.seats.map((s) => ({ ...s, is_held: s.is_held || false })),
    };
  }

  async function loadTrip() {
    const t = await fetchTrip(tripId);
    setTrip(normalizeTrip(t));
  }

  useEffect(() => {
    loadTrip();

    const ws = new WebSocket(`ws://localhost:8000/ws/trip/${tripId}/`);
    ws.onopen = () => {
      // console.log('ws open');
    };
    ws.onmessage = (ev) => {
      const msg = JSON.parse(ev.data);
      // handle initial held seats
      if (msg.type === "init" && msg.held_seat_ids) {
        const heldIds = msg.held_seat_ids;
        setTrip((prev) => {
          if (!prev) return prev;
          return {
            ...prev,
            seats: prev.seats.map((s) => (heldIds.includes(s.id) ? { ...s, is_held: true } : s)),
          };
        });
        return;
      }

      if (msg.type === "seat_event" && msg.event && Array.isArray(msg.seat_ids)) {
        const { event, seat_ids } = msg;
        setTrip((prev) => {
          if (!prev) return prev;
          return {
            ...prev,
            seats: prev.seats.map((s) => {
              if (seat_ids.includes(s.id)) {
                if (event === "sold") {
                  return { ...s, is_sold: true, is_held: false };
                } else if (event === "held") {
                  return { ...s, is_held: true };
                } else if (event === "released") {
                  return { ...s, is_held: false };
                }
              }
              return s;
            }),
          };
        });
      }

    };
    ws.onerror = (e) => {
      // optional: show error or reconnect
      console.error("WS error", e);
    };
    ws.onclose = () => {
      // console.log('ws closed');
    };
    wsRef.current = ws;
    return () => {
      try {
        ws.close();
      } catch (e) {}
    };
  }, [tripId]);

  useEffect(() => {
  if (holdInfo) {
    setCountdown(holdInfo.ttl);
    const iv = setInterval(async () => {
      setCountdown((c) => {
        if (!c) return c;
        if (c <= 1) {
          clearInterval(iv);

          // 🔹 Optimistic UI update (instant clear)
          setTrip((prev) => {
            if (!prev) return prev;
            return {
              ...prev,
              seats: prev.seats.map((s) =>
                holdInfo.held.includes(s.id) ? { ...s, is_held: false } : s
              ),
            };
          });

          // 🔹 Tell backend to release
          releaseSeats(tripId, holdInfo.held, holdInfo.hold_token)
            .then((resp) => {
              console.log("Released seats:", resp.released);
            })
            .catch((err) => console.error("Failed to release seats", err));

          setHoldInfo(null);
          setSelected([]);
          return null;
        }
        return c - 1;
      });
    }, 1000);
    return () => clearInterval(iv);
  }
}, [holdInfo, tripId]);


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

      // Immediately mark those seats as held in local state for instant feedback
      setTrip((prev) => {
        if (!prev) return prev;
        return {
          ...prev,
          seats: prev.seats.map((s) =>
            resp.held.includes(s.id) ? { ...s, is_held: true } : s
          ),
        };
      });
    } else {
      alert("Failed to hold: " + JSON.stringify(resp.failed || []));
      loadTrip();
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
      // local state will be updated by the 'sold' WS event, but update optimistically:
      setTrip((prev) => {
        if (!prev) return prev;
        return {
          ...prev,
          seats: prev.seats.map((s) =>
            holdInfo.held.includes(s.id) ? { ...s, is_sold: true, is_held: false } : s
          ),
        };
      });
    } else {
      alert("❌ Purchase failed: " + JSON.stringify(resp));
      // reload to reflect authoritative state
      loadTrip();
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
      <button onClick={onBack} style={{ marginBottom: 16 }}>⬅ Back</button>
      <h2>{trip.title} — {trip.origin} → {trip.destination}</h2>

      {Object.keys(rows).sort((a, b) => a - b).map((rowNum) => (
        <div key={rowNum} style={{ display: "flex", gap: 8, marginBottom: 8 }}>
          {rows[rowNum].map((s) => {
            const isSelected = selected.includes(s.id);
            const isHeld = s.is_held || (holdInfo?.held?.includes(s.id));
            const bg = s.is_sold
              ? "#f44336"
              : isHeld
              ? "#ff9800"
              : isSelected
              ? "#ffeb3b"
              : "#8bc34a";

            return (
              <div
                key={s.id}
                style={{
                  padding: 8,
                  background: bg,
                  color: s.is_sold || isHeld ? "white" : "black",
                  borderRadius: 4,
                  cursor: s.is_sold ? "not-allowed" : "pointer",
                  minWidth: 60,
                  textAlign: "center",
                }}
                onClick={() => !s.is_sold && toggleSeat(s.id)}
              >
                {s.seat_label}<br />₹{s.price}
              </div>
            );
          })}
        </div>
      ))}

      <div style={{ marginTop: 16 }}>
        <button onClick={onHold}>Hold</button>{" "}
        <button onClick={onPurchase}>Purchase</button>
      </div>

      {holdInfo && (
        <div style={{ marginTop: 16 }}>
          ⏳ Held: {holdInfo.held.join(", ")} — expires in {countdown}s
        </div>
      )}

      <div style={{ marginTop: 24 }}>
        <strong>Seat Legend:</strong>
        <div style={{ display: "flex", gap: 16, marginTop: 8 }}>
          <div style={{ background: "#8bc34a", padding: "4px 8px", borderRadius: 4 }}>Available</div>
          <div style={{ background: "#ffeb3b", padding: "4px 8px", borderRadius: 4 }}>Selected</div>
          <div style={{ background: "#ff9800", color: "white", padding: "4px 8px", borderRadius: 4 }}>Held</div>
          <div style={{ background: "#f44336", color: "white", padding: "4px 8px", borderRadius: 4 }}>Sold</div>
        </div>
      </div>
    </div>
  );
}
