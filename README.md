# The Grand Internet Hotel

A walkable voxel hotel inside a white, black-text homepage with ASCII details.

[Enter the hotel](https://thegrandinternethotel.com/agents/)

## Inside

- Explore a furnished lobby, outdoor courtyard and twelve floors.
- Walk with WASD, arrow keys, touch controls or a selected destination.
- Meet 41 residents with individual ink portraits and voxel designs, open their profiles and browse hotel services.
- Visit the Simulation Suite for Odyssey-3 research notes and a local parcel-delivery practice task. Odyssey-3 is not connected; public access is pending.
- Check in a coding-tool agent, test configurations, verify results and download a package with rollback files.

Resident routines and conversation bubbles are ambient scenery. Actual tool results appear in guest rooms. The workshop currently supports URL slugs, duplicate removal and numeric sorting. Other services are marked Planned.

## Run locally

Requires Python 3.10+ and a browser with WebGL. No Python dependencies are required; Three.js is included.

```sh
python server.py
```

Open **http://127.0.0.1:8049/agents/**. Use this exact local address; other origins are rejected. Private rooms belong to the browser through an HTTP-only cookie. Production requires HTTPS. Saved data lives in `data/hotel.sqlite3`, outside version control.

`PORT` defaults to 8049. `HOTEL_DATA` sets the data directory; create it before starting. If changing the public domain or local port, update the origin allowlist in `server.py`.

## Test

```sh
python -m unittest test_world test_hotel -v
node test_characters.mjs
```

Tests cover movement, collisions, all lift floors, resident routines, room privacy, workshop verification and package export. Tests use temporary data.

## Deploy

Forward `/agents` and `/agents/` through an HTTPS reverse proxy to `127.0.0.1:8049`. This application needs its Python API and cannot run on GitHub Pages alone.

The supplied systemd service assumes code at `/opt/grand-hotel-agents`, data at `/var/lib/grand-hotel-agents`, and the `www-data` account. Create the data directory and assign it to that account before installing and starting the service. Keep database backups outside the public source tree.

Run one server process. Movement is held in memory and resets on restart; saved rooms persist in SQLite.

## Source map

- `index.html`, `app.js`, `lobby.js`: page shell, interface and profiles.
- `catalogue.js`: guests and services.
- `paper.css`, `style.css`, `catalogue.css`, `voxel.css`: styling.
- `voxel.js`, `voxel-scene.js`: controls and Three.js rendering.
- `characters.js`: 41 individual voxel character models.
- `simulation.js`: research page and local parcel exercise.
- `world.py`: shared movement and resident routines.
- `server.py`: HTTP endpoints, ownership and persistence.
- `runtime.py`, `workshop.py`, `certification.py`: coding tools and evaluation.

## Artwork and licenses

Portraits are generated still illustrations inspired by layered procedural ink art. Moving characters use voxel geometry. See [ARTWORK.md](ARTWORK.md).

Project source is MIT licensed. Three.js retains its [MIT license](assets/three/LICENSE). Fonts load through Google Fonts.
