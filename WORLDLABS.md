# World Labs integration

## Version and scope

The supported default is **Marble 1.1** (`marble-1.1`). World Labs lists it in the public [model catalogue](https://docs.worldlabs.ai/api/models). Atlas is a separate early-access product and is not required for this integration.

The implementation includes an owner-operated API client, resumable generation, existing-world import, a sanitized asset publisher, and an embedded Spark 2.2.0 viewer in the Simulation Suite. The viewer loads locally hosted SPZ files and applies the returned metric scale, ground-plane offset, and axis conversion. It supports keyboard, mouse, and touch exploration.

**No real generated scene is bundled yet.** A configured key with API credits or an accessible existing world is required to publish the first one. The renderer was tested with a clearly labeled synthetic SPZ fixture, which is not deployed as a hotel scene.

Marble generates scene geometry and appearance. It does not replace game logic, hotel jobs, shared agent state, character behavior, or permissions. The embedded viewer currently provides free exploration; it does not run the ten jobs or enforce collider physics. Collider assets are retained for subsequent navigation integration. The existing hotel and jobs remain operational.

## Credentials and cost

Create an API key at the [World Labs Platform](https://platform.worldlabs.ai/). API credits are separate from Marble web-app credits. Current [pricing](https://docs.worldlabs.ai/api/pricing) lists 1,580 credits for a Marble 1.1 text-generated world, approximately $1.264 at the published credit rate. Marble 1.1 Plus can incur additional variable generation charges.

Run the importer on your own trusted computer or a separate operator host, **outside the hotel service sandbox**. It accepts `WORLDLABS_API_KEY`, `--key-file` pointing to a private file containing only the key, or a hidden interactive prompt. Do not put the key in browser code, Git, the hotel API, a public asset directory, or chat.

There is no visitor-facing generation endpoint and no automated generation loop. The explicit `generate` command submits one paid request. A private journal prevents accidental duplicate submission to the same output directory.

## Generate the first scene

Use the supplied `worldlabs-hotel-prompt.txt`, or edit it before generating. From this repository:

```sh
python worldlabs_admin.py generate --model marble-1.1 --prompt-file worldlabs-hotel-prompt.txt --output worldlabs-private/grand-lobby
```

The command prompts privately for a key when no environment variable is set. It saves `operation.json` before polling and `world.json` on completion. Neither file is public. The private output directory is ignored by Git.

If polling times out, resume the existing job using the operation id from the journal:

```sh
python worldlabs_admin.py resume --operation OPERATION_ID --output worldlabs-private/grand-lobby
```

If the initial submission lost its response and the journal says `submitting`, inspect your World Labs account before doing anything else. Do not delete the journal and blindly submit again; the first request may have been charged.

## Import an existing world

Use a world id accessible to your API key:

```sh
python worldlabs_admin.py fetch --world WORLD_ID --output worldlabs-private/grand-lobby
```

A public Marble sharing link does not itself establish API access or a right to republish another creator's assets. Use a world you own or have permission to publish.

## Publish reviewed assets

```sh
python worldlabs_admin.py publish --world-file worldlabs-private/grand-lobby/world.json --destination assets/worldlabs --title "The Grand · Marble lobby" --camera 0 1.6 0
```

This downloads the lightweight 100k SPZ when available, falling back to 500k, and an optional collider. It writes `active.json` only after downloads succeed. The public manifest contains local filenames and rendering metadata, not provider credentials, signed URLs, original prompts, or private world permissions.

Asset downloads accept HTTPS from the explicitly approved World Labs CDN hosts, reject redirects, send no API key, and cap each asset at 64 MiB. If World Labs returns a new CDN hostname, review it before extending the allowlist; do not permit arbitrary URLs.

Run the site locally, open the Simulation Suite, and inspect the scene. Adjust the camera if the start point is inside furniture or outside the generated space. Camera values are in the converted Three.js coordinate frame.

Deploy the reviewed files to `/opt/grand-hotel-agents/assets/worldlabs/`, keeping them root-owned and readable by the service. Copy the SPZ/GLB files first and `active.json` last. Do not deploy `worldlabs-private` or the API key. The application detects the new manifest without a restart. Confirm the scene loads in desktop and mobile browsers before calling it ready.

## Security and tests

The live server still has a private network namespace and no outbound provider access. The browser loads only same-origin scene assets. WebAssembly and blob-worker permissions are scoped to the dedicated viewer document, not the rest of the site.

Run `python -m unittest test_worldlabs test_security -v`. Tests cover sanitized publication, denied external URLs/traversal, missing or invalid metadata, resumable operation flow, duplicate-charge prevention, and failed-download handling. Mock API tests do not establish that credentials work; a real authorized generation/import and visual review are still required.

References: [API quickstart](https://docs.worldlabs.ai/api), [rendering scale and coordinates](https://docs.worldlabs.ai/api/rendering-spz), [Spark documentation](https://sparkjs.dev/docs/).
