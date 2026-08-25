#!/usr/bin/env python3
"""
CyberLabs CLI — Interactive Cybersecurity Labs from the command line.

Usage:
    python cli.py list                         # List all labs
    python cli.py list --category web          # List web labs
    python cli.py start web-001 --player lo    # Start a lab
    python cli.py submit web-001 --flag FLAG{...} --player lo
    python cli.py hint web-001 --player lo     # Get a hint
    python cli.py stats --player lo            # Player stats
    python cli.py leaderboard                  # Top players
"""

import argparse
import json
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from platform import CyberLabs


def cmd_list(args):
    """List labs."""
    platform = CyberLabs()
    labs = platform.list_labs(category=args.category, difficulty=args.difficulty)

    print(f"\n📚 CyberLabs — {len(labs)} Labs\n")

    if not args.category:
        categories = platform.list_categories()
        print("Categories:")
        for cat, count in sorted(categories.items()):
            print(f"  {cat:<25} {count} labs")
        print()

    print(f"{'ID':<12} {'Name':<25} {'Difficulty':<15} {'Points':<8} {'XP'}")
    print("-" * 70)

    for lab in labs:
        diff_color = {"beginner": "🟢", "intermediate": "🟡", "advanced": "🔴", "expert": "⚫"}.get(lab.difficulty, "⚪")
        print(f"{lab.id:<12} {lab.name:<25} {diff_color} {lab.difficulty:<13} {lab.points:<8} {lab.xp_reward}")


def cmd_start(args):
    """Start a lab."""
    platform = CyberLabs()
    result = platform.start_lab(args.lab_id, args.player)

    if "error" in result:
        print(f"\n❌ {result['error']}")
        return

    print(f"\n🎯 Starting: {result['name']}")
    print(f"{'='*60}")
    print(f"  Category:   {result['category']}")
    print(f"  Difficulty: {result['difficulty']}")
    print(f"  Points:     {result['points']}")
    print(f"  XP Reward:  {result.get('xp_reward', 'N/A')}")
    print(f"  Attempt:    #{result['attempt']}")
    print(f"\n📋 Objective:")
    print(f"  {result['objective']}")
    print(f"\n📖 Instructions:")
    for i, inst in enumerate(result['instructions'], 1):
        print(f"  {i}. {inst}")
    print(f"\n💡 Hints available: {result['hints_available']}")
    print(f"  Use: python cli.py hint {args.lab_id} --player {args.player}")


def cmd_submit(args):
    """Submit a flag."""
    platform = CyberLabs()
    result = platform.submit_flag(args.lab_id, args.player, args.flag)

    if result.solved:
        print(f"\n✅ Correct! Lab {args.lab_id} solved!")
        print(f"  XP Earned: {result.xp_earned}")
        print(f"  Attempts:  {result.attempts}")
    else:
        print(f"\n❌ Incorrect flag. Try again!")
        print(f"  Attempts: {result.attempts + 1}")


def cmd_hint(args):
    """Get a hint."""
    platform = CyberLabs()
    hint = platform.get_hint(args.lab_id, args.player, args.index)

    if hint:
        print(f"\n💡 Hint #{args.index + 1}:")
        print(f"  {hint}")
    else:
        print(f"\n❌ No more hints available.")


def cmd_stats(args):
    """Player stats."""
    platform = CyberLabs()
    stats = platform.get_player_stats(args.player)

    p = stats["player"]
    print(f"\n📊 Player Stats: {p['name']}")
    print(f"{'='*60}")
    print(f"  Level:       {p['level']} (XP: {p['xp']})")
    print(f"  Completed:   {stats['completed']}/{stats['total_labs']} ({stats['completion_rate']:.1f}%)")
    print(f"  Badges:      {len(p['badges'])}")

    if p['badges']:
        print(f"\n  🏅 Badges:")
        for b in stats['badges']:
            print(f"    {b.get('icon', '🏅')} {b['name']}: {b.get('description', '')}")

    print(f"\n  📈 Category Progress:")
    for cat, data in stats['category_stats'].items():
        pct = data['completed'] / data['total'] * 100 if data['total'] > 0 else 0
        bar = "█" * int(pct / 10) + "░" * (10 - int(pct / 10))
        print(f"    {cat:<25} {bar} {data['completed']}/{data['total']}")


def cmd_leaderboard(args):
    """Show leaderboard."""
    platform = CyberLabs()
    board = platform.get_leaderboard(top=args.top)

    print(f"\n🏆 Leaderboard (Top {args.top})\n")

    if not board:
        print("  No players yet.")
        return

    print(f"{'Rank':<6} {'Name':<20} {'Level':<8} {'XP':<10} {'Labs'}")
    print("-" * 55)

    for entry in board:
        medal = {1: "🥇", 2: "🥈", 3: "🥉"}.get(entry['rank'], f"#{entry['rank']}")
        print(f"{medal:<6} {entry['name']:<20} Lv.{entry['level']:<6} {entry['xp']:<10} {entry['labs_completed']}")


def cmd_categories(args):
    """List categories."""
    platform = CyberLabs()
    cats = platform.list_categories()

    print(f"\n📚 Lab Categories\n")
    for cat, count in sorted(cats.items()):
        print(f"  {cat:<25} {count} labs")


def main():
    parser = argparse.ArgumentParser(description="🎯 CyberLabs CLI")
    sub = parser.add_subparsers(dest="command")

    # list
    list_p = sub.add_parser("list", help="List labs")
    list_p.add_argument("-c", "--category", help="Filter by category")
    list_p.add_argument("-d", "--difficulty", help="Filter by difficulty")

    # start
    start_p = sub.add_parser("start", help="Start a lab")
    start_p.add_argument("lab_id", help="Lab ID")
    start_p.add_argument("-p", "--player", default="default", help="Player ID")

    # submit
    submit_p = sub.add_parser("submit", help="Submit flag")
    submit_p.add_argument("lab_id", help="Lab ID")
    submit_p.add_argument("-f", "--flag", required=True, help="Flag to submit")
    submit_p.add_argument("-p", "--player", default="default", help="Player ID")

    # hint
    hint_p = sub.add_parser("hint", help="Get hint")
    hint_p.add_argument("lab_id", help="Lab ID")
    hint_p.add_argument("-p", "--player", default="default", help="Player ID")
    hint_p.add_argument("-i", "--index", type=int, default=0, help="Hint index")

    # stats
    stats_p = sub.add_parser("stats", help="Player stats")
    stats_p.add_argument("-p", "--player", default="default", help="Player ID")

    # leaderboard
    lb_p = sub.add_parser("leaderboard", help="Show leaderboard")
    lb_p.add_argument("-n", "--top", type=int, default=10, help="Top N players")

    # categories
    sub.add_parser("categories", help="List categories")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    commands = {
        "list": cmd_list,
        "start": cmd_start,
        "submit": cmd_submit,
        "hint": cmd_hint,
        "stats": cmd_stats,
        "leaderboard": cmd_leaderboard,
        "categories": cmd_categories,
    }

    commands[args.command](args)


if __name__ == "__main__":
    main()
