# nospoon

> Reference implementation of the Spoon codec.

Python CLI and library for the NoSpoon Messenger protocol. This is the original prototype — the Flutter app ([nospoon_app](https://github.com/KondrashovDenis/nospoon_app)) was built on top of this codec.

Use this repo to understand how the pipeline works, experiment with encoding, or integrate Spoon messages into your own tools.

## Pipeline

```
text → brainfuck → ttl wrapper → spoon prefix code → .bin → ipfs → relay
```

## Modules

- **`core/compiler.py`** — Text to Brainfuck compiler with optimal factorization
- **`core/interpreter.py`** — Brainfuck interpreter with safety limits
- **`core/transcoder.py`** — Spoon prefix code ↔ Brainfuck conversion
- **`core/ttl.py`** — TTL wrapper (time-based self-destruction via BF logic)
- **`core/codec.py`** — High-level encode/decode with password support
- **`transport/ipfs_client.py`** — Pinata v2 API client
- **`transport/relay_client.py`** — Cloudflare Workers relay client
- **`transport/messenger.py`** — Unified messenger interface
- **`cloudflare/worker.js`** — Cloudflare Worker source for the relay

## Install

```bash
pip install -r requirements.txt
```

## Usage

### Local encode/decode

```bash
python cli.py encode "Hello, spoon" 24h
python cli.py decode message.bin
```

### With password

```bash
python cli.py encode "secret" 1h mypassword
python cli.py decode message.bin mypassword
```

### Network (send/receive via relay)

```bash
python cli.py send "hello" abc123def456 24h
python cli.py inbox abc123def456
python cli.py stats
```

### TTL options

`1h` · `6h` · `24h` · `7d` (default: `24h`)

## Related

- [nospoon_app](https://github.com/KondrashovDenis/nospoon_app) — Flutter app (Android, Windows, macOS/iOS planned)
- [nospoon.ru](https://nospoon.ru) — landing page with live demo

## License

MIT

---

🥄 *there is no spoon.*
