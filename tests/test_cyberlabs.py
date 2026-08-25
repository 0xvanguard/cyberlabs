"""Tests for CyberLabs."""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from platform import CyberLabs, Lab, Player, LabResult


def test_init():
    """Test platform initialization."""
    platform = CyberLabs(save_dir="/tmp/cyberlabs_test")
    assert len(platform.labs) > 0
    assert len(platform.list_categories()) == 6


def test_list_labs():
    """Test listing labs."""
    platform = CyberLabs(save_dir="/tmp/cyberlabs_test")
    web_labs = platform.list_labs(category="web")
    assert len(web_labs) == 5
    for lab in web_labs:
        assert lab.category == "web"


def test_get_lab():
    """Test getting specific lab."""
    platform = CyberLabs(save_dir="/tmp/cyberlabs_test")
    lab = platform.get_lab("web-001")
    assert lab is not None
    assert lab.id == "web-001"
    assert lab.name == "Reflected XSS"


def test_player_creation():
    """Test player creation."""
    platform = CyberLabs(save_dir="/tmp/cyberlabs_test")
    player = platform.get_player("test_player", "TestUser")
    assert player.id == "test_player"
    assert player.name == "TestUser"
    assert player.xp == 0


def test_start_lab():
    """Test starting a lab."""
    platform = CyberLabs(save_dir="/tmp/cyberlabs_test")
    result = platform.start_lab("web-001", "test_player")
    assert "error" not in result
    assert result["lab_id"] == "web-001"
    assert result["attempt"] == 1


def test_submit_correct():
    """Test correct flag submission."""
    platform = CyberLabs(save_dir="/tmp/cyberlabs_test")
    platform.start_lab("web-001", "test_player")
    result = platform.submit_flag("web-001", "test_player", "FLAG{xss_reflected_1nject3d}")
    assert result.solved is True
    assert result.xp_earned > 0


def test_submit_incorrect():
    """Test incorrect flag submission."""
    platform = CyberLabs(save_dir="/tmp/cyberlabs_test")
    platform.start_lab("web-001", "test_player")
    result = platform.submit_flag("web-001", "test_player", "FLAG{wrong_answer}")
    assert result.solved is False
    assert result.xp_earned == 0


def test_hint():
    """Test getting hints."""
    platform = CyberLabs(save_dir="/tmp/cyberlabs_test")
    hint = platform.get_hint("web-001", "test_player", 0)
    assert hint is not None
    assert len(hint) > 0


def test_player_stats():
    """Test player statistics."""
    import shutil
    shutil.rmtree("/tmp/cyberlabs_stats_test", ignore_errors=True)
    platform = CyberLabs(save_dir="/tmp/cyberlabs_stats_test")
    platform.start_lab("web-001", "stats_player")
    platform.submit_flag("web-001", "stats_player", "FLAG{xss_reflected_1nject3d}")
    stats = platform.get_player_stats("stats_player")
    assert stats["completed"] == 1
    assert stats["player"]["xp"] > 0


def test_xp_level_up():
    """Test XP and level up."""
    player = Player(id="test", name="Test")
    player.add_xp(100)
    assert player.level >= 2
    assert player.xp == 100


def test_badges():
    """Test badge system."""
    platform = CyberLabs(save_dir="/tmp/cyberlabs_test")
    platform.start_lab("web-001", "badge_player")
    platform.submit_flag("web-001", "badge_player", "FLAG{xss_reflected_1nject3d}")
    player = platform.get_player("badge_player")
    assert "first_lab" in player.badges


def test_categories():
    """Test category listing."""
    platform = CyberLabs(save_dir="/tmp/cyberlabs_test")
    cats = platform.list_categories()
    assert "web" in cats
    assert "crypto" in cats
    assert "forensics" in cats
    assert "network" in cats
    assert "malware" in cats
    assert "reverse_engineering" in cats


def test_stats():
    """Test platform statistics."""
    platform = CyberLabs(save_dir="/tmp/cyberlabs_test")
    stats = platform.stats()
    assert stats["total_labs"] == 30
    assert stats["categories"]["web"] == 5


if __name__ == "__main__":
    test_init()
    test_list_labs()
    test_get_lab()
    test_player_creation()
    test_start_lab()
    test_submit_correct()
    test_submit_incorrect()
    test_hint()
    test_player_stats()
    test_xp_level_up()
    test_badges()
    test_categories()
    test_stats()
    print("✅ All tests passed!")
