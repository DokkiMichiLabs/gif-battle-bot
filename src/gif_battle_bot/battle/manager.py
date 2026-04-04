from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

from gif_battle_bot.battle.models import BattleRound
from typing import Any

# from gif_battle_bot.storage.postgres import PostgresStorage


@dataclass
class BattleUpdateResult:
    round_started: bool
    leader_changed: bool
    time_bonus_applied: bool
    current_leader_user_id: int
    participant_count: int
    started_at: datetime
    last_activity_at: datetime
    deadline_at: datetime


class BattleManager:
    def __init__(self, storage: Any,) -> None:
        self._storage = storage
        self._active_round: BattleRound | None = None

    def load_state(self) -> None:
        self._active_round = self._storage.load_active_round()

    def save_state(self) -> None:
        self._storage.save_active_round(self._active_round)

    def has_active_round(self) -> bool:
        return self._active_round is not None

    def get_active_round(self) -> BattleRound | None:
        return self._active_round

    def get_status_message_id(self) -> int | None:
        if self._active_round is None:
            return None
        return self._active_round.status_message_id

    def set_status_message_id(self, message_id: int | None) -> None:
        if self._active_round is None:
            return
        self._active_round.status_message_id = message_id
        self.save_state()

    def handle_gif_message(
        self,
        channel_id: int,
        user_id: int,
        message_id: int,
        battle_timeout_seconds: int,
        takeover_time_bonus_seconds: int,
    ) -> BattleUpdateResult:
        now = datetime.now(timezone.utc)

        if self._active_round is None:
            self._active_round = BattleRound.create(
                channel_id=channel_id,
                user_id=user_id,
                message_id=message_id,
                battle_timeout_seconds=battle_timeout_seconds,
            )
            self.save_state()
            return BattleUpdateResult(
                round_started=True,
                leader_changed=True,
                time_bonus_applied=False,
                current_leader_user_id=self._active_round.last_gif_user_id,
                participant_count=len(self._active_round.participant_ids),
                started_at=self._active_round.started_at,
                last_activity_at=self._active_round.last_activity_at,
                deadline_at=self._active_round.deadline_at,
            )

        if self._active_round.channel_id != channel_id:
            raise ValueError(
                f"BattleManager received channel_id={channel_id}, "
                f"but active round is for channel_id={self._active_round.channel_id}."
            )

        previous_leader_user_id = self._active_round.last_gif_user_id
        leader_changed = user_id != previous_leader_user_id

        self._active_round.participant_ids.add(user_id)
        self._active_round.add_gif_message(message_id=message_id, author_id=user_id)

        if leader_changed:
            self._active_round.last_gif_user_id = user_id
            self._active_round.last_activity_at = now
            base_time = max(self._active_round.deadline_at, now)
            self._active_round.deadline_at = base_time + timedelta(seconds=takeover_time_bonus_seconds)
        self.save_state()

        return BattleUpdateResult(
            round_started=False,
            leader_changed=leader_changed,
            time_bonus_applied=leader_changed,
            current_leader_user_id=self._active_round.last_gif_user_id,
            participant_count=len(self._active_round.participant_ids),
            started_at=self._active_round.started_at,
            last_activity_at=self._active_round.last_activity_at,
            deadline_at=self._active_round.deadline_at,
        )

    def record_reaction_add(
        self,
        message_id: int,
        reactor_user_id: int,
        emoji_key: str,
    ) -> bool:
        if self._active_round is None:
            return False

        gif_message = self._active_round.gif_messages.get(message_id)
        if gif_message is None:
            return False

        if reactor_user_id == gif_message.author_id:
            return False

        changed = gif_message.add_reaction(
            emoji_key=emoji_key,
            reactor_user_id=reactor_user_id,
        )

        if changed:
            self.save_state()

        return changed

    def record_reaction_remove(
        self,
        message_id: int,
        reactor_user_id: int,
        emoji_key: str,
    ) -> bool:
        if self._active_round is None:
            return False

        gif_message = self._active_round.gif_messages.get(message_id)
        if gif_message is None:
            return False

        changed = gif_message.remove_reaction(
            emoji_key=emoji_key,
            reactor_user_id=reactor_user_id,
        )

        if changed:
            self.save_state()

        return changed

    def get_deadline(self) -> datetime | None:
        if self._active_round is None:
            return None
        return self._active_round.deadline_at or self._active_round.last_activity_at

    def is_round_expired(self) -> bool:
        if self._active_round is None:
            return False

        now = datetime.now(timezone.utc)
        deadline = self.get_deadline()

        if deadline is None:
            return False

        return now >= deadline

    def get_seconds_until_timeout(self) -> int | None:
        if self._active_round is None:
            return None

        deadline = self.get_deadline()
        if deadline is None:
            return None

        now = datetime.now(timezone.utc)
        remaining = (deadline - now).total_seconds()

        return max(0, int(remaining))

    def end_round(self) -> BattleRound | None:
        finished_round = self._active_round
        self._active_round = None
        self.save_state()
        return finished_round