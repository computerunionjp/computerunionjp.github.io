"""WordPress のエクスポート XML (WXR 形式) を読み込むためのパーサ。"""

from __future__ import annotations

import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from pathlib import Path

WP_NS = "http://wordpress.org/export/1.2/"
CONTENT_NS = "http://purl.org/rss/1.0/modules/content/"


def _wp(tag: str) -> str:
    return f"{{{WP_NS}}}{tag}"


def _content(tag: str) -> str:
    return f"{{{CONTENT_NS}}}{tag}"


@dataclass
class WPCategory:
    domain: str
    nicename: str
    name: str


@dataclass
class WPItem:
    post_id: int
    post_type: str
    title: str
    link: str
    status: str
    post_date_gmt: str
    post_modified_gmt: str
    post_name: str
    content_html: str
    categories: list[WPCategory] = field(default_factory=list)

    def category_nicenames(self, domain: str = "category") -> set[str]:
        return {c.nicename for c in self.categories if c.domain == domain}


def parse_items(xml_path: str | Path) -> list[WPItem]:
    """WXR ファイルをパースして WPItem のリストを返す。"""
    tree = ET.parse(xml_path)
    channel = tree.getroot().find("channel")
    if channel is None:
        raise ValueError(
            "channel 要素が見つかりません。WordPress の WXR ファイルではない可能性があります。"
        )

    items: list[WPItem] = []
    for el in channel.findall("item"):
        post_type_el = el.find(_wp("post_type"))
        post_id_el = el.find(_wp("post_id"))
        if post_type_el is None or post_id_el is None:
            continue
        post_id_text = (post_id_el.text or "").strip()
        if not post_id_text:
            continue

        categories = [
            WPCategory(
                domain=c.get("domain", ""),
                nicename=c.get("nicename", ""),
                name=(c.text or "").strip(),
            )
            for c in el.findall("category")
        ]

        items.append(
            WPItem(
                post_id=int(post_id_text),
                post_type=(post_type_el.text or "").strip(),
                title=(el.findtext("title") or "").strip(),
                link=(el.findtext("link") or "").strip(),
                status=(el.findtext(_wp("status")) or "").strip(),
                post_date_gmt=(el.findtext(_wp("post_date_gmt")) or "").strip(),
                post_modified_gmt=(el.findtext(_wp("post_modified_gmt")) or "").strip(),
                post_name=(el.findtext(_wp("post_name")) or "").strip(),
                content_html=el.findtext(_content("encoded")) or "",
                categories=categories,
            )
        )
    return items
