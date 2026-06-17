# Platform-Specific Deployment Notes

## Windows Agent → Linux Server

### SSH Password Auth via SSH_ASKPASS

On Windows Git-Bash (MSYS2), `ssh` cannot open `/dev/tty` for interactive password input in non-interactive contexts.

```bash
# Create password script
cat > /d/workspace/ssh-pass.sh << 'EOF'
#!/bin/bash
echo 'YOUR_PASSWORD_HERE'
EOF
chmod +x /d/workspace/ssh-pass.sh

# Set environment for EVERY ssh call
export DISPLAY=:0
export SSH_ASKPASS=/d/workspace/ssh-pass.sh
export SSH_ASKPASS_REQUIRE=force

ssh -o StrictHostKeyChecking=no -p $PORT $USER@$HOST 'echo CONNECTED'
```

**Critical**: `DISPLAY=:0` required. `SSH_ASKPASS_REQUIRE=force` required on newer OpenSSH. Each terminal call needs the exports again.

**Transition to key auth**:
```bash
DISPLAY=:0 SSH_ASKPASS=/d/workspace/ssh-pass.sh SSH_ASKPASS_REQUIRE=force \
  ssh -o StrictHostKeyChecking=no -p $PORT $USER@$HOST \
  'mkdir -p ~/.ssh && chmod 700 ~/.ssh && echo "$(cat)" >> ~/.ssh/authorized_keys' \
  < ~/.ssh/id_ed25519.pub
```

### tar + SFTP Path Mapping

```bash
# In git-bash:
tar -czf /tmp/project.tar.gz packages/
cygpath -w /tmp/project.tar.gz
# → C:\Users\<user>\AppData\Local\Temp\project.tar.gz
```

Then in Python paramiko:
```python
sftp.put(r"C:\Users\...\project.tar.gz", '/tmp/project.tar.gz')
```

### CRLF Line Endings

Windows Git with `core.autocrlf=true` creates CRLF files that break on Linux.

**Fix**: `sed -i 's/\\r$//' file.tsx` or set `core.autocrlf=input` / add `.gitattributes`.

### curl + Inline JSON

Windows shells mangle JSON. Use file-based body:
```bash
echo '{"key":"value"}' > /tmp/payload.json
curl --data-binary @/tmp/payload.json http://host:3001/api/endpoint
```

### Paramiko Stability

Multiple SSH keys in `~/.ssh/` → paramiko may try wrong key first.
```python
ssh.connect(host, username=user, password=passwd,
            timeout=30, banner_timeout=30, auth_timeout=30,
            allow_agent=False, look_for_keys=False)
```

## Fresh ECS Deployment (Root Access)

```bash
# System update + basics
apt-get update -qq && apt-get install -y -qq curl wget git unzip ca-certificates gnupg

# Node.js 18
curl -fsSL https://deb.nodesource.com/setup_18.x | bash -
apt-get install -y -qq nodejs
npm install -g pnpm@8 pm2

# MySQL
apt-get install -y -qq mysql-server
systemctl start mysql && systemctl enable mysql
mysql -e "CREATE DATABASE myapp CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"

# nginx
apt-get install -y -qq nginx
systemctl start nginx && systemctl enable nginx
```

### nginx reverse proxy

```nginx
server {
    listen 80;
    location / {
        proxy_pass http://127.0.0.1:3101;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_read_timeout 300s;
    }
}
```

### PM2 startup

```bash
pm2 startup systemd
pm2 save
```
