# Regulatory Compliance Engine - Architecture Diagram

## System Overview

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                           REGULATORY COMPLIANCE ENGINE                           │
│                              Desktop Application                                 │
└─────────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────────┐
│                                ELECTRON WRAPPER                                  │
│  ┌─────────────────────┐  ┌──────────────────┐  ┌─────────────────────────────┐ │
│  │   Main Process      │  │  Preload Script  │  │      Renderer Process      │ │
│  │   (main.cjs)        │  │   (preload.js)   │  │     (React Frontend)        │ │
│  │                     │  │                  │  │                             │ │
│  │ • Window Management │  │ • IPC Bridge     │  │ • User Interface            │ │
│  │ • App Lifecycle     │  │ • Security       │  │ • Test Execution UI         │ │
│  │ • Backend Launch    │  │ • API Access     │  │ • Real-time Results         │ │
│  └─────────────────────┘  └──────────────────┘  └─────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────────────┘
                                        │
                                        │ HTTP/WebSocket
                                        ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                             REACT FRONTEND LAYER                                │
│  ┌─────────────────────────────────────────────────────────────────────────────┐ │
│  │                              User Interface                                 │ │
│  │  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────────────────┐ │ │
│  │  │   Home Page     │  │ Test Execution  │  │        UI Components        │ │ │
│  │  │  (HomePage.jsx) │  │   Window        │  │                             │ │ │
│  │  │                 │  │(TestExecution   │  │ • LoadingSpinner.jsx        │ │ │
│  │  │ • Test Options  │  │  Window.jsx)    │  │ • Toast.jsx                 │ │ │
│  │  │ • URL Input     │  │                 │  │ • Status Indicators         │ │ │
│  │  │ • Start Tests   │  │ • Real-time     │  │                             │ │ │
│  │  └─────────────────┘  │   Progress      │  └─────────────────────────────┘ │ │
│  │                       │ • Test Results  │                                  │ │
│  │                       │ • Error Display │                                  │ │
│  │                       └─────────────────┘                                  │ │
│  └─────────────────────────────────────────────────────────────────────────────┘ │
│  ┌─────────────────────────────────────────────────────────────────────────────┐ │
│  │                           Business Logic Layer                             │ │
│  │  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────────────────┐ │ │
│  │  │     Hooks       │  │    Services     │  │        Constants            │ │ │
│  │  │                 │  │                 │  │                             │ │ │
│  │  │• useCompliance  │  │ • api.js        │  │ • testOptions.js            │ │ │
│  │  │  Test.js        │  │ • HTTP Client   │  │ • Test Type Definitions     │ │ │
│  │  │• State Mgmt     │  │ • Error Handle  │  │ • Configuration             │ │ │
│  │  │• Async Logic    │  │ • Response Map  │  │                             │ │ │
│  │  └─────────────────┘  └─────────────────┘  └─────────────────────────────┘ │ │
│  └─────────────────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────────────┘
                                        │
                                        │ REST API Calls
                                        ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                              FASTAPI BACKEND                                    │
│  ┌─────────────────────────────────────────────────────────────────────────────┐ │
│  │                              API Gateway                                    │ │
│  │  ┌─────────────────────────────────────────────────────────────────────────┐ │ │
│  │  │                           app.py (FastAPI)                             │ │ │
│  │  │                                                                         │ │ │
│  │  │ Endpoints:                      Middleware:                             │ │ │
│  │  │ • GET /                        • CORS Configuration                     │ │ │
│  │  │ • GET /test-types              • Request/Response Logging               │ │ │
│  │  │ • POST /run-test               • Error Handling                         │ │ │
│  │  │ • GET /test-results/{id}       • Authentication (Future)               │ │ │
│  │  └─────────────────────────────────────────────────────────────────────────┘ │ │
│  └─────────────────────────────────────────────────────────────────────────────┘ │
│                                        │                                        │
│                                        ▼                                        │
│  ┌─────────────────────────────────────────────────────────────────────────────┐ │
│  │                         MICROSERVICES ARCHITECTURE                          │ │
│  │                                                                             │ │
│  │  ┌─────────────────────────────────────────────────────────────────────────┐ │ │
│  │  │                     TestServiceFactory                                 │ │ │
│  │  │                                                                         │ │ │
│  │  │ • Service Registry & Router                                             │ │ │
│  │  │ • Request Validation & Routing                                          │ │ │
│  │  │ • Response Standardization                                              │ │ │
│  │  │ • Error Handling & Logging                                              │ │ │
│  │  └─────────────────────────────────────────────────────────────────────────┘ │ │
│  │                                        │                                   │ │
│  │                              Routes to appropriate service                 │ │
│  │                                        ▼                                   │ │
│  │  ┌───────────────────────────────────────────────────────────────────────┐  │ │
│  │  │                        COMPLIANCE TEST SERVICES                      │  │ │
│  │  │                                                                       │  │ │
│  │  │ ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────────────┐ │  │ │
│  │  │ │ Session Reminder│ │   Playcheck     │ │    Multiple Spin        │ │  │ │
│  │  │ │    Service      │ │   Service       │ │       Service           │ │  │ │
│  │  │ └─────────────────┘ └─────────────────┘ └─────────────────────────┘ │  │ │
│  │  │                                                                       │  │ │
│  │  │ ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────────────┐ │  │ │
│  │  │ │   Banking       │ │  Practice Play  │ │   Max Bet Limit         │ │  │ │
│  │  │ │   Service       │ │    Service      │ │     Service             │ │  │ │
│  │  │ └─────────────────┘ └─────────────────┘ └─────────────────────────┘ │  │ │
│  │  │                                                                       │  │ │
│  │  │ Each Service Implements:                                              │  │ │
│  │  │ • BaseTestService Interface                                           │  │ │
│  │  │ • execute_test() Method                                               │  │ │
│  │  │ • validate_request() Method                                           │  │ │
│  │  │ • Async Execution Support                                             │  │ │
│  │  │ • Detailed Response Generation                                        │  │ │
│  │  └───────────────────────────────────────────────────────────────────────┘  │ │
│  └─────────────────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────────────┘
                                        │
                                        ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                            AI/ML PROCESSING LAYER                               │
│  ┌─────────────────────────────────────────────────────────────────────────────┐ │
│  │                            Detection Models                                 │ │
│  │                                                                             │ │
│  │  Models Directory:                    AI Services:                         │ │
│  │  • best.pt (Primary Model)           • Computer Vision Detection           │ │
│  │  • best_all.pt (Comprehensive)       • UI Element Recognition             │ │
│  │  • best1.pt, best2.pt, best3.pt     • Compliance Validation               │ │
│  │  • classes.json (Label Mapping)      • Automated Testing Logic            │ │
│  │                                       • Screenshot Analysis                │ │
│  └─────────────────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────────────┘
                                        │
                                        ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                               EXTERNAL TARGETS                                  │
│  ┌─────────────────────────────────────────────────────────────────────────────┐ │
│  │                          Gaming Websites & Applications                     │ │
│  │                                                                             │ │
│  │ • Online Casino Platforms          • Mobile Gaming Apps                    │ │
│  │ • Slot Machine Interfaces          • Web-based Gaming Sites               │ │
│  │ • Banking/Payment Systems          • Regulatory Compliance Targets         │ │
│  │ • Session Management Systems       • User Interface Elements               │ │
│  └─────────────────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────────────┘
```

## Data Flow Diagram

```
User Input → React UI → API Service → Service Factory → Test Service → AI Models → Target Website
    ↑                                                                                    │
    └─── Test Results ← Response Formatting ← Test Execution ← Model Analysis ←────────┘
```

## Component Interactions

### 1. User Interaction Flow
```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│    User     │───▶│   React     │───▶│   Electron  │───▶│   FastAPI   │
│  Interface  │    │  Frontend   │    │   Process   │    │   Backend   │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
       ▲                                                         │
       │                                                         ▼
┌─────────────┐                                          ┌─────────────┐
│   Results   │◀─────────────────────────────────────────│  Compliance │
│   Display   │                                          │   Testing   │
└─────────────┘                                          └─────────────┘
```

### 2. Test Execution Pipeline
```
Test Request → Validation → Service Selection → AI Model → Website Interaction → Results
     │              │             │              │              │              │
     ▼              ▼             ▼              ▼              ▼              ▼
┌─────────┐  ┌─────────────┐ ┌──────────┐ ┌─────────────┐ ┌──────────┐ ┌─────────┐
│ API     │  │ Request     │ │ Service  │ │ Model       │ │ Browser  │ │Response │
│ Gateway │  │ Validation  │ │ Factory  │ │ Analysis    │ │ Control  │ │ Format  │
└─────────┘  └─────────────┘ └──────────┘ └─────────────┘ └──────────┘ └─────────┘
```

## Technology Stack

### Frontend Layer
- **Framework**: React 18.2.0
- **Build Tool**: Vite 5.0.0
- **Styling**: TailwindCSS 4.0.0
- **Icons**: Lucide React
- **HTTP Client**: Axios 1.6.0

### Desktop Wrapper
- **Runtime**: Electron 25.0.0
- **Process Communication**: IPC (Inter-Process Communication)
- **Security**: Context Isolation + Preload Scripts

### Backend Layer
- **Framework**: FastAPI (Python)
- **Architecture**: Microservices
- **Async Support**: Python asyncio
- **API Documentation**: OpenAPI/Swagger

### AI/ML Layer
- **Models**: PyTorch (.pt files)
- **Computer Vision**: Custom trained models
- **Detection**: UI element recognition
- **Analysis**: Compliance validation

## Security Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        Security Layers                          │
├─────────────────────────────────────────────────────────────────┤
│ 1. Electron Security                                            │
│    • Context Isolation Enabled                                 │
│    • Node Integration Disabled in Renderer                     │
│    • Preload Scripts for Safe API Access                       │
├─────────────────────────────────────────────────────────────────┤
│ 2. API Security                                                │
│    • CORS Configuration                                        │
│    • Request Validation (Pydantic)                            │
│    • Error Handling & Sanitization                            │
├─────────────────────────────────────────────────────────────────┤
│ 3. Network Security                                            │
│    • HTTPS Communication                                       │
│    • Input Sanitization                                       │
│    • Rate Limiting (Future)                                   │
└─────────────────────────────────────────────────────────────────┘
```

## Deployment Architecture

```
Development Mode:
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│    Vite     │    │   Electron  │    │   Python    │
│ Dev Server  │───▶│    Main     │───▶│   Backend   │
│ :5173       │    │   Process   │    │   :7000     │
└─────────────┘    └─────────────┘    └─────────────┘

Production Mode:
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   Built     │    │   Electron  │    │   Python    │
│ React App   │───▶│ Application │───▶│   Backend   │
│ (dist/)     │    │   Package   │    │ (embedded)  │
└─────────────┘    └─────────────┘    └─────────────┘
```

This architecture provides:
- **Modularity**: Clear separation of concerns
- **Scalability**: Microservices can be extended independently
- **Maintainability**: Unified codebase with clear structure
- **Security**: Multiple layers of protection
- **Performance**: Optimized build process and async operations
- **Extensibility**: Easy to add new test types and features
