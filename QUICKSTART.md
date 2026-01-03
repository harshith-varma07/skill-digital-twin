# Quick Start Guide - Docker Edition

Get the Skill Digital Twin up and running in 5 minutes! 🚀

## What You'll Need

- Docker Desktop installed ([Download here](https://www.docker.com/products/docker-desktop))
- OpenAI API Key ([Get one here](https://platform.openai.com/api-keys))
- YouTube API Key ([Get one here](https://console.cloud.google.com/apis/credentials))

## Step-by-Step Setup

### 1. Clone the Repository

```bash
git clone https://github.com/harshith-varma07/skill-digital-twin.git
cd skill-digital-twin
```

### 2. Set Up API Keys

Create a `.env` file from the example:

```bash
cp .env.example .env
```

Open `.env` in your favorite text editor and add your API keys:

```env
OPENAI_API_KEY=sk-your-actual-openai-key-here
YOUTUBE_API_KEY=your-actual-youtube-api-key-here
```

**Don't have API keys yet?** The app will still run, but AI features won't work.

### 3. Start the Application

```bash
docker compose up -d
```

Or if you have Make installed:

```bash
make up
```

**First time setup:** This will download and build everything. Grab a coffee! ☕ (5-10 minutes)

### 4. Watch It Start

```bash
docker compose logs -f
```

Or:

```bash
make logs
```

Press `Ctrl+C` to stop watching logs.

### 5. Open the Application

Once you see logs showing the services are ready:

- **Main App**: http://localhost
- **API Docs**: http://localhost:8000/docs
- **API**: http://localhost:8000

### 6. (Optional) Add Sample Data

```bash
docker compose exec backend python -m app.seed_data
```

Or:

```bash
make seed
```

## Verification Checklist

Use this checklist to verify everything is working:

- [ ] Can access frontend at http://localhost
- [ ] Can access API docs at http://localhost:8000/docs
- [ ] Can see the "Welcome to Skill Digital Twin API" message at http://localhost:8000
- [ ] All containers show "healthy" status: `docker compose ps`

## Common Issues and Fixes

### Port Already in Use

**Error**: "Port 80 is already allocated"

**Fix**: Stop the service using port 80 or change the port:

```bash
# In docker-compose.yml, change frontend ports to:
ports:
  - "8080:80"  # Use port 8080 instead

# Then access at http://localhost:8080
```

### Services Won't Start

**Fix**: Check Docker Desktop is running and has enough resources:

1. Open Docker Desktop
2. Go to Settings → Resources
3. Set Memory to at least 4GB
4. Click "Apply & Restart"

### Can't Access the Application

**Fix**: Wait a bit longer - services need time to initialize:

```bash
# Check if services are healthy
docker compose ps

# View logs for errors
docker compose logs backend
docker compose logs frontend
```

## Stopping the Application

```bash
docker compose down
```

Or:

```bash
make down
```

**To completely reset** (removes all data):

```bash
docker compose down -v
make clean
```

## Development Mode

Want to make changes to the code? Use development mode with hot-reload:

```bash
docker compose -f docker-compose.dev.yml up
```

Or:

```bash
make dev
```

Access at http://localhost:3000 (different port!)

## Next Steps

✅ **You're all set!** The application is running.

Now you can:

1. **Explore the UI** - Create an account and start profiling your skills
2. **Read the API Docs** - http://localhost:8000/docs
3. **Check out the full documentation** - See [README.md](README.md) and [DOCKER.md](DOCKER.md)
4. **Customize the setup** - Modify docker-compose.yml or create docker-compose.override.yml

## Useful Commands

```bash
# View logs
docker compose logs -f

# Restart services
docker compose restart

# Rebuild after code changes
docker compose up -d --build

# Access database
docker compose exec postgres psql -U postgres -d skill_digital_twin

# Stop everything
docker compose down
```

Or use the Makefile shortcuts:

```bash
make help    # See all available commands
make logs    # View logs
make restart # Restart services
make rebuild # Rebuild services
make db-shell # Access database
make down    # Stop everything
```

## Getting Help

- **Issues?** Check [DOCKER.md](DOCKER.md) for detailed troubleshooting
- **Questions?** Open an issue on GitHub
- **Documentation**: See [README.md](README.md) for full documentation

Happy learning! 🎓✨
