"""
CyberLabs — Interactive Cybersecurity Labs Platform

A Python library for managing cybersecurity labs with XP, badges, and progress tracking.
Supports 6 categories: Web, Crypto, Forensics, Network, Malware, Reverse Engineering.

Usage:
    from cyberlabs import CyberLabs

    platform = CyberLabs()
    labs = platform.list_labs(category="web")
    print(f"Found {len(labs)} web security labs")
"""

import json
import hashlib
import random
import time
from pathlib import Path
from dataclasses import dataclass, field, asdict
from typing import Optional, List, Dict, Any, Callable
from enum import Enum
from datetime import datetime


class Difficulty(Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"


class LabCategory(Enum):
    WEB = "web"
    CRYPTO = "crypto"
    FORENSICS = "forensics"
    NETWORK = "network"
    MALWARE = "malware"
    REVERSE_ENGINEERING = "reverse_engineering"


@dataclass
class Lab:
    """A single cybersecurity lab."""
    id: str
    name: str
    category: str
    difficulty: str
    description: str
    objective: str
    instructions: List[str]
    hints: List[str]
    flag: str
    points: int
    xp_reward: int
    time_limit: int = 3600  # seconds
    tags: List[str] = field(default_factory=list)
    prerequisites: List[str] = field(default_factory=list)
    files: Dict[str, str] = field(default_factory=dict)  # filename -> content
    validator: Optional[str] = None  # Python code to validate answer

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class LabResult:
    """Result of completing a lab."""
    lab_id: str
    player_id: str
    solved: bool
    time_taken: int = 0
    attempts: int = 0
    hints_used: int = 0
    xp_earned: int = 0
    completed_at: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class Player:
    """Player profile with progress tracking."""
    id: str
    name: str
    xp: int = 0
    level: int = 1
    badges: List[str] = field(default_factory=list)
    labs_completed: List[str] = field(default_factory=list)
    labs_attempted: Dict[str, int] = field(default_factory=dict)  # lab_id -> attempts
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    last_active: str = field(default_factory=lambda: datetime.now().isoformat())

    @property
    def xp_to_next_level(self) -> int:
        return self.level * 100

    @property
    def progress_percent(self) -> float:
        if self.xp_to_next_level == 0:
            return 0
        return min((self.xp % self.xp_to_next_level) / self.xp_to_next_level * 100, 100)

    def add_xp(self, amount: int) -> bool:
        """Add XP and check for level up. Returns True if leveled up."""
        self.xp += amount
        old_level = self.level
        while self.xp >= self.level * 100:
            self.level += 1
        return self.level > old_level

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class CyberLabs:
    """
    Interactive Cybersecurity Labs Platform.

    Provides labs across 6 categories with XP, badges, and progress tracking.
    """

    BADGES = {
        "first_lab": {"name": "First Blood", "description": "Complete your first lab", "icon": "🩸"},
        "web_10": {"name": "Web Warrior", "description": "Complete 10 web labs", "icon": "🌐"},
        "crypto_10": {"name": "Crypto Cracker", "description": "Complete 10 crypto labs", "icon": "🔐"},
        "forensics_10": {"name": "Digital Detective", "description": "Complete 10 forensics labs", "icon": "🔍"},
        "network_10": {"name": "Network Ninja", "description": "Complete 10 network labs", "icon": "🕸️"},
        "malware_10": {"name": "Malware Hunter", "description": "Complete 10 malware labs", "icon": "🦠"},
        "reverse_10": {"name": "Binary Breaker", "description": "Complete 10 reverse engineering labs", "icon": "⚙️"},
        "speed_demon": {"name": "Speed Demon", "description": "Complete a lab in under 60 seconds", "icon": "⚡"},
        "no_hints": {"name": "Lone Wolf", "description": "Complete 5 labs without hints", "icon": "🐺"},
        "perfect": {"name": "Perfectionist", "description": "Complete a lab on first attempt", "icon": "💎"},
        "level_5": {"name": "Rising Star", "description": "Reach level 5", "icon": "⭐"},
        "level_10": {"name": "Cyber Expert", "description": "Reach level 10", "icon": "🌟"},
        "all_categories": {"name": "Jack of All Trades", "description": "Complete labs in all categories", "icon": "🎯"},
        "century": {"name": "Century Club", "description": "Complete 100 labs", "icon": "🏆"},
    }

    def __init__(self, data_dir: Optional[str] = None, save_dir: Optional[str] = None):
        """
        Initialize CyberLabs.

        Args:
            data_dir: Directory containing lab definitions.
            save_dir: Directory for saving player progress.
        """
        self.labs: List[Lab] = []
        self.players: Dict[str, Player] = {}
        self.results: List[LabResult] = []
        self.save_dir = Path(save_dir or "/tmp/cyberlabs")
        self.save_dir.mkdir(parents=True, exist_ok=True)

        # Load built-in labs
        self._load_builtin_labs()

        # Load custom labs if directory provided
        if data_dir:
            self._load_from_dir(data_dir)

        # Load saved players
        self._load_players()

    def _load_builtin_labs(self) -> None:
        """Load built-in lab collection."""
        self.labs.extend(self._get_web_labs())
        self.labs.extend(self._get_crypto_labs())
        self.labs.extend(self._get_forensics_labs())
        self.labs.extend(self._get_network_labs())
        self.labs.extend(self._get_malware_labs())
        self.labs.extend(self._get_reverse_labs())

    def _load_from_dir(self, directory: str) -> None:
        """Load labs from JSON files."""
        dir_path = Path(directory)
        if not dir_path.exists():
            return
        for json_file in dir_path.glob("*.json"):
            try:
                with open(json_file) as f:
                    data = json.load(f)
                for lab_data in data.get("labs", []):
                    self.labs.append(Lab(**lab_data))
            except (json.JSONDecodeError, KeyError):
                continue

    def _load_players(self) -> None:
        """Load saved player data."""
        players_file = self.save_dir / "players.json"
        if players_file.exists():
            try:
                with open(players_file) as f:
                    data = json.load(f)
                for pid, pdata in data.items():
                    self.players[pid] = Player(**pdata)
            except (json.JSONDecodeError, KeyError):
                pass

    def _save_players(self) -> None:
        """Save player data."""
        players_file = self.save_dir / "players.json"
        data = {pid: p.to_dict() for pid, p in self.players.items()}
        with open(players_file, "w") as f:
            json.dump(data, f, indent=2)

    # ─── Public API ──────────────────────────────────────────────────────

    def list_labs(self, category: Optional[str] = None,
                  difficulty: Optional[str] = None) -> List[Lab]:
        """List labs with optional filters."""
        result = self.labs
        if category:
            result = [l for l in result if l.category == category]
        if difficulty:
            result = [l for l in result if l.difficulty == difficulty]
        return result

    def get_lab(self, lab_id: str) -> Optional[Lab]:
        """Get a specific lab by ID."""
        for lab in self.labs:
            if lab.id == lab_id:
                return lab
        return None

    def list_categories(self) -> Dict[str, int]:
        """List all categories with lab counts."""
        categories = {}
        for lab in self.labs:
            categories[lab.category] = categories.get(lab.category, 0) + 1
        return categories

    def get_player(self, player_id: str, name: Optional[str] = None) -> Player:
        """Get or create a player."""
        if player_id not in self.players:
            self.players[player_id] = Player(
                id=player_id,
                name=name or f"Player_{player_id[:8]}",
            )
            self._save_players()
        return self.players[player_id]

    def start_lab(self, lab_id: str, player_id: str) -> Dict[str, Any]:
        """Start a lab and return instructions."""
        lab = self.get_lab(lab_id)
        if not lab:
            return {"error": f"Lab not found: {lab_id}"}

        player = self.get_player(player_id)

        # Track attempt
        attempts = player.labs_attempted.get(lab_id, 0)
        player.labs_attempted[lab_id] = attempts + 1
        player.last_active = datetime.now().isoformat()
        self._save_players()

        return {
            "lab_id": lab.id,
            "name": lab.name,
            "category": lab.category,
            "difficulty": lab.difficulty,
            "objective": lab.objective,
            "instructions": lab.instructions,
            "hints_available": len(lab.hints),
            "points": lab.points,
            "time_limit": lab.time_limit,
            "files": lab.files,
            "attempt": attempts + 1,
        }

    def submit_flag(self, lab_id: str, player_id: str, flag: str) -> LabResult:
        """Submit a flag answer."""
        lab = self.get_lab(lab_id)
        if not lab:
            return LabResult(lab_id=lab_id, player_id=player_id, solved=False)

        player = self.get_player(player_id)
        attempts = player.labs_attempted.get(lab_id, 0)

        # Check flag
        solved = flag.strip() == lab.flag.strip()

        # Calculate XP
        xp_earned = 0
        if solved:
            xp_earned = lab.xp_reward
            # Bonus for first attempt
            if attempts <= 1:
                xp_earned = int(xp_earned * 1.5)
            # Penalty for hints
            hints_used = player.labs_attempted.get(f"{lab_id}_hints", 0)
            xp_earned = max(xp_earned - hints_used * 10, 10)

            # Add XP and check level up
            leveled_up = player.add_xp(xp_earned)
            player.labs_completed.append(lab_id)

            # Check badge eligibility
            self._check_badges(player)

        result = LabResult(
            lab_id=lab_id,
            player_id=player_id,
            solved=solved,
            attempts=attempts,
            xp_earned=xp_earned,
        )
        self.results.append(result)
        self._save_players()

        return result

    def get_hint(self, lab_id: str, player_id: str, hint_index: int = 0) -> Optional[str]:
        """Get a hint for a lab."""
        lab = self.get_lab(lab_id)
        if not lab:
            return None

        player = self.get_player(player_id)

        # Track hint usage
        hint_key = f"{lab_id}_hints"
        current_hints = player.labs_attempted.get(hint_key, 0)
        player.labs_attempted[hint_key] = current_hints + 1
        self._save_players()

        if hint_index < len(lab.hints):
            return lab.hints[hint_index]
        return None

    def get_player_stats(self, player_id: str) -> Dict[str, Any]:
        """Get player statistics."""
        player = self.get_player(player_id)

        category_stats = {}
        for lab in self.labs:
            cat = lab.category
            if cat not in category_stats:
                category_stats[cat] = {"total": 0, "completed": 0}
            category_stats[cat]["total"] += 1
            if lab.id in player.labs_completed:
                category_stats[cat]["completed"] += 1

        return {
            "player": player.to_dict(),
            "total_labs": len(self.labs),
            "completed": len(player.labs_completed),
            "completion_rate": len(player.labs_completed) / len(self.labs) * 100 if self.labs else 0,
            "category_stats": category_stats,
            "badges": [self.BADGES.get(b, {"name": b}) for b in player.badges],
        }

    def get_leaderboard(self, top: int = 10) -> List[Dict[str, Any]]:
        """Get top players by XP."""
        sorted_players = sorted(self.players.values(), key=lambda p: p.xp, reverse=True)
        return [
            {
                "rank": i + 1,
                "name": p.name,
                "xp": p.xp,
                "level": p.level,
                "labs_completed": len(p.labs_completed),
            }
            for i, p in enumerate(sorted_players[:top])
        ]

    def export_results(self, output_file: str, format: str = "json") -> int:
        """Export lab results."""
        with open(output_file, "w") as f:
            if format == "json":
                data = {
                    "exported_at": datetime.now().isoformat(),
                    "total_results": len(self.results),
                    "results": [r.to_dict() for r in self.results],
                }
                json.dump(data, f, indent=2)
        return len(self.results)

    def stats(self) -> Dict[str, Any]:
        """Get platform statistics."""
        return {
            "total_labs": len(self.labs),
            "categories": self.list_categories(),
            "total_players": len(self.players),
            "total_results": len(self.results),
            "total_xp_awarded": sum(r.xp_earned for r in self.results),
        }

    # ─── Badge System ────────────────────────────────────────────────────

    def _check_badges(self, player: Player) -> None:
        """Check and award badges."""
        # First lab
        if "first_lab" not in player.badges and len(player.labs_completed) >= 1:
            player.badges.append("first_lab")

        # Category badges
        category_counts = {}
        for lab_id in player.labs_completed:
            lab = self.get_lab(lab_id)
            if lab:
                category_counts[lab.category] = category_counts.get(lab.category, 0) + 1

        badge_map = {
            "web": "web_10",
            "crypto": "crypto_10",
            "forensics": "forensics_10",
            "network": "network_10",
            "malware": "malware_10",
            "reverse_engineering": "reverse_10",
        }

        for cat, badge in badge_map.items():
            if badge not in player.badges and category_counts.get(cat, 0) >= 10:
                player.badges.append(badge)

        # Level badges
        if "level_5" not in player.badges and player.level >= 5:
            player.badges.append("level_5")
        if "level_10" not in player.badges and player.level >= 10:
            player.badges.append("level_10")

        # All categories
        if "all_categories" not in player.badges and len(category_counts) >= 6:
            player.badges.append("all_categories")

    # ─── Built-in Labs ───────────────────────────────────────────────────

    def _get_web_labs(self) -> List[Lab]:
        """Web security labs."""
        return [
            Lab(
                id="web-001", name="Reflected XSS", category="web", difficulty="beginner",
                description="Find and exploit a reflected XSS vulnerability",
                objective="Inject JavaScript that triggers an alert()",
                instructions=["Navigate to the search page", "Enter a payload in the search box", "Observe the reflection"],
                hints=["Try <script>alert(1)</script>", "Check if input is reflected in the page", "Look for injection points in HTML"],
                flag="FLAG{xss_reflected_1nject3d}", points=100, xp_reward=50,
                tags=["xss", "injection", "beginner"],
            ),
            Lab(
                id="web-002", name="SQL Injection", category="web", difficulty="beginner",
                description="Exploit a SQL injection vulnerability",
                objective="Bypass authentication using SQL injection",
                instructions=["Go to the login page", "Try special characters in the username field", "Bypass the password check"],
                hints=["Try ' OR '1'='1", "Use UNION SELECT to extract data", "Check for blind SQLi"],
                flag="FLAG{sql_1nj3ct10n_auth_bypass}", points=150, xp_reward=75,
                tags=["sqli", "injection", "authentication"],
            ),
            Lab(
                id="web-003", name="CSRF Attack", category="web", difficulty="intermediate",
                description="Craft a CSRF exploit to change a user's password",
                objective="Create a malicious page that changes the admin password",
                instructions=["Analyze the password change request", "Identify CSRF token behavior", "Create a CSRF PoC"],
                hints=["Check if CSRF token is validated", "Try removing the token", "Use auto-submitting form"],
                flag="FLAG{csrf_t0k3n_byp4ss3d}", points=200, xp_reward=100,
                tags=["csrf", "token", "form"],
            ),
            Lab(
                id="web-004", name="File Upload Bypass", category="web", difficulty="intermediate",
                description="Upload a web shell by bypassing file restrictions",
                objective="Upload and execute a PHP web shell",
                instructions=["Try uploading different file types", "Check file type validation", "Bypass content-type check"],
                hints=["Try changing Content-Type header", "Use double extension (.php.jpg)", "Check for magic bytes validation"],
                flag="FLAG{upl04d_byp4ss3d_sh3ll}", points=200, xp_reward=100,
                tags=["upload", "bypass", "shell"],
            ),
            Lab(
                id="web-005", name="SSRF Exploitation", category="web", difficulty="advanced",
                description="Exploit Server-Side Request Forgery to access internal services",
                objective="Access the internal admin panel via SSRF",
                instructions=["Find the SSRF vulnerability", "Enumerate internal services", "Access the admin panel"],
                hints=["Try 127.0.0.1 and localhost", "Check for URL validation bypass", "Use file:// protocol"],
                flag="FLAG{ssrf_1nt3r4l_4cc3ss}", points=300, xp_reward=150,
                tags=["ssrf", "internal", "enumeration"],
            ),
        ]

    def _get_crypto_labs(self) -> List[Lab]:
        """Cryptography labs."""
        return [
            Lab(
                id="crypto-001", name="Caesar Cipher", category="crypto", difficulty="beginner",
                description="Decrypt a message encrypted with Caesar cipher",
                objective="Find the shift value and decrypt the message",
                instructions=["Analyze the ciphertext", "Try different shift values", "Decrypt the message"],
                hints=["Try shifting by 1-25", "Look for common words", "The shift is 13 (ROT13)"],
                flag="FLAG{c43s4r_sh1ft_f0und}", points=100, xp_reward=50,
                tags=["caesar", "cipher", "beginner"],
            ),
            Lab(
                id="crypto-002", name="Base64 Challenge", category="crypto", difficulty="beginner",
                description="Decode multiple layers of encoding",
                objective="Decode Base64, then Hex, then find the flag",
                instructions=["Identify the encoding", "Decode each layer", "Combine the results"],
                hints=["First layer is Base64", "Second layer is Hex", "Third layer is ROT13"],
                flag="FLAG{mult1l4y3r_d3c0d3d}", points=150, xp_reward=75,
                tags=["base64", "hex", "encoding"],
            ),
            Lab(
                id="crypto-003", name="RSA Weak Key", category="crypto", difficulty="intermediate",
                description="Factor a weak RSA modulus to break encryption",
                objective="Factor N and decrypt the ciphertext",
                instructions=["Extract N and e from the public key", "Factor N", "Calculate private key d"],
                hints=["N is small enough to factor", "Try factordb.com", "Use sympy.factorint()"],
                flag="FLAG{rs4_f4ct0r3d_br0k3n}", points=250, xp_reward=125,
                tags=["rsa", "factoring", "public_key"],
            ),
            Lab(
                id="crypto-004", name="XOR Encryption", category="crypto", difficulty="intermediate",
                description="Break XOR encryption with known plaintext",
                objective="Recover the key and decrypt the message",
                instructions=["Identify the XOR pattern", "Use known plaintext to find key", "Decrypt the full message"],
                hints=["Try single-byte XOR first", "Use frequency analysis", "Check for repeating key"],
                flag="FLAG{x0r_k3y_r3c0v3r3d}", points=200, xp_reward=100,
                tags=["xor", "symmetric", "key_recovery"],
            ),
            Lab(
                id="crypto-005", name="Hash Collision", category="crypto", difficulty="advanced",
                description="Find a hash collision for MD5",
                objective="Generate two different inputs with the same MD5 hash",
                instructions=["Understand MD5 structure", "Research collision attacks", "Generate collision"],
                hints=["Look at MD5sim", "Use fastcoll tool", "The collision prefix is known"],
                flag="FLAG{md5_c0ll1s10n_f0und}", points=300, xp_reward=150,
                tags=["hash", "collision", "md5"],
            ),
        ]

    def _get_forensics_labs(self) -> List[Lab]:
        """Digital forensics labs."""
        return [
            Lab(
                id="fore-001", name="File Carving", category="forensics", difficulty="beginner",
                description="Recover deleted files from a disk image",
                objective="Extract the hidden flag file",
                instructions=["Analyze the disk image", "Look for file signatures", "Recover the deleted file"],
                hints=["Use foremost or scalpel", "Check for JPEG header (FFD8FF)", "The flag is in a text file"],
                flag="FLAG{f1l3_c4rv3d_r3c0v3r3d}", points=150, xp_reward=75,
                tags=["carving", "recovery", "disk"],
            ),
            Lab(
                id="fore-002", name="Steganography", category="forensics", difficulty="beginner",
                description="Find hidden data in an image file",
                objective="Extract the hidden flag from the PNG",
                instructions=["Examine the image metadata", "Check for hidden data", "Extract the flag"],
                hints=["Try strings command", "Check LSB encoding", "Use stegsolve or zsteg"],
                flag="FLAG{st3g0_h1dd3n_m3ss4g3}", points=150, xp_reward=75,
                tags=["steganography", "image", "hidden"],
            ),
            Lab(
                id="fore-003", name="Memory Forensics", category="forensics", difficulty="intermediate",
                description="Analyze a memory dump to find evidence",
                objective="Find the password and flag in the memory dump",
                instructions=["Load the memory dump in Volatility", "Identify the process", "Extract credentials"],
                hints=["Use pslist to see processes", "Check for credential files", "Look for notepad.exe"],
                flag="FLAG{m3m0ry_f0r3ns1cs_w1n}", points=250, xp_reward=125,
                tags=["memory", "volatility", "credentials"],
            ),
            Lab(
                id="fore-004", name="PCAP Analysis", category="forensics", difficulty="intermediate",
                description="Analyze network traffic capture for secrets",
                objective="Find the exfiltrated data in the PCAP",
                instructions=["Open the PCAP in Wireshark", "Follow the TCP streams", "Extract the data"],
                hints=["Filter for HTTP traffic", "Check for FTP credentials", "Look at DNS queries"],
                flag="FLAG{p4p_4n4lys1s_d4t4_f0und}", points=200, xp_reward=100,
                tags=["pcap", "network", "wireshark"],
            ),
            Lab(
                id="fore-005", name="Log Analysis", category="forensics", difficulty="advanced",
                description="Analyze system logs to trace an attacker",
                objective="Identify the attacker's IP and method of entry",
                instructions=["Review auth logs", "Find suspicious activity", "Trace the attack chain"],
                hints=["Check /var/log/auth.log", "Look for failed SSH attempts", "Find the successful login"],
                flag="FLAG{l0g_4n4lys1s_4tt4ck3r_f0und}", points=300, xp_reward=150,
                tags=["logs", "ssh", "attack_chain"],
            ),
        ]

    def _get_network_labs(self) -> List[Lab]:
        """Network security labs."""
        return [
            Lab(
                id="net-001", name="Network Scanning", category="network", difficulty="beginner",
                description="Discover hosts and services on a network",
                objective="Find all open ports on the target",
                instructions=["Use nmap to scan the target", "Identify open ports", "Document the services"],
                hints=["Try nmap -sV target", "Check common ports first", "Use -O for OS detection"],
                flag="FLAG{n3twerk_sc4n_c0mpl3t3}", points=100, xp_reward=50,
                tags=["nmap", "scanning", "discovery"],
            ),
            Lab(
                id="net-002", name="Packet Analysis", category="network", difficulty="beginner",
                description="Analyze captured network packets",
                objective="Find the hidden message in the traffic",
                instructions=["Open the packet capture", "Filter for interesting traffic", "Extract the data"],
                hints=["Look for HTTP traffic", "Check DNS queries", "Follow TCP streams"],
                flag="FLAG{p4ck3t_4n4lys1s_f0und}", points=150, xp_reward=75,
                tags=["packets", "analysis", "traffic"],
            ),
            Lab(
                id="net-003", name="Firewall Bypass", category="network", difficulty="intermediate",
                description="Bypass firewall rules to access a service",
                objective="Connect to the restricted service",
                instructions=["Analyze firewall rules", "Find allowed ports", "Tunnel through allowed port"],
                hints=["Check for port knocking", "Try SSH tunneling", "Look for misconfigurations"],
                flag="FLAG{f1r3w4ll_byp4ss3d}", points=250, xp_reward=125,
                tags=["firewall", "bypass", "tunneling"],
            ),
            Lab(
                id="net-004", name="DNS Enumeration", category="network", difficulty="intermediate",
                description="Enumerate subdomains and find hidden services",
                objective="Find the hidden admin subdomain",
                instructions=["Perform DNS enumeration", "Check for zone transfers", "Brute-force subdomains"],
                hints=["Try dig axfr", "Use subfinder or amass", "Check for common subdomain names"],
                flag="FLAG{dns_3num3r4t10n_h1dd3n}", points=200, xp_reward=100,
                tags=["dns", "enumeration", "subdomains"],
            ),
            Lab(
                id="net-005", name="Man-in-the-Middle", category="network", difficulty="advanced",
                description="Perform a MITM attack to intercept traffic",
                objective="Capture credentials from intercepted traffic",
                instructions=["Set up ARP spoofing", "Intercept traffic", "Extract credentials"],
                hints=["Use arpspoof or bettercap", "Enable IP forwarding", "Capture HTTP basic auth"],
                flag="FLAG{m1tm_4tt4ck_cr3d3nt14ls}", points=300, xp_reward=150,
                tags=["mitm", "arp", "credentials"],
            ),
        ]

    def _get_malware_labs(self) -> List[Lab]:
        """Malware analysis labs."""
        return [
            Lab(
                id="mal-001", name="Malware Identification", category="malware", difficulty="beginner",
                description="Identify the type of malware sample",
                objective="Determine the malware family and behavior",
                instructions=["Run the sample in a sandbox", "Check file properties", "Analyze behavior"],
                hints=["Check file hashes on VirusTotal", "Look for strings", "Monitor network connections"],
                flag="FLAG{m4lw4r3_1d3nt1f13d}", points=150, xp_reward=75,
                tags=["analysis", "identification", "sandbox"],
            ),
            Lab(
                id="mal-002", name="String Analysis", category="malware", difficulty="beginner",
                description="Extract and analyze strings from malware",
                objective="Find the C2 server address in the strings",
                instructions=["Run strings on the binary", "Look for URLs and IPs", "Identify C2 infrastructure"],
                hints=["Use strings -a", "Filter for HTTP/HTTPS", "Check for encoded strings"],
                flag="FLAG{str1ngs_c2_f0und}", points=100, xp_reward=50,
                tags=["strings", "c2", "analysis"],
            ),
            Lab(
                id="mal-003", name="Packed Binary", category="malware", difficulty="intermediate",
                description="Unpack a packed malware sample",
                objective="Unpack and analyze the real payload",
                instructions=["Identify the packer", "Find the OEP", "Dump the unpacked binary"],
                hints=["Check for UPX signature", "Use OllyDbg or x64dbg", "Set breakpoint on VirtualAlloc"],
                flag="FLAG{p4ck3d_und3rp4ck3d}", points=250, xp_reward=125,
                tags=["packing", "unpacking", "upx"],
            ),
            Lab(
                id="mal-004", name="Ransomware Analysis", category="malware", difficulty="advanced",
                description="Analyze ransomware behavior and find recovery options",
                objective="Determine if files can be recovered",
                instructions=["Analyze encryption method", "Check for key storage", "Look for recovery flaws"],
                hints=["Check for hardcoded keys", "Analyze crypto implementation", "Look for key in memory"],
                flag="FLAG{r4ns0mw4r3_k3y_f0und}", points=300, xp_reward=150,
                tags=["ransomware", "encryption", "recovery"],
            ),
            Lab(
                id="mal-005", name="Rootkit Detection", category="malware", difficulty="advanced",
                description="Detect and analyze a kernel rootkit",
                objective="Find the hidden backdoor in the system",
                instructions=["Check for hooks", "Compare system calls", "Analyze kernel modules"],
                hints=["Use rkhunter", "Check /proc for anomalies", "Compare with clean system"],
                flag="FLAG{r00tk1t_d3t3ct3d}", points=300, xp_reward=150,
                tags=["rootkit", "kernel", "detection"],
            ),
        ]

    def _get_reverse_labs(self) -> List[Lab]:
        """Reverse engineering labs."""
        return [
            Lab(
                id="rev-001", name="Basic RE", category="reverse_engineering", difficulty="beginner",
                description="Reverse engineer a simple binary",
                objective="Find the flag in the executable",
                instructions=["Open in a disassembler", "Find the main function", "Trace the flag"],
                hints=["Use Ghidra or IDA", "Look for string comparisons", "Check the XOR loop"],
                flag="FLAG{b4s1c_r3_v3rs3d}", points=100, xp_reward=50,
                tags=["basic", "disassembly", "strings"],
            ),
            Lab(
                id="rev-002", name="License Key", category="reverse_engineering", difficulty="beginner",
                description="Reverse engineer a license key check",
                objective="Generate a valid license key",
                instructions=["Analyze the validation function", "Understand the algorithm", "Generate a key"],
                hints=["Look for strlen checks", "The key format is XXXX-XXXX", "Check the comparison logic"],
                flag="FLAG{l1c3ns3_k3y_g3n3r4t3d}", points=150, xp_reward=75,
                tags=["license", "keygen", "validation"],
            ),
            Lab(
                id="rev-003", name="Anti-Debug", category="reverse_engineering", difficulty="intermediate",
                description="Bypass anti-debugging techniques",
                objective="Debug through the anti-analysis protections",
                instructions=["Identify the anti-debug method", "Bypass the check", "Continue debugging"],
                hints=["Check for IsDebuggerPresent", "Patch the conditional jump", "Use a kernel debugger"],
                flag="FLAG{4nt1_d3bug_byp4ss3d}", points=250, xp_reward=125,
                tags=["anti-debug", "patching", "bypass"],
            ),
            Lab(
                id="rev-004", name="Crypter Analysis", category="reverse_engineering", difficulty="advanced",
                description="Analyze a crypter-protected binary",
                objective="Extract the original payload",
                instructions=["Analyze the crypter stub", "Find the decryption routine", "Dump the payload"],
                hints=["Set breakpoint on VirtualAlloc", "Follow the decryption loop", "Dump after decryption"],
                flag="FLAG{cr1pt3r_p4y104d_3xtr4ct3d}", points=300, xp_reward=150,
                tags=["crypter", "payload", "extraction"],
            ),
            Lab(
                id="rev-005", name="VM Protection", category="reverse_engineering", difficulty="expert",
                description="Reverse engineer a VM-protected binary",
                objective="Understand the virtual machine and extract logic",
                instructions=["Identify the VM opcode handler", "Map the instruction set", "Emulate the VM"],
                hints=["Look for switch statements", "Map opcodes to operations", "Write an emulator"],
                flag="FLAG{vm_pr0t3ct10n_br0k3n}", points=500, xp_reward=250,
                tags=["vm", "protection", "emulation"],
            ),
        ]

    def __len__(self) -> int:
        return len(self.labs)

    def __repr__(self) -> str:
        return f"CyberLabs(labs={len(self.labs)}, categories={len(self.list_categories())})"
