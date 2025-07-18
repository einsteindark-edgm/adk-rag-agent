# Customer Communication Agent for Shipment Tracking

This repository contains a Google Agent Development Kit (ADK) implementation of an AI agent specialized in customer communication for shipment tracking and anomaly updates, exposed via the A2A (Agent-to-Agent) protocol.

## Overview

The Customer Communication Agent provides automated customer service for shipment tracking, including:

- Real-time shipment status updates
- Anomaly detection and communication
- ETA calculations and updates
- Professional customer messaging with appropriate tone
- Proactive delay notifications

## Architecture

### Component Diagram

```mermaid
graph TB
    subgraph "Client Layer"
        A2AC[A2A Client<br/>JSON-RPC]
        HTTPC[HTTP Client<br/>httpx]
    end
    
    subgraph "A2A Server Layer"
        A2AS[A2A Server<br/>Port 8006]
        UVIC[Uvicorn<br/>ASGI Server]
    end
    
    subgraph "Clean Architecture"
        subgraph "Infrastructure Layer"
            EXE[RAGAgentExecutor<br/>A2A Executor]
            AGENT[Customer Communication<br/>Agent]
            TOOLS[ADK Tools<br/>- check_shipment_status<br/>- get_anomaly_details<br/>- calculate_new_eta<br/>- generate_customer_message]
            CONFIG[Configuration<br/>- Settings<br/>- Environment]
        end
        
        subgraph "Domain Layer"
            ENT[Entities<br/>- Shipment<br/>- Anomaly<br/>- CustomerUpdate]
            EXC[Exceptions<br/>Domain Errors]
        end
    end
    
    subgraph "Google ADK Layer"
        RUNNER[ADK Runner<br/>Session Management]
        LLM[LLM Integration<br/>Gemini 2.0]
    end
    
    subgraph "External Services"
        DB[(Database<br/>Shipment Data)]
        API[External APIs<br/>Tracking Systems]
    end
    
    A2AC --> HTTPC
    HTTPC -.->|HTTP/JSON-RPC| A2AS
    A2AS --> UVIC
    UVIC --> EXE
    EXE --> RUNNER
    RUNNER --> AGENT
    AGENT --> TOOLS
    TOOLS --> DB
    TOOLS --> API
    TOOLS -.-> CONFIG
    TOOLS -.-> ENT
    
    style A2AC fill:#e1f5e1
    style A2AS fill:#e1e5f5
    style EXE fill:#f5e1e1
    style RUNNER fill:#f5f5e1
    style AGENT fill:#e5e1f5
```

### Sequence Diagram - Customer Query Processing

```mermaid
sequenceDiagram
    participant Customer as Customer
    participant Client as A2A Client
    participant Server as A2A Server
    participant Executor as RAGAgentExecutor
    participant Runner as ADK Runner
    participant Agent as Customer Agent
    participant Tools as Tools
    participant DB as Database

    Customer->>Client: "Where is my package ABC123?"
    Client->>Server: JSON-RPC Request<br/>{method: "message/send"}
    Server->>Executor: execute()<br/>(session_id, messages, context, updater)
    
    Note over Executor: Convert A2A message to ADK format
    
    Executor->>Runner: get_session(session_id)
    alt Session doesn't exist
        Executor->>Runner: create_session(session_id)
    end
    
    Executor->>Executor: await updater.submit()
    Executor->>Executor: await updater.start_work()
    
    Executor->>Runner: session.run_async(message)
    Runner->>Agent: Process customer query
    
    Agent->>Tools: check_shipment_status("ABC123")
    Tools->>DB: Query shipment data
    DB-->>Tools: Shipment details
    Tools-->>Agent: Status: In transit, Location: Miami
    
    Agent->>Tools: get_anomaly_details("ABC123")
    Tools->>DB: Query anomalies
    DB-->>Tools: Anomaly: Weather delay
    Tools-->>Agent: 2-hour delay due to weather
    
    Agent->>Tools: calculate_new_eta(shipment, anomaly)
    Tools-->>Agent: New ETA: Tomorrow 3:00 PM
    
    Agent->>Tools: generate_customer_message(context)
    Tools-->>Agent: Formatted message with apologetic tone
    
    Agent-->>Runner: Final response
    Runner-->>Executor: Event Stream with response
    Executor->>Executor: await updater.add_artifact(parts)
    Executor->>Executor: await updater.complete()
    
    Executor-->>Server: Task Completed
    Server-->>Client: JSON-RPC Response
    Client-->>Customer: "Your package ABC123 is currently in Miami..."
```

### Sequence Diagram - Proactive Anomaly Notification

```mermaid
sequenceDiagram
    participant System as Monitoring System
    participant Server as A2A Server
    participant Agent as Customer Agent
    participant Tools as Tools
    participant DB as Database
    participant Notif as Notification Service

    System->>Server: Anomaly detected for shipment XYZ789
    Server->>Agent: Process anomaly event
    
    Agent->>Tools: get_anomaly_details("XYZ789")
    Tools->>DB: Query anomaly data
    DB-->>Tools: Severe traffic delay (4+ hours)
    Tools-->>Agent: Anomaly details
    
    Agent->>Tools: check_shipment_status("XYZ789")
    Tools->>DB: Query shipment
    DB-->>Tools: High-value, time-sensitive
    Tools-->>Agent: Shipment profile
    
    Agent->>Tools: calculate_new_eta(shipment, anomaly)
    Tools-->>Agent: Delay: 5 hours, New ETA: 11:00 PM
    
    Note over Agent: Determine tone: Urgent + Apologetic<br/>Offer compensation (delay > 4 hours)
    
    Agent->>Tools: generate_customer_message({<br/>  tone: ["urgent", "apologetic"],<br/>  offer_compensation: true<br/>})
    Tools-->>Agent: Formatted urgent notification
    
    Agent->>Notif: Send notification to customer
    Notif-->>Agent: Notification sent
    
    Agent->>DB: Log customer communication
```

## Features

### Core Capabilities

1. **Shipment Status Tracking**
   - Real-time location updates
   - Current ETA information
   - Delivery progress tracking

2. **Anomaly Management**
   - Weather delays
   - Traffic conditions
   - Customs issues
   - Technical problems

3. **Customer Communication**
   - Tone-appropriate messaging
   - Multi-language support (if configured)
   - Proactive notifications
   - Complaint handling

4. **ETA Calculations**
   - Dynamic recalculation based on conditions
   - Consideration of multiple factors
   - Realistic time estimates

## Project Structure

```
agent-customer-tracking/
├── app/                        # Main application code
│   ├── domain/                 # Domain layer
│   │   └── entities/          # Business entities
│   │       ├── shipment.py    # Shipment model
│   │       ├── anomaly.py     # Anomaly model
│   │       └── customer_update.py  # Customer update model
│   ├── infrastructure/         # Infrastructure layer
│   │   ├── agent.py           # ADK agent definition
│   │   ├── tools/             # ADK tools implementation
│   │   │   ├── check_shipment_status.py
│   │   │   ├── get_anomaly_details.py
│   │   │   ├── calculate_new_eta.py
│   │   │   └── generate_customer_message.py
│   │   ├── web/               # A2A executor
│   │   ├── a2a/               # A2A card configuration
│   │   └── config/            # Configuration files
│   └── main/                  # Entry points
│       └── a2a_main.py        # A2A server
├── a2a_client.py              # A2A client for testing
├── requirements.txt           # Python dependencies
├── CLAUDE.md                  # AI assistant instructions
└── .env.example              # Environment variables template
```

## Prerequisites

- Python 3.9+
- Google Cloud account with billing enabled
- Google Cloud project with Vertex AI API enabled
- Access to create and manage Vertex AI resources

## Installation

1. **Clone the repository**:
   ```bash
   git clone git@github.com:AI-NextWorld/agent-customer.git
   cd agent-customer-tracking
   ```

2. **Set up virtual environment**:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment**:
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. **Set up Google Cloud authentication**:
   ```bash
   gcloud auth application-default login
   gcloud services enable aiplatform.googleapis.com
   ```

## Configuration

Create a `.env` file with the following variables:

```env
# Google Cloud Configuration
GOOGLE_CLOUD_PROJECT=your-project-id
GOOGLE_CLOUD_LOCATION=us-central1

# A2A Server Configuration
A2A_HOST=0.0.0.0
A2A_PORT=8006

# Agent Configuration
AGENT_MODEL=gemini-2.0-flash-exp

# Optional: Database Configuration
DATABASE_URL=postgresql://user:pass@localhost/shipments
```

## Running the Agent

### Start the A2A Server

```bash
python __main__.py
```

The server will start on `http://localhost:8006`

### Using the A2A Client

```bash
# Interactive mode
python a2a_client.py

# Test mode with predefined queries
python a2a_client.py --test
```

### Example Queries

```python
# Check shipment status
"Where is my package ABC123?"

# Ask about delays
"Why is my shipment XYZ789 delayed?"

# Request ETA update
"When will my order DEF456 arrive?"

# Express concern
"My package GHI789 was supposed to arrive yesterday!"
```

## Agent Communication Tones

The agent adapts its communication tone based on the situation:

- **Professional**: Standard updates and inquiries
- **Apologetic**: Delays over 2 hours or customer frustration
- **Urgent**: Critical delays for time-sensitive shipments
- **Reassuring**: Anxious customers or first-time users
- **Formal**: High-value shipments or business customers

## Tools Documentation

### check_shipment_status
Retrieves current shipment information including location, status, and original ETA.

### get_anomaly_details
Fetches details about any anomalies affecting the shipment (delays, issues, etc.).

### calculate_new_eta
Calculates updated delivery time based on current conditions and anomalies.

### generate_customer_message
Creates appropriately toned messages for customer communication.

## Development

### Adding New Tools

1. Create a new tool in `app/infrastructure/tools/`
2. Follow the ADK tool pattern with ToolContext
3. Import and add to agent tools list in `app/infrastructure/agent.py`
4. Update agent instructions if needed

### Testing

```bash
# Run unit tests
python -m pytest tests/

# Run integration tests
python -m pytest tests/integration/

# Test with mock data
python a2a_client.py --test
```

## Troubleshooting

### Common Issues

1. **Authentication errors**:
   ```bash
   gcloud auth application-default login
   ```

2. **API not enabled**:
   ```bash
   gcloud services enable aiplatform.googleapis.com
   ```

3. **Port already in use**:
   - Change A2A_PORT in .env file
   - Or kill the process using the port

4. **Database connection issues**:
   - Verify DATABASE_URL in .env
   - Ensure database is running

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the Apache License 2.0 - see the LICENSE file for details.

## Support

For issues and questions:
- Check the [CLAUDE.md](CLAUDE.md) file for development guidance
- Open an issue on GitHub
- Contact the development team

## Acknowledgments

- Google Agent Development Kit (ADK) team
- Google Vertex AI team
- A2A protocol contributors