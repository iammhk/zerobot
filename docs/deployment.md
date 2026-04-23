# Deployment

## Docker

> [!TIP]
> The `-v ~/.zerobot:/home/zerobot/.zerobot` flag mounts your local config directory into the container, so your config and workspace persist across container restarts.
> The container runs as user `zerobot` (UID 1000). If you get **Permission denied**, fix ownership on the host first: `sudo chown -R 1000:1000 ~/.zerobot`, or pass `--user $(id -u):$(id -g)` to match your host UID. Podman users can use `--userns=keep-id` instead.

### Docker Compose

```bash
docker compose run --rm zerobot-cli onboard   # first-time setup
vim ~/.zerobot/config.json                     # add API keys
docker compose up -d zerobot-gateway           # start gateway
```

```bash
docker compose run --rm zerobot-cli agent -m "Hello!"   # run CLI
docker compose logs -f zerobot-gateway                   # view logs
docker compose down                                      # stop
```

### Docker

```bash
# Build the image
docker build -t zerobot .

# Initialize config (first time only)
docker run -v ~/.zerobot:/home/zerobot/.zerobot --rm zerobot onboard

# Edit config on host to add API keys
vim ~/.zerobot/config.json

# Run gateway (connects to enabled channels, e.g. Telegram/Discord/Mochat)
docker run -v ~/.zerobot:/home/zerobot/.zerobot -p 18790:18790 zerobot gateway

# Or run a single command
docker run -v ~/.zerobot:/home/zerobot/.zerobot --rm zerobot agent -m "Hello!"
docker run -v ~/.zerobot:/home/zerobot/.zerobot --rm zerobot status
```

## Linux Service

Run the gateway as a systemd user service so it starts automatically and restarts on failure.

**1. Find the zerobot binary path:**

```bash
which zerobot   # e.g. /home/user/.local/bin/zerobot
```

**2. Create the service file** at `~/.config/systemd/user/zerobot-gateway.service` (replace `ExecStart` path if needed):

```ini
[Unit]
Description=zerobot Gateway
After=network.target

[Service]
Type=simple
ExecStart=%h/.local/bin/zerobot gateway
Restart=always
RestartSec=10
NoNewPrivileges=yes
ProtectSystem=strict
ReadWritePaths=%h

[Install]
WantedBy=default.target
```

**3. Enable and start:**

```bash
systemctl --user daemon-reload
systemctl --user enable --now zerobot-gateway
```

**Common operations:**

```bash
systemctl --user status zerobot-gateway        # check status
systemctl --user restart zerobot-gateway       # restart after config changes
journalctl --user -u zerobot-gateway -f        # follow logs
```

If you edit the `.service` file itself, run `systemctl --user daemon-reload` before restarting.

> **Note:** User services only run while you are logged in. To keep the gateway running after logout, enable lingering:
>
> ```bash
> loginctl enable-linger $USER
> ```

