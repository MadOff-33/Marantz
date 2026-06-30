# Lenovo Audio Endpoint Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Configure the Lenovo Ubuntu host as a stable Spotify Connect and DLNA audio endpoint for the Marantz PM5005 through the Behringer UCA222 without regressing existing services.

**Architecture:** The plan audits the current Lenovo state first, validates the USB DAC locally, then adds a stable ALSA layer shared by `raspotify` and `gmediarender` or `gmrender-resurrect`. Both services are managed by `systemd`, and every meaningful state change is recorded in `/home/mike/audio-endpoint-report.md`.

**Tech Stack:** Ubuntu, ALSA, `raspotify`/`librespot`, `gmediarender` or `gmrender-resurrect`, `systemd`, SSH, Git

---

## File Structure

- `docs/superpowers/specs/2026-06-30-lenovo-audio-endpoint-design.md`
  Reference design validated by the user.
- `docs/superpowers/plans/2026-06-30-lenovo-audio-endpoint.md`
  Execution checklist for this intervention.
- `README.md`
  Short local project summary and operating notes.
- `notes/session-log.md`
  Optional operator notes captured during intervention.
- `/home/mike/audio-endpoint-report.md` on the Lenovo
  Ground-truth audit and validation report required by the specification.
- `/etc/asound.conf` on the Lenovo
  Shared ALSA routing for Spotify and DLNA.
- `/etc/raspotify/conf` on the Lenovo
  Spotify Connect configuration.
- `/etc/systemd/system/gmediarender.service` on the Lenovo
  Systemd unit if package mode or custom install is used.
- `/usr/local/bin/gmediarender` or `/usr/bin/gmediarender` on the Lenovo
  DLNA renderer binary path depending on installation path.

### Task 1: Create Local Project Scaffolding

**Files:**
- Create: `D:\projects\lenovo-audio-endpoint\README.md`
- Create: `D:\projects\lenovo-audio-endpoint\notes\session-log.md`
- Modify: `D:\projects\lenovo-audio-endpoint\.git`

- [ ] **Step 1: Create the note directory**

Run:

```powershell
New-Item -ItemType Directory -Force 'D:\projects\lenovo-audio-endpoint\notes' | Out-Null
```

Expected: command exits silently with code 0.

- [ ] **Step 2: Write the local README**

Content:

```markdown
# Lenovo Audio Endpoint

Local project workspace for the Lenovo Ubuntu audio endpoint intervention.

## Purpose

- Keep the validated design and execution plan in one place
- Track local notes while working
- Preserve a local Git history before any optional GitHub push

## Remote Target

- Host alias: `lenovo-openclaw`
- Expected user: `mike`
- Main objective: Spotify Connect plus DLNA renderer on the same ALSA endpoint
```

- [ ] **Step 3: Write the session note file**

Content:

```markdown
# Session Log

- 2026-06-30: Project initialized locally on D drive.
```

- [ ] **Step 4: Commit the scaffold**

Run:

```powershell
cd D:\projects\lenovo-audio-endpoint
git add README.md notes\session-log.md docs\superpowers\specs\2026-06-30-lenovo-audio-endpoint-design.md docs\superpowers\plans\2026-06-30-lenovo-audio-endpoint.md
git commit -m "chore: initialize local project workspace"
```

Expected: one initial commit containing the design, plan, and note files.

### Task 2: Audit The Lenovo Before Any Change

**Files:**
- Modify: `/home/mike/audio-endpoint-report.md`
- Test: Lenovo service state, network state, current audio inventory

- [ ] **Step 1: Confirm remote access and gather identity**

Run:

```powershell
ssh lenovo-openclaw "hostname; whoami; date -Is"
```

Expected: output shows host identity, user `mike`, and current timestamp.

- [ ] **Step 2: Create the report header and baseline sections**

Run:

```powershell
ssh lenovo-openclaw @'
mkdir -p /home/mike/audio-endpoint
{
  echo "# Rapport audio endpoint Lenovo"
  echo
  echo "Date: $(date -Is)"
  echo "Hostname: $(hostname)"
  echo
  echo "## OS"
  lsb_release -a 2>/dev/null || cat /etc/os-release
  echo
  echo "## Kernel"
  uname -a
  echo
  echo "## Reseau"
  ip -br addr
  echo
  echo "## Docker existant"
  docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" 2>/dev/null || true
  echo
  echo "## Services existants"
  systemctl status home-assistant --no-pager 2>/dev/null || true
  systemctl status homeassistant --no-pager 2>/dev/null || true
  systemctl status docker --no-pager 2>/dev/null || true
} | tee /home/mike/audio-endpoint-report.md
'@
```

Expected: report file created with OS, kernel, network, Docker, and service baseline.

- [ ] **Step 3: Append current audio and USB inventory**

Run:

```powershell
ssh lenovo-openclaw @'
{
  echo
  echo "## USB"
  lsusb
  echo
  echo "## ALSA aplay -l"
  aplay -l
  echo
  echo "## ALSA aplay -L"
  aplay -L
  echo
  echo "## Cartes ALSA"
  cat /proc/asound/cards
} | tee -a /home/mike/audio-endpoint-report.md
'@
```

Expected: Behringer UCA222 or similar USB audio codec appears in `lsusb` and ALSA listings.

- [ ] **Step 4: Capture initial non-regression checks**

Run:

```powershell
ssh lenovo-openclaw @'
{
  echo
  echo "## Verification Home Assistant"
  curl -I --max-time 5 http://127.0.0.1:8123 || true
  echo
  echo "## Verification OpenClaw"
  curl -I --max-time 5 http://127.0.0.1:8000 || true
} | tee -a /home/mike/audio-endpoint-report.md
'@
```

Expected: HTTP headers or connection evidence proving both local services still answer.

### Task 3: Validate The Behringer And Stabilize ALSA

**Files:**
- Modify: `/etc/asound.conf`
- Modify: `/home/mike/audio-endpoint-report.md`
- Test: direct ALSA playback to the Marantz path

- [ ] **Step 1: Test direct playback on current default output**

Run:

```powershell
ssh lenovo-openclaw "speaker-test -c 2 -t wav"
```

Expected: audible stereo test on the Marantz, or a clear ALSA error if default routing is wrong.

- [ ] **Step 2: Test the explicit USB audio device if needed**

Run:

```powershell
ssh lenovo-openclaw "aplay -l"
```

Then use the detected stable card name in:

```powershell
ssh lenovo-openclaw "speaker-test -D plughw:CARD=CODEC,DEV=0 -c 2 -t wav"
```

Expected: audible stereo test through the Behringer when the correct card name is used.

- [ ] **Step 3: Back up any existing ALSA config**

Run:

```powershell
ssh lenovo-openclaw "sudo cp -a /etc/asound.conf /etc/asound.conf.bak.\$(date +%Y%m%d-%H%M%S) 2>/dev/null || true"
```

Expected: backup created if `/etc/asound.conf` exists, otherwise no failure.

- [ ] **Step 4: Write the shared ALSA configuration**

Replace `CODEC` below with the actual stable card name from `aplay -l` or `/proc/asound/cards`.

Content:

```conf
pcm.!default {
    type plug
    slave.pcm "behringer_dmix"
}

ctl.!default {
    type hw
    card CODEC
}

pcm.behringer_hw {
    type hw
    card CODEC
    device 0
}

pcm.behringer_dmix {
    type dmix
    ipc_key 1024
    slave {
        pcm "behringer_hw"
        rate 44100
        channels 2
        period_time 0
        period_size 1024
        buffer_size 4096
    }
}

pcm.behringer {
    type plug
    slave.pcm "behringer_dmix"
}
```

Run:

```powershell
ssh lenovo-openclaw @'
sudo tee /etc/asound.conf >/dev/null <<'EOF'
pcm.!default {
    type plug
    slave.pcm "behringer_dmix"
}

ctl.!default {
    type hw
    card CODEC
}

pcm.behringer_hw {
    type hw
    card CODEC
    device 0
}

pcm.behringer_dmix {
    type dmix
    ipc_key 1024
    slave {
        pcm "behringer_hw"
        rate 44100
        channels 2
        period_time 0
        period_size 1024
        buffer_size 4096
    }
}

pcm.behringer {
    type plug
    slave.pcm "behringer_dmix"
}
EOF
'@
```

Expected: `/etc/asound.conf` updated successfully.

- [ ] **Step 5: Validate ALSA logical devices**

Run:

```powershell
ssh lenovo-openclaw @'
{
  echo
  echo "## Test ALSA behringer"
  speaker-test -D behringer -c 2 -t wav
  echo
  echo "## Test ALSA default"
  speaker-test -D default -c 2 -t wav
} | tee -a /home/mike/audio-endpoint-report.md
'@
```

Expected: both tests play through the Marantz without card-busy errors.

### Task 4: Install And Validate Spotify Connect

**Files:**
- Modify: `/etc/raspotify/conf`
- Modify: `/home/mike/audio-endpoint-report.md`
- Test: Spotify device discovery and playback

- [ ] **Step 1: Install Raspotify from the official installer**

Run:

```powershell
ssh lenovo-openclaw "sudo apt-get update && sudo apt-get -y install curl && curl -sL https://dtcooper.github.io/raspotify/install.sh | sh"
```

Expected: package installation completes and the `raspotify` service becomes available.

- [ ] **Step 2: Write the target Raspotify configuration**

Content:

```conf
LIBRESPOT_NAME="Marantz-Lenovo"
BITRATE="320"
LIBRESPOT_BACKEND="alsa"
LIBRESPOT_DEVICE="behringer"
```

Run:

```powershell
ssh lenovo-openclaw @'
sudo tee /etc/raspotify/conf >/dev/null <<'EOF'
LIBRESPOT_NAME="Marantz-Lenovo"
BITRATE="320"
LIBRESPOT_BACKEND="alsa"
LIBRESPOT_DEVICE="behringer"
EOF
sudo systemctl daemon-reload
sudo systemctl enable raspotify
sudo systemctl restart raspotify
'@
```

Expected: service restarts cleanly with the configured device name.

- [ ] **Step 3: Inspect service state and logs**

Run:

```powershell
ssh lenovo-openclaw @'
{
  echo
  echo "## raspotify status"
  systemctl is-enabled raspotify
  systemctl is-active raspotify
  systemctl status raspotify --no-pager
  echo
  echo "## raspotify logs"
  journalctl -u raspotify -n 100 --no-pager
} | tee -a /home/mike/audio-endpoint-report.md
'@
```

Expected: `enabled`, `active`, and no fatal ALSA backend errors.

- [ ] **Step 4: Validate on the iPhone**

Manual check:

```text
Open Spotify on the iPhone, choose the devices picker, confirm "Marantz-Lenovo" appears, start playback, and confirm audible sound on the Marantz.
```

Expected: Spotify playback works end to end without restarting the Lenovo.

### Task 5: Install And Validate The DLNA Renderer

**Files:**
- Modify: `/etc/systemd/system/gmediarender.service`
- Modify: `/home/mike/audio-endpoint-report.md`
- Test: DS Audio device discovery and playback

- [ ] **Step 1: Try the packaged renderer path first**

Run:

```powershell
ssh lenovo-openclaw "sudo apt-get update && sudo apt-get install -y gmediarender gstreamer1.0-alsa gstreamer1.0-plugins-base gstreamer1.0-plugins-good"
```

Expected: package install succeeds, or apt reports the package is unavailable.

- [ ] **Step 2: If the package is unavailable, build from official upstream**

Run:

```powershell
ssh lenovo-openclaw @'
sudo apt-get update
sudo apt-get install -y git build-essential autoconf automake libtool pkg-config \
  libglib2.0-dev libgstreamer1.0-dev libgstreamer-plugins-base1.0-dev \
  libupnp-dev gstreamer1.0-alsa gstreamer1.0-plugins-base gstreamer1.0-plugins-good
rm -rf /tmp/gmrender-resurrect
git clone https://github.com/hzeller/gmrender-resurrect.git /tmp/gmrender-resurrect
cd /tmp/gmrender-resurrect
./autogen.sh
./configure
make -j"$(nproc)"
sudo make install
'@
```

Expected: `gmediarender` installed under `/usr/local/bin/gmediarender`.

- [ ] **Step 3: Manually validate renderer startup**

Run:

```powershell
ssh lenovo-openclaw "timeout 20s gmediarender -f 'Marantz-Lenovo-DLNA' --gstout-audiosink=alsasink --gstout-audiodevice=behringer"
```

Expected: process starts without immediate ALSA or GStreamer failure.

- [ ] **Step 4: Create the systemd service**

Content:

```ini
[Unit]
Description=DLNA UPnP Renderer for Marantz via Behringer UCA222
After=network-online.target sound.target
Wants=network-online.target

[Service]
Type=simple
ExecStart=<absolute-path-to-gmediarender> -f Marantz-Lenovo-DLNA --gstout-audiosink=alsasink --gstout-audiodevice=behringer
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
```

Use the exact full path reported by `command -v gmediarender`, either `/usr/bin/gmediarender` for the package install or `/usr/local/bin/gmediarender` for the source-build fallback, and keep that same path in both the unit file and the write command below.

Run:

```powershell
ssh lenovo-openclaw @'
sudo tee /etc/systemd/system/gmediarender.service >/dev/null <<'EOF'
[Unit]
Description=DLNA UPnP Renderer for Marantz via Behringer UCA222
After=network-online.target sound.target
Wants=network-online.target

[Service]
Type=simple
ExecStart=<absolute-path-to-gmediarender> -f Marantz-Lenovo-DLNA --gstout-audiosink=alsasink --gstout-audiodevice=behringer
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF
sudo systemctl daemon-reload
sudo systemctl enable --now gmediarender
'@
```

Expected: systemd accepts the unit and the service starts.

- [ ] **Step 5: Inspect service state and logs**

Run:

```powershell
ssh lenovo-openclaw @'
{
  echo
  echo "## gmediarender status"
  systemctl is-enabled gmediarender
  systemctl is-active gmediarender
  systemctl status gmediarender --no-pager
  echo
  echo "## gmediarender logs"
  journalctl -u gmediarender -n 100 --no-pager
} | tee -a /home/mike/audio-endpoint-report.md
'@
```

Expected: `enabled`, `active`, and no fatal startup errors.

- [ ] **Step 6: Validate in DS Audio**

Manual check:

```text
Open DS Audio on the iPhone, verify that "Marantz-Lenovo-DLNA" appears as an output device, start NAS playback, and confirm audible sound on the Marantz.
```

Expected: DS Audio sees the renderer and playback works end to end.

### Task 6: Discovery, Conflict, And Final Validation

**Files:**
- Modify: `/home/mike/audio-endpoint-report.md`
- Test: discovery visibility, service coexistence, firewall impact, final acceptance

- [ ] **Step 1: Inspect firewall and network listeners**

Run:

```powershell
ssh lenovo-openclaw @'
{
  echo
  echo "## UFW"
  sudo ufw status verbose || true
  echo
  echo "## Ports audio reseau"
  sudo ss -tulpn | grep -E "gmediarender|1900|spotify|librespot|raspotify" || true
} | tee -a /home/mike/audio-endpoint-report.md
'@
```

Expected: enough evidence to decide whether discovery is blocked by firewall policy.

- [ ] **Step 2: Only if discovery fails, perform a reversible firewall diagnostic**

Run:

```powershell
ssh lenovo-openclaw @'
sudo ufw disable
sleep 5
sudo ufw --force enable
'@
```

Expected: non-interactive and used only for diagnosis, never left disabled, with the outcome documented in the report.

- [ ] **Step 3: Validate service handoff**

Run:

```powershell
ssh lenovo-openclaw @'
sudo systemctl restart raspotify
sudo systemctl restart gmediarender
{
  echo
  echo "## Logs apres redemarrage"
  journalctl -u raspotify -n 50 --no-pager
  journalctl -u gmediarender -n 50 --no-pager
} | tee -a /home/mike/audio-endpoint-report.md
'@
```

Manual check:

```text
Play Spotify, stop it, play DS Audio, stop it, then return to Spotify without rebooting the Lenovo.
```

Expected: both sources work in sequence without manual service edits or machine restart.

- [ ] **Step 4: Capture final acceptance state**

Run:

```powershell
ssh lenovo-openclaw @'
{
  echo
  echo "## Validation finale"
  echo "### Services"
  systemctl is-enabled raspotify
  systemctl is-active raspotify
  systemctl status raspotify --no-pager
  systemctl is-enabled gmediarender
  systemctl is-active gmediarender
  systemctl status gmediarender --no-pager
  echo
  echo "### Audio"
  aplay -l
  aplay -L
  echo
  echo "### Home Assistant"
  curl -I --max-time 5 http://127.0.0.1:8123 || true
  echo
  echo "### OpenClaw"
  curl -I --max-time 5 http://127.0.0.1:8000 || true
} | tee -a /home/mike/audio-endpoint-report.md
'@
```

Expected: report contains enough evidence to answer every acceptance criterion with yes or no.

- [ ] **Step 5: Commit the updated local notes**

Run:

```powershell
cd D:\projects\lenovo-audio-endpoint
git add README.md notes\session-log.md docs\superpowers\specs\2026-06-30-lenovo-audio-endpoint-design.md docs\superpowers\plans\2026-06-30-lenovo-audio-endpoint.md
git commit -m "docs: add execution plan for lenovo audio endpoint"
```

Expected: local Git history records the plan and any note updates.

## Self-Review

- Spec coverage checked: audit, ALSA, Spotify, DLNA, coexistence, firewall diagnostics, reporting, and non-regression all map to explicit tasks.
- Placeholder scan checked: no `TODO`, `TBD`, or vague implementation stubs remain.
- Type and path consistency checked: service names, output device names, and report path are consistent across tasks.
