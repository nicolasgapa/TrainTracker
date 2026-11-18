# NEC Delay Tracker

How often each Acela and Northeast Regional train is late at each major
station between Washington and Boston.

- `collect.py` saves actual arrival times (and how late they were) from
  [amtrak.io](https://amtrak.io) to `data/arrivals.csv`. Python standard library only.
- `.github/workflows/collect.yml` runs it every hour and commits the new rows.
  Each run picks up everything since the last run, and re-saving a row never duplicates it.
- `index.html` reads the CSV and shows % late and the average delay for each train at each station.

## Run locally

```bash
python3 collect.py                 # fetch new arrivals
python3 -m http.server 8000        # then open http://localhost:8000
```

## Put it on GitHub

1. Push this folder to a GitHub repo.
2. Settings → Pages → Deploy from branch → `main` / root.
3. Actions tab → "Collect arrivals" → Run workflow (or wait for the hourly run).

Live data from Amtraker (ODC-By 1.0) via amtrak.io. Not affiliated with Amtrak.
