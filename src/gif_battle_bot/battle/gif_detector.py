from __future__ import annotations

import re
from urllib.parse import urlparse

import discord


URL_REGEX = re.compile(r"https?://[^\s<>()]+", re.IGNORECASE)

GIF_PROVIDER_HOSTS = (
    "tenor.com",
    "giphy.com",
    "media.giphy.com",
    "i.giphy.com",
    "klipy.com",
    "static.klipy.com",
)

GIF_PROVIDER_MEDIA_EXTENSIONS = (".gif", ".mp4", ".webp")
GIF_PROVIDER_PATH_SEGMENTS = {"gif", "gifs"}


def extract_urls(text: str) -> list[str]:
    if not text:
        return []
    return URL_REGEX.findall(text)


def is_gif_url(url: str) -> bool:
    lowered = url.lower()

    if lowered.endswith(".gif"):
        return True

    parsed = urlparse(lowered)
    netloc = parsed.netloc.removeprefix("www.")
    path = parsed.path

    is_known_provider = any(netloc == host or netloc.endswith(f".{host}") for host in GIF_PROVIDER_HOSTS)
    if not is_known_provider:
        return False

    path_segments = {segment for segment in path.strip("/").split("/") if segment}
    if path_segments & GIF_PROVIDER_PATH_SEGMENTS:
        return True

    return path.endswith(GIF_PROVIDER_MEDIA_EXTENSIONS)


def attachment_is_gif(attachment: discord.Attachment) -> bool:
    name = (attachment.filename or "").lower()
    content_type = (attachment.content_type or "").lower()

    if name.endswith(".gif"):
        return True

    if content_type == "image/gif":
        return True

    return False


def embed_looks_like_gif(embed: discord.Embed) -> bool:
    possible_urls = []

    if embed.url:
        possible_urls.append(embed.url)
    if embed.thumbnail and embed.thumbnail.url:
        possible_urls.append(embed.thumbnail.url)
    if embed.image and embed.image.url:
        possible_urls.append(embed.image.url)
    if embed.video and embed.video.url:
        possible_urls.append(embed.video.url)

    return any(is_gif_url(url) for url in possible_urls)


def get_gif_detection_reason(message: discord.Message) -> str | None:
    for attachment in message.attachments:
        if attachment_is_gif(attachment):
            return f"attachment:{attachment.filename or attachment.url}"

    for url in extract_urls(message.content):
        if is_gif_url(url):
            return f"content_url:{url}"

    for embed in message.embeds:
        if embed_looks_like_gif(embed):
            return "embed_url"

    return None


def message_contains_gif(message: discord.Message) -> bool:
    return get_gif_detection_reason(message) is not None
