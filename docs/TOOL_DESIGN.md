# SpoonOS Tool Design Document

## Overview
This project uses two custom tools integrated with the SpoonOS SDK to provide high-frequency trading capabilities and market analysis.

## Tools

### 1. NeoWalletTool (`neo_wallet_tool`)
**Purpose**: Interfaces with the Neo N3 Blockchain.
**Capabilities**:
- `balance`: Query NEO/GAS balances.
- `transfer`: Execute on-chain assets transfers.
**Integration**: Uses `neo3-python` (mamba) for signing and RPC communication. Includes a `Mock` mode for safe demonstration without testnet funds.

### 2. MarketAnalyticsTool (`market_analytics`)
**Purpose**: Provides real-time (simulated) market data and sentiment analysis.
**Capabilities**:
- `sentiment`: aggregated social sentiment score.
- `quantitative`: price action and order book analysis.
**Logic**: Returns structured JSON data that the Agent uses to justify trading decisions.

## Agent Integration
The tools are registered via `ToolManager` in `main.py` and exposed to the `FlowChain` agent. The System Prompt instructs the agent to always cross-reference `market_analytics` before executing `neo_wallet_tool` commands.
