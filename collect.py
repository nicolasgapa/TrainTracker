"""Save actual NEC arrivals (Acela + Northeast Regional) to data/arrivals.csv.

Run it as often as you like (GitHub Actions runs it hourly). Each run picks up
everything that happened since the last run: the live feed keeps every past
stop of a running train, and finished trains stay in the feed for ~2 hours.
Rows are keyed by (origin_date, train, station), so overlapping runs never
create duplicates.
"""
import csv
import json
import os
import urllib.request
from datetime import datetime

API = "https://amtrak.io/api"
ROUTES = {"acela": "Acela", "northeast-regional": "Regional"}
STATIONS = ["WAS", "BAL", "WIL", "PHL", "NWK", "NYP", "STM", "NHV", "PVD", "BOS"]
CSV_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "arrivals.csv")
FIELDS = ["origin_date", "train", "route", "station", "event", "scheduled", "actual", "delay_min"]


def get(path):
    req = urllib.request.Request(API + path, headers={"User-Agent": "TrainTracker/1.0"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        body = json.load(resp)
    return body["data"] if body.get("ok") else None


def stop_row(train, stop):
    """One row for a stop the train has actually reached, else None.
    Uses arrival time; falls back to departure at a train's origin station."""
    for event in ("arrival", "departure"):
        if stop.get(event + "_kind") == "actual" and stop.get(event) and stop.get("scheduled_" + event):
            sched, actual = stop["scheduled_" + event], stop[event]
            delay = (datetime.fromisoformat(actual) - datetime.fromisoformat(sched)).total_seconds() / 60
            return {
                "origin_date": train["origin_date"],
                "train": train["number"],
                "route": ROUTES[train["route_id"]],
                "station": stop["code"],
                "event": event,
                "scheduled": sched,
                "actual": actual,
                "delay_min": round(delay),
            }
    return None


def main():
    rows = {}
    if os.path.exists(CSV_PATH):
        with open(CSV_PATH, newline="") as f:
            for r in csv.DictReader(f):
                rows[(r["origin_date"], r["train"], r["station"])] = r
    before = len(rows)

    trains = [t for t in get("/trains") or [] if t["route_id"] in ROUTES]
    for t in trains:
        data = get(f"/trains/{t['number']}?origin_date={t['origin_date']}&operator=amtrak") or {}
        detail = next((r for r in data.get("runs", []) if r["origin_date"] == t["origin_date"]), None)
        if not detail:
            continue
        for stop in detail.get("stops", []):
            if stop["code"] in STATIONS:
                row = stop_row(detail, stop)
                if row:
                    rows[(row["origin_date"], row["train"], row["station"])] = row

    os.makedirs(os.path.dirname(CSV_PATH), exist_ok=True)
    with open(CSV_PATH, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS, lineterminator="\n")
        w.writeheader()
        for key in sorted(rows):
            w.writerow(rows[key])
    print(f"{len(trains)} live NEC trains checked, {len(rows) - before} new arrivals, {len(rows)} total")


if __name__ == "__main__":
    main()
