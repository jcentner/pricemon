# Deployment

Podman is optional. Use it when you want `pricemon` running continuously on a VPS with restart-on-failure behavior.

## Runtime Files

These files are local and must not be committed:

- `.env`: Telegram secrets and runtime overrides.
- `config.toml`: feed and rule config.
- `data/`: SQLite state.

Minimum `.env`:

```text
TELEGRAM_BOT_TOKEN=<bot-token>
TELEGRAM_CHAT_ID=<chat-id>
PRICEMON_CONFIG=config.toml
PRICEMON_DB=data/pricemon.db
```

To find a Telegram chat ID, send any message to the bot, then query `getUpdates` with the bot token. Do not paste the token into logs or commits.

## Podman Smoke Test

```bash
podman build -t pricemon:latest .
podman run --rm \
  --env-file .env \
  -v "$PWD/config.toml:/app/config.toml:ro" \
  -v "$PWD/data:/app/data" \
  localhost/pricemon:latest pricemon --dry-run
```

Expected output shape:

```text
fetched=25 marked_seen=0 matched=0 sent=0
```

Test Telegram delivery before enabling the daemon:

```bash
podman run --rm \
  --env-file .env \
  -v "$PWD/config.toml:/app/config.toml:ro" \
  -v "$PWD/data:/app/data" \
  localhost/pricemon:latest pricemon --send-test
```

## User Systemd Service

Create `~/.config/systemd/user/pricemon.service`:

```ini
[Unit]
Description=Pricemon RSS monitor
After=network-online.target
Wants=network-online.target

[Service]
Restart=always
RestartSec=30
ExecStartPre=-/usr/bin/podman rm -f pricemon
ExecStart=/usr/bin/podman run --name pricemon --env-file %h/pricemon/.env -v %h/pricemon/config.toml:/app/config.toml:ro -v %h/pricemon/data:/app/data localhost/pricemon:latest
ExecStop=/usr/bin/podman stop -t 10 pricemon

[Install]
WantedBy=default.target
```

Enable and start:

```bash
loginctl enable-linger "$USER"
systemctl --user daemon-reload
systemctl --user enable --now pricemon.service
```

Operate:

```bash
systemctl --user status pricemon.service
journalctl --user -u pricemon.service -f
systemctl --user restart pricemon.service
```

## Update

```bash
cd ~/pricemon
git pull --ff-only
podman build -t pricemon:latest .
systemctl --user restart pricemon.service
```