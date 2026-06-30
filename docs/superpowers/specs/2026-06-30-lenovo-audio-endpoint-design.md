# Design - Lenovo Ubuntu as Spotify Connect and DLNA audio endpoint

## Objective

Turn the Lenovo Ubuntu host into a headless audio endpoint connected to the Marantz PM5005 through the Behringer UCA222 USB DAC, with two supported user flows:

- Spotify on iPhone -> Spotify Connect -> Lenovo -> Behringer UCA222 -> Marantz
- DS Audio on iPhone -> Synology Audio Station -> Lenovo DLNA renderer -> Behringer UCA222 -> Marantz

The Lenovo must expose:

- `Marantz-Lenovo` for Spotify Connect
- `Marantz-Lenovo-DLNA` for DLNA/UPnP rendering

The intervention must preserve existing services on the Lenovo, especially Home Assistant, OpenClaw, and Docker-managed workloads.

## Constraints

- Do not use Docker for the audio stack.
- Do not modify existing Docker containers.
- Do not perform general network reconfiguration without explicit need.
- Do not leave the firewall disabled.
- Do not treat the work as complete unless both Spotify Connect and DS Audio work end to end.
- Keep a local intervention report on the Lenovo at `/home/mike/audio-endpoint-report.md`.

## Recommended Approach

The recommended implementation is:

1. Audit the Lenovo state before any change.
2. Detect and validate the Behringer UCA222 locally with ALSA.
3. Create a stable ALSA configuration with logical devices named `behringer` and `behringer_dmix`.
4. Install and configure Raspotify using ALSA.
5. Install `gmediarender` from Ubuntu packages when available.
6. If the package is unavailable, compile `gmrender-resurrect` from its official upstream repository.
7. Run both services under `systemd` with automatic restart.
8. Validate Spotify, then DS Audio, then alternating playback between them.

This path is preferred because it stays aligned with the provided specification, minimizes moving parts, and keeps the operational model easy to maintain.

## Alternatives Considered

### Option A - Raspotify + packaged gmediarender + ALSA dmix

Best case path. Lowest maintenance cost and closest to the requested target architecture.

### Option B - Raspotify + upstream gmrender-resurrect build + ALSA dmix

Fallback when the Ubuntu package is missing or unusable. Slightly more technical overhead, but still acceptable because it uses the official project source.

### Option C - Different audio receiver stack

Rejected unless both A and B fail. This would drift from the requested architecture and increase troubleshooting cost for DS Audio compatibility.

## Target Architecture

### Spotify path

iPhone Spotify selects `Marantz-Lenovo`, which maps to a `raspotify` service backed by `librespot`. `librespot` outputs through ALSA to the logical device `behringer`, which resolves to the Behringer UCA222 and then the Marantz amplifier.

### DLNA path

DS Audio controls Synology Audio Station, which sends media to a DLNA/UPnP renderer on the Lenovo named `Marantz-Lenovo-DLNA`. That renderer outputs through the same ALSA layer and the same DAC.

### Audio device strategy

The Lenovo should expose a stable ALSA default backed by:

- `pcm.behringer_hw` for the hardware device
- `pcm.behringer_dmix` for shared access
- `pcm.behringer` as the service-facing device

The default ALSA device should point to `behringer_dmix` so that both Spotify and DLNA can share one consistent audio target and recover more gracefully from handoff between services.

## Execution Phases

### Phase 1 - Initial audit

Collect:

- date, hostname, Ubuntu version, kernel
- IP addresses and interfaces
- Docker state
- Home Assistant state
- OpenClaw reachability if locally testable
- current audio inventory with `lsusb`, `aplay -l`, `aplay -L`

All results are appended to `/home/mike/audio-endpoint-report.md`.

### Phase 2 - Hardware validation

Confirm the Behringer UCA222 is visible over USB and exposed by ALSA. Run direct speaker tests against default ALSA first, then against the explicit device if needed. Do not continue until local audio playback to the Marantz is confirmed or the lack of detection is documented.

### Phase 3 - ALSA stabilization

Back up `/etc/asound.conf` if present, then configure a stable logical routing layer. Use a card name when possible rather than a volatile card index. Re-test both `behringer` and `default` after configuration.

### Phase 4 - Spotify Connect setup

Install Raspotify from the official installer, configure:

- `LIBRESPOT_NAME="Marantz-Lenovo"`
- `LIBRESPOT_BACKEND="alsa"`
- `LIBRESPOT_DEVICE="behringer"` or `default` only if necessary
- `BITRATE="320"`

Enable the service at boot, collect logs, and validate device visibility from the iPhone.

### Phase 5 - DLNA renderer setup

Install `gmediarender` from packages first. If unavailable, build `gmrender-resurrect` from the official upstream source and create a dedicated `systemd` service with restart behavior. Validate renderer visibility in DS Audio and confirm playback through the Marantz.

### Phase 6 - Conflict and firewall diagnostics

If one service blocks the other:

- inspect ALSA errors in logs
- confirm both services target the same logical ALSA endpoint
- verify whether `dmix` resolves device contention

If network discovery fails:

- inspect current firewall state
- test only minimal and reversible diagnostic changes
- inspect active listeners before proposing any firewall rule

### Phase 7 - Final validation and reporting

Confirm:

- `raspotify` enabled and active
- `gmediarender` enabled and active
- local audio test passes
- Spotify playback passes
- DS Audio playback passes
- alternating handoff between Spotify and DS Audio works without manual Lenovo restarts
- Home Assistant and OpenClaw remain intact

## Error Handling and Rollback

The intervention should preserve rollback points:

- back up `/etc/asound.conf` before changes
- keep `systemd` unit files small and isolated
- disable only the new audio services if instability appears
- never stop Docker, Home Assistant, or OpenClaw unless an issue is directly tied to the intervention and explicitly documented

If the DLNA portion fails but Spotify works, the mission remains incomplete. The same applies in reverse.

## Acceptance Criteria

The work is complete only if all of the following are true:

- Behringer UCA222 is detected by USB and ALSA
- local sound reaches the Marantz
- Spotify on iPhone sees `Marantz-Lenovo` and plays audio successfully
- DS Audio sees `Marantz-Lenovo-DLNA` and plays NAS audio successfully
- Home Assistant remains available on port 8123
- OpenClaw remains available on port 8000
- `/home/mike/audio-endpoint-report.md` exists and documents the intervention

## Known Assumptions

- Spotify account is Premium Family, which satisfies librespot requirements.
- The Behringer UCA222 is already connected to the Lenovo and the Marantz through a line-level input.
- The iPhone is on the same local network as the Lenovo during testing.
- The user authorizes the official upstream build path for `gmrender-resurrect` if packaged `gmediarender` is unavailable.
