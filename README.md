<a href="https://livekit.io/">
  <img src="./.github/assets/livekit-mark.png" alt="LiveKit logo" width="100" height="100">
</a>

# Dental Clinic Assistant - Voice AI Agent

A voice-enabled AI assistant for managing dental clinic appointments, built with [LiveKit Agents](https://github.com/livekit/agents) and [LiveKit Cloud](https://cloud.livekit.io/).

## Overview

This project is a conversational voice AI agent that helps patients book dental appointments at DentalBuddy clinic. The assistant handles the complete appointment booking workflow through natural conversation, collecting patient information, service preferences, and scheduling consultations.

## Features

- **Voice-First Interface**: Natural conversation over voice for appointment scheduling
- **Intelligent Conversation Flow**: 
  - Collects patient name and contact information
  - Gathers appointment type (service or consultation)
  - Handles doctor preference (male or female)
  - Validates appointment dates (no weekends/past dates)
  - Confirms availability and pricing
- **Calendar Integration**: Automatically creates calendar events for confirmed appointments
- **Real-Time Context Awareness**: Uses current date and time to prevent booking for past dates
- **Multiple AI Features**:
  - Background noise cancellation for clear audio
  - Turn detection for natural conversation flow
  - Large language model (Groq's Llama 3.1) for intelligent responses
  - Multiple voice provider support

## What It Does

The assistant provides information about:
- **Available Services**: Teeth scaling, whitening, braces, cavity filling, teeth replacement
- **Pricing**: Service costs and consultation charges
- **Doctor Availability**: Male and female dentists at the clinic
- **Clinic Hours**: Monday-Friday, 8:00 AM to 6:00 PM
- **Appointment Booking**: Full workflow to schedule and confirm appointments

## Project Structure

```
src/
├── agent.py              # Main agent implementation
└── __init__.py

tests/
└── test_agent.py         # Test suite

Dockerfile               # Production deployment configuration
pyproject.toml          # Project dependencies and configuration
```

The main agent code is in [src/agent.py](src/agent.py), which contains the DentalAssistant class with:
- LLM configuration (Groq Llama 3.1 8B)
- Detailed system instructions for appointment booking
- Tool definitions for calendar integration
- Conversation management

## Getting Started

### Prerequisites

- Python 3.10 or higher
- `uv` package manager ([installation guide](https://docs.astral.sh/uv/getting-started/installation/))
- LiveKit Cloud account (free tier available at [cloud.livekit.io](https://cloud.livekit.io/))

### Installation

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd my-voice-agent
   ```

2. **Install dependencies:**
   ```bash
   uv sync
   ```

3. **Set up environment variables:**
   ```bash
   cp .env.example .env.local
   ```
   Fill in the required LiveKit credentials:
   - `LIVEKIT_URL` - Your LiveKit server URL
   - `LIVEKIT_API_KEY` - API key for authentication
   - `LIVEKIT_API_SECRET` - API secret for authentication

   (Obtain these from your LiveKit Cloud dashboard or use the CLI: `lk cloud auth && lk app env --write --destination .env.local`)

## Running the Agent

### Interactive Console Mode
Start a direct conversation with the agent:

```bash
uv run python src/agent.py console
```

This launches an interactive terminal session where you can type messages and speak with the agent.

### Production Deployment
The Dockerfile is configured for deployment to LiveKit Cloud:

```bash
lk agent build . -image <image-name>
lk agent deploy -image <image-name>
```

## Development

### Code Formatting
Maintain code quality using Ruff:

```bash
# Format code
uv run ruff format

# Check for issues
uv run ruff check
```

### Testing
Run the test suite:

```bash
uv run pytest
```

Tests are located in the [tests/](tests/) directory.

## How It Works

### Conversation Flow

1. **Greeting**: The assistant introduces itself as DentalBuddy scheduling assistant
2. **Information Collection**: Gathers patient name and contact information
3. **Appointment Type**: Asks whether the patient needs a service or consultation
4. **Details**: 
   - For services: Asks which service is needed
   - For consultations: Asks for desired duration
5. **Doctor Preference**: Inquires if patient prefers a male or female dentist
6. **Date Selection**: Helps the patient select an available date/time
7. **Confirmation**: Displays appointment details and pricing
8. **Calendar Booking**: Automatically creates the appointment in the calendar

### Key Features

- **Validation**: Prevents booking for past dates or clinic closed days (weekends)
- **Real-Time Context**: Uses current date/time to validate appointment scheduling
- **Doctor Assignment**: Automatically assigns available doctors based on preference
- **Pricing**: Provides transparent pricing for all services and consultations
- **Error Handling**: Gracefully handles unclear inputs and re-prompts for clarification


## Technology Stack

- **Framework**: [LiveKit Agents SDK](https://github.com/livekit/agents) - Python SDK for building voice AI agents
- **LLM**: Groq's Llama 3.1 8B Instant model for intelligent conversation
- **Audio Processing**: 
  - Silero for voice activity detection
  - AI Coustics for noise cancellation
  - OpenAI for voice encoding/decoding
- **Integration**: Google Calendar API for appointment scheduling
- **Package Manager**: `uv` for fast, reliable Python dependency management

## Deployment

### Docker Deployment
Build and deploy with Docker:

```bash
docker build -t my-dental-assistant .
docker run -e LIVEKIT_URL=... -e LIVEKIT_API_KEY=... -e LIVEKIT_API_SECRET=... my-dental-assistant
```

### LiveKit Cloud
Deploy directly to LiveKit Cloud:

```bash
lk agent deploy
```

See [LiveKit Agents Deployment Documentation](https://docs.livekit.io/deploy/agents/) for more details.

## Documentation

For detailed information on extending and customizing this agent, refer to:
- [Agent Configuration Guide](AGENTS.md) - Project-specific configuration guidance
- [LiveKit Agents Documentation](https://docs.livekit.io/agents/)
- [LiveKit CLI Documentation](https://docs.livekit.io/intro/basics/cli/)

## Support & Resources

- **LiveKit Docs**: https://docs.livekit.io
- **GitHub Issues**: Report bugs or request features
- **LiveKit Community**: Join the [LiveKit Slack](https://livekit.io/join-slack) for community support


## Deploying to production

This project is production-ready and includes a working `Dockerfile`. To deploy it to LiveKit Cloud or another environment, see the [deploying to production](https://docs.livekit.io/deploy/agents/) guide.

## Self-hosted LiveKit

You can also self-host LiveKit instead of using LiveKit Cloud. See the [self-hosting](https://docs.livekit.io/transport/self-hosting/local/) guide for more information. If you choose to self-host, you'll need to also use [model plugins](https://docs.livekit.io/agents/models/#plugins) instead of LiveKit Inference and will need to remove the [LiveKit Cloud noise cancellation](https://docs.livekit.io/transport/media/noise-cancellation/) plugin.

