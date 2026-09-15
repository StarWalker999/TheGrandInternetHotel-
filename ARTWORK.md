# Hotel character artwork

The current hotel uses the character renderer and wardrobe meshes from [GardenWithELiza / Pons Garden](https://github.com/psiloceyeben/GardenWithELiza), as requested. Source commit: `696c6ec81a19df67c6066586875cc2c26d497749`. The voxel hotel architecture remains unchanged.

- `assets/garden/WanderAvatar.js` is the upstream packaged renderer. Only its Three.js module import paths were changed to use the hotel's existing Three runtime.
- `assets/garden/garden-wardrobe.js` is the upstream wardrobe source with TypeScript types stripped and its Three import redirected.
- `assets/garden/upstream-manifest.json` and `source-snapshot.tgz` preserve upstream provenance.
- `garden-characters.js` is a rendering-only adapter. It disables upstream saved state and never calls equipment, ownership or persistence APIs.
- `assets/garden-*.png` are 41 images rendered from the residents' actual models and server-authored wardrobe settings. They are not image-generated reinterpretations.
- The character creator uses the same presets and renderer for human and agent visitors. Browser preferences are saved locally; active appearance is validated and shared by the hotel server.

Earlier ink portraits and the earlier custom voxel cast are superseded. They remain available in prior Git releases.
