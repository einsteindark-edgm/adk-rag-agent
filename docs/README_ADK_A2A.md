# Colombian Import Specialist - Technical Documentation

This documentation set covers the implementation of a Colombian Import Specialist agent using Google ADK (Agent Development Kit) with Clean Architecture and the A2A (Agent-to-Agent) protocol.

## Agent Specialization

This agent is specifically designed to provide information about Colombian import procedures, using the `import_export` corpus with the `rules_imports` document containing official regulations.

## 📚 Documentation Files

### 1. [ADK_A2A_CLEAN_ARCHITECTURE_GUIDE.md](./ADK_A2A_CLEAN_ARCHITECTURE_GUIDE.md)
Complete guide for integrating ADK agents with Clean Architecture and A2A protocol. Includes:
- Architecture overview with diagrams
- Project structure
- Core components implementation
- Common errors and solutions
- Testing strategies

### 2. [ADK_A2A_QUICK_REFERENCE.md](./ADK_A2A_QUICK_REFERENCE.md)
Quick reference for developers already familiar with the concepts:
- Essential code snippets
- Critical points to remember
- Common fixes
- Debug commands

### 3. [MIGRATION_GUIDE_ADK_TO_A2A.md](./MIGRATION_GUIDE_ADK_TO_A2A.md)
Step-by-step guide for migrating existing ADK agents to use A2A protocol:
- Before/after comparisons
- Migration steps
- Testing the migration
- Rollback strategies

### 4. [TROUBLESHOOTING_A2A_ADK.md](./TROUBLESHOOTING_A2A_ADK.md)
Detailed troubleshooting guide based on real errors encountered:
- Actual error messages with solutions
- Debugging techniques
- Common patterns that cause issues
- Emergency fixes

### 5. [WORKING_EXAMPLE_ADK_A2A.md](./WORKING_EXAMPLE_ADK_A2A.md)
Complete working example with all code:
- Full project structure
- Working implementation of all components
- Example tools
- Test client
- Expected outputs

## 🚀 Getting Started

1. **New Project**: Start with [WORKING_EXAMPLE_ADK_A2A.md](./WORKING_EXAMPLE_ADK_A2A.md)
2. **Migration**: Use [MIGRATION_GUIDE_ADK_TO_A2A.md](./MIGRATION_GUIDE_ADK_TO_A2A.md)
3. **Having Issues**: Check [TROUBLESHOOTING_A2A_ADK.md](./TROUBLESHOOTING_A2A_ADK.md)
4. **Need Details**: Read [ADK_A2A_CLEAN_ARCHITECTURE_GUIDE.md](./ADK_A2A_CLEAN_ARCHITECTURE_GUIDE.md)
5. **Quick Lookup**: Use [ADK_A2A_QUICK_REFERENCE.md](./ADK_A2A_QUICK_REFERENCE.md)

## 🔑 Key Learnings

### Critical Points
1. **Package Name**: Use `a2a-sdk>=0.2.11`, not `a2a==0.1.0`
2. **Async/Sync**: ADK session methods are SYNC, TaskUpdater methods are ASYNC
3. **Response Format**: Extract from `result['artifacts'][0]['parts'][0]['text']`
4. **Client Creation**: Don't pass `httpx_client` to A2AClient constructor

### Architecture Benefits
- **Clean Architecture**: Separates concerns (domain, use cases, infrastructure)
- **A2A Protocol**: Standardized JSON-RPC communication
- **ADK Integration**: Leverages Google's agent framework
- **HTTP Interface**: Makes agents accessible via standard protocols

## 📝 Version Information

- **Google ADK**: 0.5.0
- **A2A SDK**: >=0.2.11
- **Python**: 3.11+
- **Documentation Date**: July 2025

## 🤝 Contributing

When updating these docs:
1. Test all code examples
2. Include actual error messages
3. Provide working solutions
4. Keep version information updated