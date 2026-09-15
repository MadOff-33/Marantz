# Lenovo Audio Endpoint — Intervention Report (versioned copy)

> **Provenance**
> - Source host: `lenovo-openclaw` (hostname `48sab`), file `/home/mike/audio-endpoint-report.md`
> - Source file MD5: `14f9d9346461d02f3f4ee1c109dc7f01`
> - Report period: 2026-06-30 (audit → ALSA stabilization → Spotify Connect → DLNA → final validation)
> - Imported: 2026-09-15
>
> **Redaction (public repo)**
> LAN host IPs → `<LAN_IP>` / `<LAN_IP_ETH>` / `<LAN_IP_WIFI>`, gateway → `<LAN_GW>`,
> subnet → `<LAN_SUBNET>`, global IPv6 → `<IPV6_GUA>`, link-local IPv6 → `<IPV6_LL>`,
> MAC addresses → `<MAC>`. Docker-internal ranges (172.17–19.0.0/16) kept as-is.

---

# Lenovo Audio Endpoint Audit Report

Audit timestamp: 2026-06-30T15:14:05+00:00  
Host: `48sab`  
Remote user: `mike`

## Scope

This report captures the pre-change baseline for the Lenovo audio endpoint target. This audit was read-only and did not modify Docker, network, services, or audio configuration.

## OS Baseline

- Distribution: Ubuntu 26.04 LTS (Resolute Raccoon)
- Kernel: `Linux 48sab 7.0.0-15-generic #15-Ubuntu SMP PREEMPT_DYNAMIC Wed Apr 22 16:06:43 UTC 2026 x86_64 GNU/Linux`

### `/etc/os-release`

```text
PRETTY_NAME="Ubuntu 26.04 LTS"
NAME="Ubuntu"
VERSION_ID="26.04"
VERSION="26.04 (Resolute Raccoon)"
VERSION_CODENAME=resolute
ID=ubuntu
ID_LIKE=debian
HOME_URL="https://www.ubuntu.com/"
SUPPORT_URL="https://help.ubuntu.com/"
BUG_REPORT_URL="https://bugs.launchpad.net/ubuntu/"
PRIVACY_POLICY_URL="https://www.ubuntu.com/legal/terms-and-policies/privacy-policy"
UBUNTU_CODENAME=resolute
LOGO=ubuntu-logo
```

## Network Baseline

### Interfaces

```text
lo               UNKNOWN        127.0.0.1/8 ::1/128
enp3s0           UP             <LAN_IP_ETH>/24 metric 100 <IPV6_GUA>/64 <IPV6_LL>/64
wlp5s0           UP             <LAN_IP_WIFI>/24 metric 600 <IPV6_GUA>/64 <IPV6_LL>/64
br-fffd1e46f118  UP             172.18.0.1/16 <IPV6_LL>/64
docker0          DOWN           172.17.0.1/16 <IPV6_LL>/64
br-a0b415f96454  UP             172.19.0.1/16 <IPV6_LL>/64
veth3df4acc@if2  UP             <IPV6_LL>/64
veth6985ffe@if2  UP             <IPV6_LL>/64
```

### Routes

```text
default via <LAN_GW> dev enp3s0 proto dhcp src <LAN_IP_ETH> metric 100
default via <LAN_GW> dev wlp5s0 proto dhcp src <LAN_IP_WIFI> metric 600
172.17.0.0/16 dev docker0 proto kernel scope link src 172.17.0.1 linkdown
172.18.0.0/16 dev br-fffd1e46f118 proto kernel scope link src 172.18.0.1
172.19.0.0/16 dev br-a0b415f96454 proto kernel scope link src 172.19.0.1
<LAN_SUBNET> dev enp3s0 proto kernel scope link src <LAN_IP_ETH> metric 100
<LAN_SUBNET> dev wlp5s0 proto kernel scope link src <LAN_IP_WIFI> metric 600
<LAN_GW> dev enp3s0 proto dhcp scope link src <LAN_IP_ETH> metric 100
<LAN_GW> dev wlp5s0 proto dhcp scope link src <LAN_IP_WIFI> metric 600
```

### Resolver

```text
nameserver 127.0.0.53
options edns0 trust-ad
search .
```

## Docker Baseline

- Docker version: `29.4.3`

### `docker ps`

```text
CONTAINER ID   IMAGE                                          COMMAND                  CREATED       STATUS                 PORTS                                                                                            NAMES
3ef792e3916b   ghcr.io/openclaw/openclaw:latest               "tini -s -- node ope…"   13 days ago   Up 11 days (healthy)   0.0.0.0:18789->18789/tcp, [::]:18789->18789/tcp, 0.0.0.0:8000->18789/tcp, [::]:8000->18789/tcp   openclaw
e1d166b664b6   cjd_dev:latest                                 "python app.py"          2 weeks ago   Up 2 weeks (healthy)   0.0.0.0:5050->5000/tcp, [::]:5050->5000/tcp                                                      cjd_flask
cd32fbf60ed3   ghcr.io/home-assistant/home-assistant:stable   "/init"                  7 weeks ago   Up 4 weeks                                                                                                              homeassistant
```

### `docker compose ls`

```text
NAME                STATUS              CONFIG FILES
cjd_dev             running(1)          /home/mike/cjd_dev/docker-compose.yml
domotique           running(1)          /home/mike/domotique/docker-compose.yml
openclaw            running(1)          /home/mike/openclaw/docker-compose.yml
```

## Service Baseline

- `docker.service`: active and enabled
- `systemd-networkd.service`: active and enabled
- `NetworkManager.service`: not present
- `avahi-daemon.service`: not present

### `systemctl status docker --no-pager --lines=12`

```text
Active: active (running) since Tue 2026-06-02 12:41:05 UTC; 4 weeks 0 days ago
Main PID: 1803 (dockerd)
Proxy listeners observed for ports 5050, 8000, and 18789.
```

### `systemctl status systemd-networkd --no-pager --lines=12`

```text
Active: active (running) since Thu 2026-06-11 06:39:01 UTC; 2 weeks 5 days ago
Main PID: 1024339 (systemd-networkd)
Recent log lines show Wi-Fi carrier changes on `wlp5s0` on 2026-06-29 before reconnection.
```

## USB Inventory

### `lsusb`

```text
Bus 001 Device 001: ID 1d6b:0002 Linux Foundation 2.0 root hub
Bus 001 Device 003: ID 04f2:b604 Chicony Electronics Co., Ltd Integrated Camera (1280x720@30)
Bus 001 Device 004: ID 06cb:00a2 Synaptics, Inc. Metallica MOH Touch Fingerprint Reader
Bus 001 Device 005: ID 8087:0a2a Intel Corp. Bluetooth wireless interface
Bus 001 Device 006: ID 08bb:2902 Texas Instruments PCM2902 Audio Codec
Bus 002 Device 001: ID 1d6b:0003 Linux Foundation 3.0 root hub
```

## Audio Inventory

### `/proc/asound/cards`

```text
 0 [PCH            ]: HDA-Intel - HDA Intel PCH
                      HDA Intel PCH at 0xf1420000 irq 147
 1 [CODEC          ]: USB-Audio - USB Audio CODEC
                      Burr-Brown from TI USB Audio CODEC at usb-0000:00:14.0-4, full speed
```

### `aplay -l`

```text
MISSING_COMMAND: aplay
```

### `aplay -L`

```text
MISSING_COMMAND: aplay
```

## Initial Non-Regression Checks

- Home Assistant local HTTP check on `127.0.0.1:8123`: `200`
- OpenClaw local HTTP check on `127.0.0.1:8000`: `200`

## Notes

- Both wired (`enp3s0`) and Wi-Fi (`wlp5s0`) are up, with wired preferred by route metric.
- Docker is active and currently exposing OpenClaw on port `8000` and an additional port `18789`.
- A USB audio device is present as `Texas Instruments PCM2902 Audio Codec` / `Burr-Brown USB Audio CODEC`.
- `aplay` is not installed, so ALSA playback device listings could not be captured during this audit.
- No audio, Docker, or network configuration changes were made during this task.
## ALSA Inventory Completion (2026-06-30)

- `aplay` was unavailable during the original audit.
- Passwordless sudo check failed: `sudo -n true` exited 1, so no package was installed system-wide.
- Minimal fallback used: downloaded `alsa-utils` and required library/data packages into a temporary directory and ran the packaged `aplay` binary without altering Docker, networking, firewall, or audio routing configuration.

### `aplay -l`

```text
aplay: device_list:279: no soundcards found...
```

### `aplay -L`

```text
null
    Discard all samples (playback) or generate zero samples (capture)
```
## Privilege and ALSA root-cause check (2026-06-30T15:27:48+00:00)
### id mike
uid=1000(mike) gid=1000(mike) groups=1000(mike),4(adm),24(cdrom),27(sudo),30(dip),46(plugdev),100(users),101(lxd),983(docker),982(ollama)
### /dev/snd
total 0
drwxr-xr-x  4 root root      340 Jun 30 14:45 .
drwxr-xr-x 20 root root     4380 Jun 30 14:45 ..
drwxr-xr-x  2 root root       60 Jun 30 14:45 by-id
drwxr-xr-x  2 root root      100 Jun 30 14:45 by-path
crw-rw----  1 root audio 116,  9 Jun  2 12:39 controlC0
crw-rw----  1 root audio 116, 12 Jun 30 14:45 controlC1
crw-rw----  1 root audio 116,  7 Jun  2 12:39 hwC0D0
crw-rw----  1 root audio 116,  8 Jun  2 12:39 hwC0D2
crw-rw----  1 root audio 116,  3 Jun  2 12:39 pcmC0D0c
crw-rw----  1 root audio 116,  2 Jun  2 12:39 pcmC0D0p
crw-rw----  1 root audio 116,  4 Jun  2 12:39 pcmC0D3p
crw-rw----  1 root audio 116,  5 Jun  2 12:39 pcmC0D7p
crw-rw----  1 root audio 116,  6 Jun  2 12:39 pcmC0D8p
crw-rw----  1 root audio 116, 11 Jun 30 14:45 pcmC1D0c
crw-rw----  1 root audio 116, 10 Jun 30 14:45 pcmC1D0p
crw-rw----  1 root audio 116,  1 Jun 11 06:39 seq
crw-rw----  1 root audio 116, 33 Jun 11 06:39 timer
### /proc/asound/cards
 0 [PCH            ]: HDA-Intel - HDA Intel PCH
                      HDA Intel PCH at 0xf1420000 irq 147
 1 [CODEC          ]: USB-Audio - USB Audio CODEC
                      Burr-Brown from TI USB Audio CODEC at usb-0000:00:14.0-4, full speed
## Privilege and ALSA root-cause check (2026-06-30T15:28:00+00:00)
### id mike
uid=1000(mike) gid=1000(mike) groups=1000(mike),4(adm),24(cdrom),27(sudo),30(dip),46(plugdev),100(users),101(lxd),983(docker),982(ollama)
### /dev/snd
total 0
drwxr-xr-x  4 root root      340 Jun 30 14:45 .
drwxr-xr-x 20 root root     4380 Jun 30 14:45 ..
drwxr-xr-x  2 root root       60 Jun 30 14:45 by-id
drwxr-xr-x  2 root root      100 Jun 30 14:45 by-path
crw-rw----  1 root audio 116,  9 Jun  2 12:39 controlC0
crw-rw----  1 root audio 116, 12 Jun 30 14:45 controlC1
crw-rw----  1 root audio 116,  7 Jun  2 12:39 hwC0D0
crw-rw----  1 root audio 116,  8 Jun  2 12:39 hwC0D2
crw-rw----  1 root audio 116,  3 Jun  2 12:39 pcmC0D0c
crw-rw----  1 root audio 116,  2 Jun  2 12:39 pcmC0D0p
crw-rw----  1 root audio 116,  4 Jun  2 12:39 pcmC0D3p
crw-rw----  1 root audio 116,  5 Jun  2 12:39 pcmC0D7p
crw-rw----  1 root audio 116,  6 Jun  2 12:39 pcmC0D8p
crw-rw----  1 root audio 116, 11 Jun 30 14:45 pcmC1D0c
crw-rw----  1 root audio 116, 10 Jun 30 14:45 pcmC1D0p
crw-rw----  1 root audio 116,  1 Jun 11 06:39 seq
crw-rw----  1 root audio 116, 33 Jun 11 06:39 timer
### /proc/asound/cards
 0 [PCH            ]: HDA-Intel - HDA Intel PCH
                      HDA Intel PCH at 0xf1420000 irq 147
 1 [CODEC          ]: USB-Audio - USB Audio CODEC
                      Burr-Brown from TI USB Audio CODEC at usb-0000:00:14.0-4, full speed

## Privilege and ALSA root-cause check (2026-06-30T15:28:40+00:00)
### id mike
uid=1000(mike) gid=1000(mike) groups=1000(mike),4(adm),24(cdrom),27(sudo),30(dip),46(plugdev),100(users),101(lxd),983(docker),982(ollama)

### /dev/snd
total 0
drwxr-xr-x  4 root root      340 Jun 30 14:45 .
drwxr-xr-x 20 root root     4380 Jun 30 14:45 ..
drwxr-xr-x  2 root root       60 Jun 30 14:45 by-id
drwxr-xr-x  2 root root      100 Jun 30 14:45 by-path
crw-rw----  1 root audio 116,  9 Jun  2 12:39 controlC0
crw-rw----  1 root audio 116, 12 Jun 30 14:45 controlC1
crw-rw----  1 root audio 116,  7 Jun  2 12:39 hwC0D0
crw-rw----  1 root audio 116,  8 Jun  2 12:39 hwC0D2
crw-rw----  1 root audio 116,  3 Jun  2 12:39 pcmC0D0c
crw-rw----  1 root audio 116,  2 Jun  2 12:39 pcmC0D0p
crw-rw----  1 root audio 116,  4 Jun  2 12:39 pcmC0D3p
crw-rw----  1 root audio 116,  5 Jun  2 12:39 pcmC0D7p
crw-rw----  1 root audio 116,  6 Jun  2 12:39 pcmC0D8p
crw-rw----  1 root audio 116, 11 Jun 30 14:45 pcmC1D0c
crw-rw----  1 root audio 116, 10 Jun 30 14:45 pcmC1D0p
crw-rw----  1 root audio 116,  1 Jun 11 06:39 seq
crw-rw----  1 root audio 116, 33 Jun 11 06:39 timer

### /proc/asound/cards
 0 [PCH            ]: HDA-Intel - HDA Intel PCH
                      HDA Intel PCH at 0xf1420000 irq 147
 1 [CODEC          ]: USB-Audio - USB Audio CODEC
                      Burr-Brown from TI USB Audio CODEC at usb-0000:00:14.0-4, full speed

## ALSA stabilization (2026-06-30T15:29:30+00:00)
### Installing prerequisite
Package: alsa-utils

### User and device permissions after audio group update
uid=1000(mike) gid=1000(mike) groups=1000(mike),4(adm),24(cdrom),27(sudo),29(audio),30(dip),46(plugdev),100(users),101(lxd),983(docker),982(ollama)
total 0
drwxr-xr-x  4 root root      340 Jun 30 14:45 .
drwxr-xr-x 20 root root     4380 Jun 30 14:45 ..
drwxr-xr-x  2 root root       60 Jun 30 14:45 by-id
drwxr-xr-x  2 root root      100 Jun 30 14:45 by-path
crw-rw----  1 root audio 116,  9 Jun  2 12:39 controlC0
crw-rw----  1 root audio 116, 12 Jun 30 14:45 controlC1
crw-rw----  1 root audio 116,  7 Jun  2 12:39 hwC0D0
crw-rw----  1 root audio 116,  8 Jun  2 12:39 hwC0D2
crw-rw----  1 root audio 116,  3 Jun  2 12:39 pcmC0D0c
crw-rw----  1 root audio 116,  2 Jun  2 12:39 pcmC0D0p
crw-rw----  1 root audio 116,  4 Jun  2 12:39 pcmC0D3p
crw-rw----  1 root audio 116,  5 Jun  2 12:39 pcmC0D7p
crw-rw----  1 root audio 116,  6 Jun  2 12:39 pcmC0D8p
crw-rw----  1 root audio 116, 11 Jun 30 14:45 pcmC1D0c
crw-rw----  1 root audio 116, 10 Jun 30 14:45 pcmC1D0p
crw-rw----  1 root audio 116,  1 Jun 11 06:39 seq
crw-rw----  1 root audio 116, 33 Jun 11 06:39 timer

### ALSA cards before /etc/asound.conf
**** List of PLAYBACK Hardware Devices ****
card 0: PCH [HDA Intel PCH], device 0: CX20753/4 Analog [CX20753/4 Analog]
  Subdevices: 1/1
  Subdevice #0: subdevice #0
card 0: PCH [HDA Intel PCH], device 3: HDMI 0 [HDMI 0]
  Subdevices: 1/1
  Subdevice #0: subdevice #0
card 0: PCH [HDA Intel PCH], device 7: HDMI 1 [HDMI 1]
  Subdevices: 1/1
  Subdevice #0: subdevice #0
card 0: PCH [HDA Intel PCH], device 8: HDMI 2 [HDMI 2]
  Subdevices: 1/1
  Subdevice #0: subdevice #0
card 1: CODEC [USB Audio CODEC], device 0: USB Audio [USB Audio]
  Subdevices: 1/1
  Subdevice #0: subdevice #0

### ALSA logical devices before /etc/asound.conf
null
    Discard all samples (playback) or generate zero samples (capture)
hw:CARD=PCH,DEV=0
    HDA Intel PCH, CX20753/4 Analog
    Direct hardware device without any conversions
hw:CARD=PCH,DEV=3
    HDA Intel PCH, HDMI 0
    Direct hardware device without any conversions
hw:CARD=PCH,DEV=7
    HDA Intel PCH, HDMI 1
    Direct hardware device without any conversions
hw:CARD=PCH,DEV=8
    HDA Intel PCH, HDMI 2
    Direct hardware device without any conversions
plughw:CARD=PCH,DEV=0
    HDA Intel PCH, CX20753/4 Analog
    Hardware device with all software conversions
plughw:CARD=PCH,DEV=3
    HDA Intel PCH, HDMI 0
    Hardware device with all software conversions
plughw:CARD=PCH,DEV=7
    HDA Intel PCH, HDMI 1
    Hardware device with all software conversions
plughw:CARD=PCH,DEV=8
    HDA Intel PCH, HDMI 2
    Hardware device with all software conversions
default:CARD=PCH
    HDA Intel PCH, CX20753/4 Analog
    Default Audio Device
sysdefault:CARD=PCH
    HDA Intel PCH, CX20753/4 Analog
    Default Audio Device
front:CARD=PCH,DEV=0
    HDA Intel PCH, CX20753/4 Analog
    Front output / input
surround21:CARD=PCH,DEV=0
    HDA Intel PCH, CX20753/4 Analog
    2.1 Surround output to Front and Subwoofer speakers
surround40:CARD=PCH,DEV=0
    HDA Intel PCH, CX20753/4 Analog
    4.0 Surround output to Front and Rear speakers
surround41:CARD=PCH,DEV=0
    HDA Intel PCH, CX20753/4 Analog
    4.1 Surround output to Front, Rear and Subwoofer speakers
surround50:CARD=PCH,DEV=0
    HDA Intel PCH, CX20753/4 Analog
    5.0 Surround output to Front, Center and Rear speakers
surround51:CARD=PCH,DEV=0
    HDA Intel PCH, CX20753/4 Analog
    5.1 Surround output to Front, Center, Rear and Subwoofer speakers
surround71:CARD=PCH,DEV=0
    HDA Intel PCH, CX20753/4 Analog
    7.1 Surround output to Front, Center, Side, Rear and Woofer speakers
hdmi:CARD=PCH,DEV=0
    HDA Intel PCH, HDMI 0
    HDMI Audio Output
hdmi:CARD=PCH,DEV=1
    HDA Intel PCH, HDMI 1
    HDMI Audio Output
hdmi:CARD=PCH,DEV=2
    HDA Intel PCH, HDMI 2
    HDMI Audio Output
dmix:CARD=PCH,DEV=0
    HDA Intel PCH, CX20753/4 Analog
    Direct sample mixing device
dmix:CARD=PCH,DEV=3
    HDA Intel PCH, HDMI 0
    Direct sample mixing device
dmix:CARD=PCH,DEV=7
    HDA Intel PCH, HDMI 1
    Direct sample mixing device
dmix:CARD=PCH,DEV=8
    HDA Intel PCH, HDMI 2
    Direct sample mixing device
hw:CARD=CODEC,DEV=0
    USB Audio CODEC, USB Audio
    Direct hardware device without any conversions
plughw:CARD=CODEC,DEV=0
    USB Audio CODEC, USB Audio
    Hardware device with all software conversions
default:CARD=CODEC
    USB Audio CODEC, USB Audio
    Default Audio Device
sysdefault:CARD=CODEC
    USB Audio CODEC, USB Audio
    Default Audio Device
front:CARD=CODEC,DEV=0
    USB Audio CODEC, USB Audio
    Front output / input
surround21:CARD=CODEC,DEV=0
    USB Audio CODEC, USB Audio
    2.1 Surround output to Front and Subwoofer speakers
surround40:CARD=CODEC,DEV=0
    USB Audio CODEC, USB Audio
    4.0 Surround output to Front and Rear speakers
surround41:CARD=CODEC,DEV=0
    USB Audio CODEC, USB Audio
    4.1 Surround output to Front, Rear and Subwoofer speakers
surround50:CARD=CODEC,DEV=0
    USB Audio CODEC, USB Audio
    5.0 Surround output to Front, Center and Rear speakers
surround51:CARD=CODEC,DEV=0
    USB Audio CODEC, USB Audio
    5.1 Surround output to Front, Center, Rear and Subwoofer speakers
surround71:CARD=CODEC,DEV=0
    USB Audio CODEC, USB Audio
    7.1 Surround output to Front, Center, Side, Rear and Woofer speakers
iec958:CARD=CODEC,DEV=0
    USB Audio CODEC, USB Audio
    IEC958 (S/PDIF) Digital Audio Output
dmix:CARD=CODEC,DEV=0
    USB Audio CODEC, USB Audio
    Direct sample mixing device
No existing /etc/asound.conf to back up

### /etc/asound.conf
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

### ALSA logical devices after /etc/asound.conf
null
    Discard all samples (playback) or generate zero samples (capture)
default
behringer_dmix
behringer
hw:CARD=PCH,DEV=0
    HDA Intel PCH, CX20753/4 Analog
    Direct hardware device without any conversions
hw:CARD=PCH,DEV=3
    HDA Intel PCH, HDMI 0
    Direct hardware device without any conversions
hw:CARD=PCH,DEV=7
    HDA Intel PCH, HDMI 1
    Direct hardware device without any conversions
hw:CARD=PCH,DEV=8
    HDA Intel PCH, HDMI 2
    Direct hardware device without any conversions
plughw:CARD=PCH,DEV=0
    HDA Intel PCH, CX20753/4 Analog
    Hardware device with all software conversions
plughw:CARD=PCH,DEV=3
    HDA Intel PCH, HDMI 0
    Hardware device with all software conversions
plughw:CARD=PCH,DEV=7
    HDA Intel PCH, HDMI 1
    Hardware device with all software conversions
plughw:CARD=PCH,DEV=8
    HDA Intel PCH, HDMI 2
    Hardware device with all software conversions
sysdefault:CARD=PCH
    HDA Intel PCH, CX20753/4 Analog
    Default Audio Device
front:CARD=PCH,DEV=0
    HDA Intel PCH, CX20753/4 Analog
    Front output / input
surround21:CARD=PCH,DEV=0
    HDA Intel PCH, CX20753/4 Analog
    2.1 Surround output to Front and Subwoofer speakers
surround40:CARD=PCH,DEV=0
    HDA Intel PCH, CX20753/4 Analog
    4.0 Surround output to Front and Rear speakers
surround41:CARD=PCH,DEV=0
    HDA Intel PCH, CX20753/4 Analog
    4.1 Surround output to Front, Rear and Subwoofer speakers
surround50:CARD=PCH,DEV=0
    HDA Intel PCH, CX20753/4 Analog
    5.0 Surround output to Front, Center and Rear speakers
surround51:CARD=PCH,DEV=0
    HDA Intel PCH, CX20753/4 Analog
    5.1 Surround output to Front, Center, Rear and Subwoofer speakers
surround71:CARD=PCH,DEV=0
    HDA Intel PCH, CX20753/4 Analog
    7.1 Surround output to Front, Center, Side, Rear and Woofer speakers
hdmi:CARD=PCH,DEV=0
    HDA Intel PCH, HDMI 0
    HDMI Audio Output
hdmi:CARD=PCH,DEV=1
    HDA Intel PCH, HDMI 1
    HDMI Audio Output
hdmi:CARD=PCH,DEV=2
    HDA Intel PCH, HDMI 2
    HDMI Audio Output
dmix:CARD=PCH,DEV=0
    HDA Intel PCH, CX20753/4 Analog
    Direct sample mixing device
dmix:CARD=PCH,DEV=3
    HDA Intel PCH, HDMI 0
    Direct sample mixing device
dmix:CARD=PCH,DEV=7
    HDA Intel PCH, HDMI 1
    Direct sample mixing device
dmix:CARD=PCH,DEV=8
    HDA Intel PCH, HDMI 2
    Direct sample mixing device
hw:CARD=CODEC,DEV=0
    USB Audio CODEC, USB Audio
    Direct hardware device without any conversions
plughw:CARD=CODEC,DEV=0
    USB Audio CODEC, USB Audio
    Hardware device with all software conversions
sysdefault:CARD=CODEC
    USB Audio CODEC, USB Audio
    Default Audio Device
front:CARD=CODEC,DEV=0
    USB Audio CODEC, USB Audio
    Front output / input
surround21:CARD=CODEC,DEV=0
    USB Audio CODEC, USB Audio
    2.1 Surround output to Front and Subwoofer speakers
surround40:CARD=CODEC,DEV=0
    USB Audio CODEC, USB Audio
    4.0 Surround output to Front and Rear speakers
surround41:CARD=CODEC,DEV=0
    USB Audio CODEC, USB Audio
    4.1 Surround output to Front, Rear and Subwoofer speakers
surround50:CARD=CODEC,DEV=0
    USB Audio CODEC, USB Audio
    5.0 Surround output to Front, Center and Rear speakers
surround51:CARD=CODEC,DEV=0
    USB Audio CODEC, USB Audio
    5.1 Surround output to Front, Center, Rear and Subwoofer speakers
surround71:CARD=CODEC,DEV=0
    USB Audio CODEC, USB Audio
    7.1 Surround output to Front, Center, Side, Rear and Woofer speakers
iec958:CARD=CODEC,DEV=0
    USB Audio CODEC, USB Audio
    IEC958 (S/PDIF) Digital Audio Output
dmix:CARD=CODEC,DEV=0
    USB Audio CODEC, USB Audio
    Direct sample mixing device

### ALSA validation as mike after new login
uid=1000(mike) gid=1000(mike) groups=1000(mike),4(adm),24(cdrom),27(sudo),29(audio),30(dip),46(plugdev),100(users),101(lxd),982(ollama),983(docker)
**** List of PLAYBACK Hardware Devices ****
card 0: PCH [HDA Intel PCH], device 0: CX20753/4 Analog [CX20753/4 Analog]
  Subdevices: 1/1
  Subdevice #0: subdevice #0
card 0: PCH [HDA Intel PCH], device 3: HDMI 0 [HDMI 0]
  Subdevices: 1/1
  Subdevice #0: subdevice #0
card 0: PCH [HDA Intel PCH], device 7: HDMI 1 [HDMI 1]
  Subdevices: 1/1
  Subdevice #0: subdevice #0
card 0: PCH [HDA Intel PCH], device 8: HDMI 2 [HDMI 2]
  Subdevices: 1/1
  Subdevice #0: subdevice #0
card 1: CODEC [USB Audio CODEC], device 0: USB Audio [USB Audio]
  Subdevices: 1/1
  Subdevice #0: subdevice #0

null
    Discard all samples (playback) or generate zero samples (capture)
default
behringer_dmix
behringer
hw:CARD=PCH,DEV=0
    HDA Intel PCH, CX20753/4 Analog
    Direct hardware device without any conversions
hw:CARD=PCH,DEV=3
    HDA Intel PCH, HDMI 0
    Direct hardware device without any conversions
hw:CARD=PCH,DEV=7
    HDA Intel PCH, HDMI 1
    Direct hardware device without any conversions
hw:CARD=PCH,DEV=8
    HDA Intel PCH, HDMI 2
    Direct hardware device without any conversions
plughw:CARD=PCH,DEV=0
    HDA Intel PCH, CX20753/4 Analog
    Hardware device with all software conversions
plughw:CARD=PCH,DEV=3
    HDA Intel PCH, HDMI 0
    Hardware device with all software conversions
plughw:CARD=PCH,DEV=7
    HDA Intel PCH, HDMI 1
    Hardware device with all software conversions
plughw:CARD=PCH,DEV=8
    HDA Intel PCH, HDMI 2
    Hardware device with all software conversions
sysdefault:CARD=PCH
    HDA Intel PCH, CX20753/4 Analog
    Default Audio Device
front:CARD=PCH,DEV=0
    HDA Intel PCH, CX20753/4 Analog
    Front output / input
surround21:CARD=PCH,DEV=0
    HDA Intel PCH, CX20753/4 Analog
    2.1 Surround output to Front and Subwoofer speakers
surround40:CARD=PCH,DEV=0
    HDA Intel PCH, CX20753/4 Analog

### ALSA speaker-test validation
behringer sine 44100: PASS command exit 0
default sine 44100: PASS command exit 0
Note: audible confirmation pending from user.

## Spotify Connect setup (2026-06-30T15:35:05+00:00)
### /etc/raspotify/conf
LIBRESPOT_NAME="Marantz-Lenovo"
BITRATE="320"
LIBRESPOT_BACKEND="alsa"
LIBRESPOT_DEVICE="behringer"

### raspotify enabled
enabled

### raspotify active
active

### raspotify status
● raspotify.service - Raspotify (Spotify Connect Client)
     Loaded: loaded (/usr/lib/systemd/system/raspotify.service; enabled; preset: enabled)
     Active: active (running) since Tue 2026-06-30 15:35:02 UTC; 3s ago
 Invocation: b088d0d10d7a41f6b1deb6749c2c8ef6
       Docs: https://github.com/dtcooper/raspotify
             https://github.com/librespot-org/librespot
             https://github.com/dtcooper/raspotify/wiki
             https://github.com/librespot-org/librespot/wiki/Options
   Main PID: 3808407 (librespot)
      Tasks: 11 (limit: 5932)
     Memory: 3.1M (peak: 3.8M)
        CPU: 49ms
     CGroup: /system.slice/raspotify.service
             └─3808407 /usr/bin/librespot

juin 30 15:35:02 48sab systemd[1]: Started raspotify.service - Raspotify (Spotify Connect Client).
juin 30 15:35:02 48sab librespot[3808407]: [2026-06-30T15:35:02Z INFO  librespot] librespot 0.8.0 ea813143 (Built on 2025-11-24, Build ID: nvonn6qo, Profile: release)
juin 30 15:35:02 48sab librespot[3808407]: [2026-06-30T15:35:02Z INFO  librespot_playback::mixer::softmixer] Mixing with softvol and volume control: Log(60.0)
juin 30 15:35:02 48sab librespot[3808407]: [2026-06-30T15:35:02Z INFO  librespot_playback::convert] Converting with ditherer: tpdf
juin 30 15:35:02 48sab librespot[3808407]: [2026-06-30T15:35:02Z INFO  librespot_playback::audio_backend::alsa] Using AlsaSink with format: S16
juin 30 15:35:03 48sab librespot[3808407]: [2026-06-30T15:35:03Z INFO  librespot_discovery] Published zeroconf service

### raspotify logs
juin 30 15:34:34 48sab systemd[1]: Started raspotify.service - Raspotify (Spotify Connect Client).
juin 30 15:35:02 48sab systemd[1]: Stopping raspotify.service - Raspotify (Spotify Connect Client)...
juin 30 15:35:02 48sab systemd[1]: raspotify.service: Deactivated successfully.
juin 30 15:35:02 48sab systemd[1]: Stopped raspotify.service - Raspotify (Spotify Connect Client).
juin 30 15:35:02 48sab systemd[1]: Started raspotify.service - Raspotify (Spotify Connect Client).
juin 30 15:35:02 48sab librespot[3808407]: [2026-06-30T15:35:02Z INFO  librespot] librespot 0.8.0 ea813143 (Built on 2025-11-24, Build ID: nvonn6qo, Profile: release)
juin 30 15:35:02 48sab librespot[3808407]: [2026-06-30T15:35:02Z INFO  librespot_playback::mixer::softmixer] Mixing with softvol and volume control: Log(60.0)
juin 30 15:35:02 48sab librespot[3808407]: [2026-06-30T15:35:02Z INFO  librespot_playback::convert] Converting with ditherer: tpdf
juin 30 15:35:02 48sab librespot[3808407]: [2026-06-30T15:35:02Z INFO  librespot_playback::audio_backend::alsa] Using AlsaSink with format: S16
juin 30 15:35:03 48sab librespot[3808407]: [2026-06-30T15:35:03Z INFO  librespot_discovery] Published zeroconf service

### Spotify user validation: YES

## DLNA renderer setup (2026-06-30T15:43:36+00:00)
### /etc/gmediarender/gmediarender.conf
UPNP_DEVICE_NAME="Marantz-Lenovo-DLNA"
ALSA_DEVICE="behringer"
INITIAL_VOLUME_DB=-10

### gmediarender enabled
enabled

### gmediarender active
active

### gmediarender status
● gmediarender.service - GMediaRender UPnP/DLNA renderer
     Loaded: loaded (/usr/lib/systemd/system/gmediarender.service; enabled; preset: enabled)
     Active: active (running) since Tue 2026-06-30 15:43:33 UTC; 3s ago
 Invocation: b0a2e87c31f049f59b7f7fbc96ea05d7
       Docs: man:gmediarender
   Main PID: 3811695 (gmediarender-wr)
      Tasks: 14 (limit: 5932)
     Memory: 5.4M (peak: 11.8M)
        CPU: 127ms
     CGroup: /system.slice/gmediarender.service
             ├─3811695 /bin/bash /usr/libexec/gmediarender/gmediarender-wrapper
             └─3811705 /usr/bin/gmediarender --logfile=stdout -f Marantz-Lenovo-DLNA -u 05f0550310a78fc70c3e9b5c0da596e8 --gstout-audiosink=alsasink --gstout-audiodevice=behringer --gstout-initial-volume-db=-10

juin 30 15:43:33 48sab gmediarender-wrapper[3811705]: <Mute val="0" channel="Master"></Mute>
juin 30 15:43:33 48sab gmediarender-wrapper[3811705]: <HorizontalKeystone val="0"></HorizontalKeystone>
juin 30 15:43:33 48sab gmediarender-wrapper[3811705]: <VolumeDB val="-2560" channel="Master"></VolumeDB>
juin 30 15:43:33 48sab gmediarender-wrapper[3811705]: <PresetNameList val=""></PresetNameList>
juin 30 15:43:33 48sab gmediarender-wrapper[3811705]: <Contrast val="0"></Contrast>
juin 30 15:43:33 48sab gmediarender-wrapper[3811705]: <Brightness val="0"></Brightness>
juin 30 15:43:33 48sab gmediarender-wrapper[3811705]: </InstanceID>
juin 30 15:43:33 48sab gmediarender-wrapper[3811705]: </Event>
juin 30 15:43:33 48sab gmediarender-wrapper[3811705]: INFO  [2026-06-30 15:43:33.377723 | main] Ready for rendering ('Marantz-Lenovo-DLNA'; uuid=05f0550310a78fc70c3e9b5c0da596e8).
juin 30 15:43:33 48sab gmediarender-wrapper[3811705]: Ready for rendering ('Marantz-Lenovo-DLNA'; uuid=05f0550310a78fc70c3e9b5c0da596e8).

### gmediarender logs
juin 30 15:43:33 48sab gmediarender-wrapper[3811705]: INFO  [2026-06-30 15:43:33.222031 | connmgr] Registering support for 'video/x-h261'
juin 30 15:43:33 48sab gmediarender-wrapper[3811705]: INFO  [2026-06-30 15:43:33.222033 | connmgr] Registering support for 'video/x-h263'
juin 30 15:43:33 48sab gmediarender-wrapper[3811705]: INFO  [2026-06-30 15:43:33.222035 | connmgr] Registering support for 'video/x-h264'
juin 30 15:43:33 48sab gmediarender-wrapper[3811705]: INFO  [2026-06-30 15:43:33.222037 | connmgr] Registering support for 'video/x-h265'
juin 30 15:43:33 48sab gmediarender-wrapper[3811705]: INFO  [2026-06-30 15:43:33.222039 | connmgr] Registering support for 'video/x-h266'
juin 30 15:43:33 48sab gmediarender-wrapper[3811705]: INFO  [2026-06-30 15:43:33.222041 | connmgr] Registering support for 'video/x-huffyuv'
juin 30 15:43:33 48sab gmediarender-wrapper[3811705]: INFO  [2026-06-30 15:43:33.222044 | connmgr] Registering support for 'video/x-jpeg'
juin 30 15:43:33 48sab gmediarender-wrapper[3811705]: INFO  [2026-06-30 15:43:33.222046 | connmgr] Registering support for 'video/x-matroska'
juin 30 15:43:33 48sab gmediarender-wrapper[3811705]: INFO  [2026-06-30 15:43:33.222048 | connmgr] Registering support for 'video/x-matroska-3d'
juin 30 15:43:33 48sab gmediarender-wrapper[3811705]: INFO  [2026-06-30 15:43:33.222050 | connmgr] Registering support for 'video/x-mp4-part'
juin 30 15:43:33 48sab gmediarender-wrapper[3811705]: INFO  [2026-06-30 15:43:33.222052 | connmgr] Registering support for 'video/x-msmpeg'
juin 30 15:43:33 48sab gmediarender-wrapper[3811705]: INFO  [2026-06-30 15:43:33.222054 | connmgr] Registering support for 'video/x-msvideo'
juin 30 15:43:33 48sab gmediarender-wrapper[3811705]: INFO  [2026-06-30 15:43:33.222056 | connmgr] Registering support for 'video/x-pn-realvideo'
juin 30 15:43:33 48sab gmediarender-wrapper[3811705]: INFO  [2026-06-30 15:43:33.222059 | connmgr] Registering support for 'video/x-prores'
juin 30 15:43:33 48sab gmediarender-wrapper[3811705]: INFO  [2026-06-30 15:43:33.222061 | connmgr] Registering support for 'video/x-pwc1'
juin 30 15:43:33 48sab gmediarender-wrapper[3811705]: INFO  [2026-06-30 15:43:33.222063 | connmgr] Registering support for 'video/x-pwc2'
juin 30 15:43:33 48sab gmediarender-wrapper[3811705]: INFO  [2026-06-30 15:43:33.222065 | connmgr] Registering support for 'video/x-qt-part'
juin 30 15:43:33 48sab gmediarender-wrapper[3811705]: INFO  [2026-06-30 15:43:33.222067 | connmgr] Registering support for 'video/x-raw'
juin 30 15:43:33 48sab gmediarender-wrapper[3811705]: INFO  [2026-06-30 15:43:33.222069 | connmgr] Registering support for 'video/x-smoke'
juin 30 15:43:33 48sab gmediarender-wrapper[3811705]: INFO  [2026-06-30 15:43:33.222071 | connmgr] Registering support for 'video/x-sonix'
juin 30 15:43:33 48sab gmediarender-wrapper[3811705]: INFO  [2026-06-30 15:43:33.222074 | connmgr] Registering support for 'video/x-svq'
juin 30 15:43:33 48sab gmediarender-wrapper[3811705]: INFO  [2026-06-30 15:43:33.222076 | connmgr] Registering support for 'video/x-theora'
juin 30 15:43:33 48sab gmediarender-wrapper[3811705]: INFO  [2026-06-30 15:43:33.222078 | connmgr] Registering support for 'video/x-unaligned-raw'
juin 30 15:43:33 48sab gmediarender-wrapper[3811705]: INFO  [2026-06-30 15:43:33.222080 | connmgr] Registering support for 'video/x-vp6'
juin 30 15:43:33 48sab gmediarender-wrapper[3811705]: INFO  [2026-06-30 15:43:33.222082 | connmgr] Registering support for 'video/x-vp6-alpha'
juin 30 15:43:33 48sab gmediarender-wrapper[3811705]: INFO  [2026-06-30 15:43:33.222084 | connmgr] Registering support for 'video/x-vp6-flash'
juin 30 15:43:33 48sab gmediarender-wrapper[3811705]: INFO  [2026-06-30 15:43:33.222086 | connmgr] Registering support for 'video/x-vp8'
juin 30 15:43:33 48sab gmediarender-wrapper[3811705]: INFO  [2026-06-30 15:43:33.222088 | connmgr] Registering support for 'video/x-vp9'
juin 30 15:43:33 48sab gmediarender-wrapper[3811705]: INFO  [2026-06-30 15:43:33.222090 | connmgr] Registering support for 'video/x-wmv'
juin 30 15:43:33 48sab gmediarender-wrapper[3811705]: INFO  [2026-06-30 15:43:33.222111 | webserver] Provide /upnp/grender-64x64.png (image/png) from /usr/share/gmediarender/grender-64x64.png
juin 30 15:43:33 48sab gmediarender-wrapper[3811705]: INFO  [2026-06-30 15:43:33.222134 | webserver] Provide /upnp/grender-128x128.png (image/png) from /usr/share/gmediarender/grender-128x128.png
juin 30 15:43:33 48sab gmediarender-wrapper[3811705]: INFO  [2026-06-30 15:43:33.222500 | webserver] Provide /upnp/rendertransportSCPD.xml (text/xml) from buffer
juin 30 15:43:33 48sab gmediarender-wrapper[3811705]: INFO  [2026-06-30 15:43:33.222592 | webserver] Provide /upnp/renderconnmgrSCPD.xml (text/xml) from buffer
juin 30 15:43:33 48sab gmediarender-wrapper[3811705]: INFO  [2026-06-30 15:43:33.222827 | webserver] Provide /upnp/rendercontrolSCPD.xml (text/xml) from buffer
juin 30 15:43:33 48sab gmediarender-wrapper[3811705]: INFO  [2026-06-30 15:43:33.274173 | upnp] Registered IPv4 <LAN_IP_ETH>:49494
juin 30 15:43:33 48sab gmediarender-wrapper[3811705]: INFO  [2026-06-30 15:43:33.274201 | upnp] Registered IPv6 <IPV6_LL>
juin 30 15:43:33 48sab gmediarender-wrapper[3811705]: INFO  [2026-06-30 15:43:33.281868 | webserver] Access /upnp/rendercontrolSCPD.xml (text/xml) len=13317
juin 30 15:43:33 48sab gmediarender-wrapper[3811705]: INFO  [2026-06-30 15:43:33.281887 | webserver] Access /upnp/rendercontrolSCPD.xml (text/xml) len=13317
juin 30 15:43:33 48sab gmediarender-wrapper[3811705]: INFO  [2026-06-30 15:43:33.288366 | webserver] Access /upnp/rendertransportSCPD.xml (text/xml) len=15697
juin 30 15:43:33 48sab gmediarender-wrapper[3811705]: INFO  [2026-06-30 15:43:33.288512 | webserver] Access /upnp/rendertransportSCPD.xml (text/xml) len=15697
juin 30 15:43:33 48sab gmediarender-wrapper[3811705]: INFO  [2026-06-30 15:43:33.376540 | upnp] Subscription request for urn:upnp-org:serviceId:AVTransport (uuid:05f0550310a78fc70c3e9b5c0da596e8)
juin 30 15:43:33 48sab gmediarender-wrapper[3811705]: INFO  [2026-06-30 15:43:33.376700 | upnp] Initial variable sync: <?xml version="1.0"?>
juin 30 15:43:33 48sab gmediarender-wrapper[3811705]: <Event xmlns="urn:schemas-upnp-org:metadata-1-0/AVT/">
juin 30 15:43:33 48sab gmediarender-wrapper[3811705]: <InstanceID val="0">
juin 30 15:43:33 48sab gmediarender-wrapper[3811705]: <TransportStatus val="OK"></TransportStatus>
juin 30 15:43:33 48sab gmediarender-wrapper[3811705]: <NextAVTransportURI val=""></NextAVTransportURI>
juin 30 15:43:33 48sab gmediarender-wrapper[3811705]: <NextAVTransportURIMetaData val=""></NextAVTransportURIMetaData>
juin 30 15:43:33 48sab gmediarender-wrapper[3811705]: <CurrentTrackMetaData val=""></CurrentTrackMetaData>
juin 30 15:43:33 48sab gmediarender-wrapper[3811705]: <RelativeCounterPosition val="2147483647"></RelativeCounterPosition>
juin 30 15:43:33 48sab gmediarender-wrapper[3811705]: <PlaybackStorageMedium val="UNKNOWN"></PlaybackStorageMedium>
juin 30 15:43:33 48sab gmediarender-wrapper[3811705]: <RelativeTimePosition val="0:00:00"></RelativeTimePosition>
juin 30 15:43:33 48sab gmediarender-wrapper[3811705]: <PossibleRecordStorageMedia val="NOT_IMPLEMENTED"></PossibleRecordStorageMedia>
juin 30 15:43:33 48sab gmediarender-wrapper[3811705]: <CurrentPlayMode val="NORMAL"></CurrentPlayMode>
juin 30 15:43:33 48sab gmediarender-wrapper[3811705]: <TransportPlaySpeed val="1"></TransportPlaySpeed>
juin 30 15:43:33 48sab gmediarender-wrapper[3811705]: <PossiblePlaybackStorageMedia val="NETWORK,UNKNOWN"></PossiblePlaybackStorageMedia>
juin 30 15:43:33 48sab gmediarender-wrapper[3811705]: <AbsoluteTimePosition val="NOT_IMPLEMENTED"></AbsoluteTimePosition>
juin 30 15:43:33 48sab gmediarender-wrapper[3811705]: <CurrentTrack val="0"></CurrentTrack>
juin 30 15:43:33 48sab gmediarender-wrapper[3811705]: <CurrentTrackURI val=""></CurrentTrackURI>
juin 30 15:43:33 48sab gmediarender-wrapper[3811705]: <CurrentTransportActions val="PLAY"></CurrentTransportActions>
juin 30 15:43:33 48sab gmediarender-wrapper[3811705]: <NumberOfTracks val="0"></NumberOfTracks>
juin 30 15:43:33 48sab gmediarender-wrapper[3811705]: <AVTransportURI val=""></AVTransportURI>
juin 30 15:43:33 48sab gmediarender-wrapper[3811705]: <AbsoluteCounterPosition val="2147483647"></AbsoluteCounterPosition>
juin 30 15:43:33 48sab gmediarender-wrapper[3811705]: <CurrentRecordQualityMode val="NOT_IMPLEMENTED"></CurrentRecordQualityMode>
juin 30 15:43:33 48sab gmediarender-wrapper[3811705]: <CurrentMediaDuration val=""></CurrentMediaDuration>
juin 30 15:43:33 48sab gmediarender-wrapper[3811705]: <AVTransportURIMetaData val=""></AVTransportURIMetaData>
juin 30 15:43:33 48sab gmediarender-wrapper[3811705]: <RecordStorageMedium val="NOT_IMPLEMENTED"></RecordStorageMedium>
juin 30 15:43:33 48sab gmediarender-wrapper[3811705]: <RecordMediumWriteStatus val="NOT_IMPLEMENTED"></RecordMediumWriteStatus>
juin 30 15:43:33 48sab gmediarender-wrapper[3811705]: <CurrentTrackDuration val="0:00:00"></CurrentTrackDuration>
juin 30 15:43:33 48sab gmediarender-wrapper[3811705]: <TransportState val="STOPPED"></TransportState>
juin 30 15:43:33 48sab gmediarender-wrapper[3811705]: <PossibleRecordQualityModes val="NOT_IMPLEMENTED"></PossibleRecordQualityModes>
juin 30 15:43:33 48sab gmediarender-wrapper[3811705]: </InstanceID>
juin 30 15:43:33 48sab gmediarender-wrapper[3811705]: </Event>
juin 30 15:43:33 48sab gmediarender-wrapper[3811705]: INFO  [2026-06-30 15:43:33.377380 | gstreamer] Query volume fraction: 0.316228
juin 30 15:43:33 48sab gmediarender-wrapper[3811705]: INFO  [2026-06-30 15:43:33.377429 | control] Output initial volume is 0.316228; setting control variables accordingly.
juin 30 15:43:33 48sab gmediarender-wrapper[3811705]: INFO  [2026-06-30 15:43:33.377416 | upnp] Subscription request for urn:upnp-org:serviceId:RenderingControl (uuid:05f0550310a78fc70c3e9b5c0da596e8)
juin 30 15:43:33 48sab gmediarender-wrapper[3811705]: INFO  [2026-06-30 15:43:33.377456 | control] Setting volume-db to -10.00db == #75
juin 30 15:43:33 48sab gmediarender-wrapper[3811705]: INFO  [2026-06-30 15:43:33.377580 | upnp] Initial variable sync: <?xml version="1.0"?>
juin 30 15:43:33 48sab gmediarender-wrapper[3811705]: <Event xmlns="urn:schemas-upnp-org:metadata-1-0/RCS/">
juin 30 15:43:33 48sab gmediarender-wrapper[3811705]: <InstanceID val="0">
juin 30 15:43:33 48sab gmediarender-wrapper[3811705]: <GreenVideoGain val="0"></GreenVideoGain>
juin 30 15:43:33 48sab gmediarender-wrapper[3811705]: <BlueVideoBlackLevel val="0"></BlueVideoBlackLevel>
juin 30 15:43:33 48sab gmediarender-wrapper[3811705]: <VerticalKeystone val="0"></VerticalKeystone>
juin 30 15:43:33 48sab gmediarender-wrapper[3811705]: <GreenVideoBlackLevel val="0"></GreenVideoBlackLevel>
juin 30 15:43:33 48sab gmediarender-wrapper[3811705]: <Volume val="75" channel="Master"></Volume>
juin 30 15:43:33 48sab gmediarender-wrapper[3811705]: <Loudness val="0" channel="Master"></Loudness>
juin 30 15:43:33 48sab gmediarender-wrapper[3811705]: <RedVideoGain val="0"></RedVideoGain>
juin 30 15:43:33 48sab gmediarender-wrapper[3811705]: <ColorTemperature val="0"></ColorTemperature>
juin 30 15:43:33 48sab gmediarender-wrapper[3811705]: <Sharpness val="0"></Sharpness>
juin 30 15:43:33 48sab gmediarender-wrapper[3811705]: <RedVideoBlackLevel val="0"></RedVideoBlackLevel>
juin 30 15:43:33 48sab gmediarender-wrapper[3811705]: <BlueVideoGain val="0"></BlueVideoGain>
juin 30 15:43:33 48sab gmediarender-wrapper[3811705]: <Mute val="0" channel="Master"></Mute>
juin 30 15:43:33 48sab gmediarender-wrapper[3811705]: <HorizontalKeystone val="0"></HorizontalKeystone>
juin 30 15:43:33 48sab gmediarender-wrapper[3811705]: <VolumeDB val="-2560" channel="Master"></VolumeDB>
juin 30 15:43:33 48sab gmediarender-wrapper[3811705]: <PresetNameList val=""></PresetNameList>
juin 30 15:43:33 48sab gmediarender-wrapper[3811705]: <Contrast val="0"></Contrast>
juin 30 15:43:33 48sab gmediarender-wrapper[3811705]: <Brightness val="0"></Brightness>
juin 30 15:43:33 48sab gmediarender-wrapper[3811705]: </InstanceID>
juin 30 15:43:33 48sab gmediarender-wrapper[3811705]: </Event>
juin 30 15:43:33 48sab gmediarender-wrapper[3811705]: INFO  [2026-06-30 15:43:33.377723 | main] Ready for rendering ('Marantz-Lenovo-DLNA'; uuid=05f0550310a78fc70c3e9b5c0da596e8).
juin 30 15:43:33 48sab gmediarender-wrapper[3811705]: Ready for rendering ('Marantz-Lenovo-DLNA'; uuid=05f0550310a78fc70c3e9b5c0da596e8).

### DS Audio user validation: YES

## Validation finale
### Services
enabled
active
enabled
active

### Audio
**** List of PLAYBACK Hardware Devices ****
card 0: PCH [HDA Intel PCH], device 0: CX20753/4 Analog [CX20753/4 Analog]
  Subdevices: 1/1
  Subdevice #0: subdevice #0
card 0: PCH [HDA Intel PCH], device 3: HDMI 0 [HDMI 0]
  Subdevices: 1/1
  Subdevice #0: subdevice #0
card 0: PCH [HDA Intel PCH], device 7: HDMI 1 [HDMI 1]
  Subdevices: 1/1
  Subdevice #0: subdevice #0
card 0: PCH [HDA Intel PCH], device 8: HDMI 2 [HDMI 2]
  Subdevices: 1/1
  Subdevice #0: subdevice #0
card 1: CODEC [USB Audio CODEC], device 0: USB Audio [USB Audio]
  Subdevices: 0/1
  Subdevice #0: subdevice #0

null
    Discard all samples (playback) or generate zero samples (capture)
default
behringer_dmix
behringer
hw:CARD=PCH,DEV=0
    HDA Intel PCH, CX20753/4 Analog
    Direct hardware device without any conversions
hw:CARD=PCH,DEV=3
    HDA Intel PCH, HDMI 0
    Direct hardware device without any conversions
hw:CARD=PCH,DEV=7
    HDA Intel PCH, HDMI 1
    Direct hardware device without any conversions
hw:CARD=PCH,DEV=8
    HDA Intel PCH, HDMI 2
    Direct hardware device without any conversions
plughw:CARD=PCH,DEV=0
    HDA Intel PCH, CX20753/4 Analog
    Hardware device with all software conversions
plughw:CARD=PCH,DEV=3
    HDA Intel PCH, HDMI 0
    Hardware device with all software conversions
plughw:CARD=PCH,DEV=7
    HDA Intel PCH, HDMI 1
    Hardware device with all software conversions
plughw:CARD=PCH,DEV=8
    HDA Intel PCH, HDMI 2
    Hardware device with all software conversions
sysdefault:CARD=PCH
    HDA Intel PCH, CX20753/4 Analog
    Default Audio Device
front:CARD=PCH,DEV=0
    HDA Intel PCH, CX20753/4 Analog
    Front output / input
surround21:CARD=PCH,DEV=0
    HDA Intel PCH, CX20753/4 Analog
    2.1 Surround output to Front and Subwoofer speakers
surround40:CARD=PCH,DEV=0
    HDA Intel PCH, CX20753/4 Analog
    4.0 Surround output to Front and Rear speakers
surround41:CARD=PCH,DEV=0
    HDA Intel PCH, CX20753/4 Analog
    4.1 Surround output to Front, Rear and Subwoofer speakers
surround50:CARD=PCH,DEV=0
    HDA Intel PCH, CX20753/4 Analog
    5.0 Surround output to Front, Center and Rear speakers
surround51:CARD=PCH,DEV=0
    HDA Intel PCH, CX20753/4 Analog
    5.1 Surround output to Front, Center, Rear and Subwoofer speakers
surround71:CARD=PCH,DEV=0
    HDA Intel PCH, CX20753/4 Analog
    7.1 Surround output to Front, Center, Side, Rear and Woofer speakers
hdmi:CARD=PCH,DEV=0
    HDA Intel PCH, HDMI 0
    HDMI Audio Output
hdmi:CARD=PCH,DEV=1
    HDA Intel PCH, HDMI 1
    HDMI Audio Output
hdmi:CARD=PCH,DEV=2
    HDA Intel PCH, HDMI 2
    HDMI Audio Output
dmix:CARD=PCH,DEV=0
    HDA Intel PCH, CX20753/4 Analog
    Direct sample mixing device
dmix:CARD=PCH,DEV=3
    HDA Intel PCH, HDMI 0
    Direct sample mixing device
dmix:CARD=PCH,DEV=7
    HDA Intel PCH, HDMI 1
    Direct sample mixing device
dmix:CARD=PCH,DEV=8
    HDA Intel PCH, HDMI 2
    Direct sample mixing device
hw:CARD=CODEC,DEV=0
    USB Audio CODEC, USB Audio
    Direct hardware device without any conversions
plughw:CARD=CODEC,DEV=0
    USB Audio CODEC, USB Audio
    Hardware device with all software conversions
sysdefault:CARD=CODEC
    USB Audio CODEC, USB Audio
    Default Audio Device
front:CARD=CODEC,DEV=0
    USB Audio CODEC, USB Audio
    Front output / input
surround21:CARD=CODEC,DEV=0
    USB Audio CODEC, USB Audio
    2.1 Surround output to Front and Subwoofer speakers
surround40:CARD=CODEC,DEV=0
    USB Audio CODEC, USB Audio
    4.0 Surround output to Front and Rear speakers
surround41:CARD=CODEC,DEV=0
    USB Audio CODEC, USB Audio
    4.1 Surround output to Front, Rear and Subwoofer speakers
surround50:CARD=CODEC,DEV=0
    USB Audio CODEC, USB Audio
    5.0 Surround output to Front, Center and Rear speakers
surround51:CARD=CODEC,DEV=0
    USB Audio CODEC, USB Audio
    5.1 Surround output to Front, Center, Rear and Subwoofer speakers
surround71:CARD=CODEC,DEV=0
    USB Audio CODEC, USB Audio
    7.1 Surround output to Front, Center, Side, Rear and Woofer speakers
iec958:CARD=CODEC,DEV=0
    USB Audio CODEC, USB Audio
    IEC958 (S/PDIF) Digital Audio Output
dmix:CARD=CODEC,DEV=0
    USB Audio CODEC, USB Audio
    Direct sample mixing device

### Home Assistant
HTTP/1.1 405 Method Not Allowed

### OpenClaw
HTTP/1.1 200 OK

### Ports audio reseau
