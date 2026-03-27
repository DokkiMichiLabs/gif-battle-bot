# GIF Battle Bot

A Discord bot that turns GIF posting into a competitive game.

Post a GIF, take the lead, and try to be the last one standing before the channel goes quiet.

## What It Does

GIF Battle Bot automatically runs battle rounds inside a Discord channel:

- A round starts when someone posts a valid GIF
- Other users jump in by posting their own GIFs
- The current leader is the last valid user to take over the battle
- If the channel stays quiet for the configured timeout, the current leader wins
- Points, XP, streaks, and stats are tracked persistently

This makes battles fair across time zones and keeps the game running naturally without manual setup.

## Core Features

- Automatic GIF battle rounds
- Last GIF standing wins
- Persistent round history
- Chaos Points scoring
- XP and levels
- Reaction-based crowd favorite bonus
- Win streak tracking
- Current champ role support
- Admin tools for battle control
- PostgreSQL-backed persistence
- Docker-friendly deployment

## Game Rules

### Battle Flow

- A new battle starts when someone posts a GIF
- Users battle by posting GIFs in the configured channel
- The current leader is the most recent valid takeover
- If the same user posts again, they do not add more time
- A new takeover adds only the configured time bonus to the current deadline
- If the round expires, the current leader wins
- The next GIF after an ended round starts a fresh round

### Rewards

**Win a battle**
- +10 Chaos Points

**Join a battle**
- +2 Chaos Points

**Crowd favorite bonus**
- +1 point per reaction from other users
- Max +5 bonus

**Streak bonus**
- Win 2 rounds in a row = +5 bonus

### XP and Levels

XP tracks long-term activity and progression.

- Users earn XP for battle actions such as successful takeovers and wins
- Levels show activity and experience in the game
- Level-up announcements can happen during live battles

## Commands

### Player Commands

- `/profile` — view your stats, XP, and level
- `/battle` — view the current battle status
- `/leaderboard` — view rankings
- `/champ` — show the current GIF Battle Champ
- `/pingbattle` — check battle-related info

### Admin Commands

- `/endbattle` — force-end the current battle

## Tech Stack

- Python
- discord.py
- PostgreSQL
- Docker

## Project Status

This project is in active development.

Planned future features include:

- richer battle history
- seasonal stats
- web leaderboard
- player profiles on a website
- better feedback/reporting tools
- more rewards and role systems
