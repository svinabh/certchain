# CertChain — Deployment Guide (Poora A to Z)

> Chain deploy karna matlab 3 cheezein: **genesis file** (chain ka janm) +
> **nodes chalana** (servers pe) + **peers jodna** (network banana).
> Ye guide Level 1 (testnet) se Level 4 (mainnet) tak sab cover karti hai.

---

## 1. Deploy karne pe kya-kya chalta hai?

Blockchain deploy = normal website deploy se ALAG. Ye cheezein deploy hoti hain:

| Component | Kya hai | Kitne chahiye |
|---|---|---|
| **Genesis file** | Chain ka "birth certificate" — initial balances, validator list, rules | 1 (sab nodes me same) |
| **Validator node** | Blocks banata hai (PoS me) | 5+ mainnet, 1 testnet ke liye kaafi |
| **Full/RPC node** | Chain ki poori copy + API deta hai | 2+ (redundancy) |
| **Explorer** | Blocks/tx browse karne ki website | 1 |
| **Faucet** | Free test coins deta hai | 1 |
| **Sequencer** (L2 route me) | Transactions order karta hai | 1 (HA baad me) |

**Genesis file baad me kabhi change nahi hoti** — supply, initial validators, rules yahi fix hote hain.

---

## 2. Kahan deploy karein? (Infra options)

### FREE options (testnet/demo ke liye)

| Option | Free kya milta hai | Catch |
|---|---|---|
| **Oracle Cloud Always Free** ⭐ | 4 ARM cores + 24GB RAM + 200GB storage, **lifetime free** | Signup me credit card mangte hain; capacity India region me turant na mile |
| **Apna laptop + Cloudflare Tunnel** 🇮🇳 | Public URL bina server, ₹0 | Laptop band = node band (demo ke liye perfect) |
| **AWS/GCP free tier** | 12 mahine chhota VM | Nodes ke liye bohot chhota hai |
| **Sepolia testnet (L1)** | L2 rollup deploy karne ke liye free test ETH | L1 ka part hai, chain nahi |

⚠️ **Honest baat:** Render/Railway/HF Spaces type free hosts nodes ke liye **kaam nahi karte** — wo idle pe so jaate hain aur node ki 24/7 uptime + storage persistence tootti hai. Node = sirf **Oracle free VM** ya **apna laptop + tunnel**.

### PAID options (mainnet-grade, Level 3-4 me)

| Option | Cost/node | Note |
|---|---|---|
| **Hetzner** (EU) | ~€15-40/month | Sabse sasta serious infra |
| **Contabo** | ~$10-25/month | Budget VPS |
| **DigitalOcean Mumbai** 🇮🇳 | $40-80/month | India latency, mehenga |
| **AWS Mumbai** | $80+/month | Enterprise-grade |

**Validator node ka minimum spec:** 4 cores, 16GB RAM, 500GB NVMe SSD, stable internet.
**India users ke liye RPC node Mumbai me rakhna** — latency aadhi.

---

## 3. Free Deployment Path (aaj hi kar sakte ho, ₹0)

> ⚠️ **macOS gotcha (diagnosed 2026-11-17):** browser me `localhost:5000` kholo to
> **403 "Access denied"** milega — kyunki macOS ka **AirPlay Receiver (Control Center)
> port 5000** pe baitha hota hai. Isliye hamari chain **port 8000+** use karti hai:
> `run_node --port 8000`. (Permanent fix chahiye to: System Settings → General →
> AirDrop & Handoff → AirPlay Receiver OFF.)

### Tareeka A: Laptop + Cloudflare Tunnel (sabse fast public demo)

```bash
# 1. Apni mini-chain ke 3 nodes chalao localhost pe (port 8000+ — macOS pe 5000 AirPlay ka hai)
.venv/bin/python -m certchain.run_node --port 8000
.venv/bin/python -m certchain.run_node --port 8001 --peers localhost:8000
.venv/bin/python -m certchain.run_node --port 8002 --peers localhost:8000

# 2. Node 1 ko public banao (₹0, account bhi nahi chahiye)
cloudflared tunnel --url http://localhost:5000
# → milta hai: https://random-name.trycloudflare.com

# 3. Ye URL do kisi ko → wo bhi tumhare node se connect ho sakta hai!
```

- ngrok bhi chalega (`ngrok http 5000`) — free me 1 tunnel
- **Demo ready:** friends ke phones se verify page khulega 🎉

### Tareeka B: Oracle Free VM pe permanent testnet node

```
1. cloud.oracle.com → signup (credit card verification, kuch charge nahi)
2. "Always Free" ARM instance: 4 OCPU, 24GB RAM, Ubuntu
3. Firewall: 26656 (P2P), 26657 (RPC), 443 (API) ports kholo
4. Node binary + genesis file daalo, systemd service banao:

   [Unit]
   Description=CertChain Node
   [Service]
   ExecStart=/usr/bin/certchaind start
   Restart=always
   User=chain

   # → laptop band bhi ho, node 24/7 chalega
5. UptimeRobot (free) se monitoring: node girа to email alert
```

---

## 4. Real Chain Deployment (framework-wise steps)

### Path 1: Cosmos SDK app-chain (sabse documented process)

```bash
# Build
git clone <tumhara-chain> && cd certchain && make install

# Genesis banao
certchaind init node1 --chain-id certchain-1
certchaind keys add validator
certchaind add-genesis-account $(certchaind keys show validator -a) 1000000000stake
certchaind gentx validator 1000000stake --chain-id certchain-1
certchaind collect-gentxs

# Start (5 validators ke gentx share karke collect-gentxs = fair genesis)
certchaind start
```

- Doosre validators: apne-apne `gentx` bhejte hain → ek shared genesis banata hai
- Peers: `config.toml` me `persistent_peers = "node_id@ip:26656,..."`

### Path 2: OP Stack L2 (EVM route)

```
1. L1 (Sepolia) pe rollup contracts deploy (foundry script se)
2. 4 processes chalao: op-geth (execution) + op-node (consensus)
   + op-batcher (L1 pe data bhejta) + op-proposer (L1 pe proofs)
3. RPC endpoint public karo (users MetaMask se connect karenge)
4. Chahiye: L1 testnet ETH (batcher ka gas) — faucet se free
```

### Docker pattern (3 nodes ek server pe ya alag servers pe)

```yaml
# docker-compose.yml
services:
  node1:
    build: .
    environment: [CHAIN_ID=certchain-1, PEERS=node2:8001,node3:8002]
    ports: ["8000:8000"]
    volumes: ["chain1-data:/data"]
  node2:
    build: .
    environment: [CHAIN_ID=certchain-1, PEERS=node1:8000,node3:8002]
    ports: ["8001:8000"]
    volumes: ["chain2-data:/data"]
  node3:
    build: .
    environment: [CHAIN_ID=certchain-1, PEERS=node1:8000,node2:8001]
    ports: ["8002:8000"]
    volumes: ["chain3-data:/data"]
volumes: { chain1-data: {}, chain2-data: {}, chain3-data: {} }
```

---

## 5. Ops Checklist (deploy ke BAAD wala kaam)

| Kaam | Tool (free) | Kyun zaroori |
|---|---|---|
| Uptime alerts | UptimeRobot | Node gire to turant pata chale |
| Metrics dashboard | Prometheus + Grafana | Block height, peers, memory dekho |
| Backups | Cron + S3/Oracle storage | Chain data corrupt ho to restore |
| Log rotation | logrotate | Disk bharne se bachao |
| Snapshots | Daily cron | Naye nodes fast sync ho payein |
| Coordinated upgrades | Release + announcement + block-height activation | Sab validators ek saath update karein |
| Key security | Validator key offline, sirf signing key online | Hack hone pe stake safe |

---

## 6. Cost ka Poora Sach

| Stage | Infra | Monthly cost |
|---|---|---|
| Demo/testnet (1-3 nodes) | Laptop + tunnel, ya Oracle free | **₹0** ✅ |
| Public testnet (3-5 nodes) | Oracle free tier | **₹0** ✅ |
| Mainnet (5 validators + 2 RPC) | Hetzner/Contabo VPS | **~$100-300/month** (ya partners apna kharcha uthate hain — validators apne servers laate hain!) |
| Explorer + faucet | 1 chhota VPS | ~$10-25/month |

💡 **Secret jo sabse badi chains use karti hain:** mainnet pe validators **khud apne servers** chalate hain (jaise Ethereum ke validators apne nodes khud chalate hain) — chain banane wale ko har node ka kharcha nahi uthana padta! Tumhara kaam sirf software + genesis + coordination hai.

---

## 7. Deployment Roadmap (milestones)

- [ ] **D1:** Laptop pe 3-node chain + Cloudflare Tunnel → public demo link bana
- [ ] **D7:** Oracle free VM pe ek node 24/7 chal (systemd + monitoring)
- [ ] **D14:** Docker compose me pura network — ek command me deploy
- [ ] **M1-2:** Framework chain testnet pe (Cosmos ya OP Stack) — 3+ validators, explorer live
- [ ] **M3-6:** Public testnet — doosre log validators banein (community nodes!)
- [ ] **M12+:** Mainnet genesis — 5 partner validators, Mumbai RPC, HA sequencer

**Pehla target (D1):** ek public link jise kholte hi tumhari chain dikhe. Wo link hi tumhara pehla deployment hai. 🚀
