#!/usr/bin/env python3
"""Validate and optionally invoke the searchAcademicLiterature MCP tool.

This helper validates the original query and invokes the configured MCP
endpoint. It does not store credentials or configure an authentication mode.
"""

from __future__ import annotations

import argparse
import json
import sys
from typing import Any

import requests

MAX_QUERY_LENGTH = 128
MAX_TOP_N = 50
DEFAULT_TOP_N = 10
TOOL_NAME = "searchAcademicLiterature"
MCP_URL = "https://sci.ksai.scnet.cn:58043/scnetmcp"
REQUEST_TIMEOUT = 360


def validate_arguments(query: str, top_n: int) -> None:
    """Validate the arguments without modifying the user's query."""
    if not query.strip():
        raise ValueError("query 不能为空。")
    if len(query) > MAX_QUERY_LENGTH:
        raise ValueError(
            f"query 长度为 {len(query)}，超过工具允许的 {MAX_QUERY_LENGTH} 个字符；"
            "不能截断或改写用户原始问题。"
        )
    if not 1 <= top_n <= MAX_TOP_N:
        raise ValueError(f"topN 必须在 1 到 {MAX_TOP_N} 之间。")


def build_tool_request(query: str, top_n: int) -> dict[str, Any]:
    """Call the MCP endpoint and return its validated JSON response."""
    validate_arguments(query, top_n)
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/call",
        "params": {
            "name": TOOL_NAME,
            "arguments": {"query": query, "topN": top_n},
        },
    }
    headers = {
        "Accept": "application/json, text/event-stream",
        "Content-Type": "application/json",
    }

    try:
        response = requests.post(
            MCP_URL,
            headers=headers,
            json=payload,
            timeout=REQUEST_TIMEOUT,
        )
    except requests.RequestException as error:
        raise RuntimeError(f"MCP 请求失败: {error}") from error

    if response.status_code != 200:
        if response.status_code in (401, 403):
            raise RuntimeError(
                f"MCP 服务拒绝访问，HTTP 状态码: {response.status_code}。"
            )
        raise RuntimeError(
            f"MCP HTTP 错误 {response.status_code}: {response.text}"
        )

    try:
        result = response.json()
    except ValueError as error:
        raise RuntimeError(f"MCP 响应不是有效的 JSON: {response.text}") from error

    if isinstance(result, dict) and "error" in result:
        raise RuntimeError(f"MCP 工具错误: {format_result(result['error'])}")

    return result


def format_result(result: Any) -> str:
    """Serialize a host-provided MCP result without inventing fields."""
    return json.dumps(result, ensure_ascii=False, indent=2)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="校验参数并调用 searchAcademicLiterature MCP 工具。"
    )
    parser.add_argument("query", help="用户原始问题或检索关键词，不会被改写")
    parser.add_argument(
        "--topN",
        "--topn",
        dest="top_n",
        type=int,
        default=DEFAULT_TOP_N,
        help=f"返回数量，范围 1-{MAX_TOP_N}，默认 {DEFAULT_TOP_N}",
    )
    parser.add_argument(
        "--result",
        help="可选：将宿主返回的 JSON 结果传入并原样格式化输出",
    )
    args = parser.parse_args()

    try:
        result = build_tool_request(args.query, args.top_n)
    except (ValueError, RuntimeError) as error:
        print(str(error), file=sys.stderr)
        return 2

    if args.result:
        try:
            result = json.loads(args.result)
        except json.JSONDecodeError as error:
            print(f"结果不是有效的 JSON: {error}", file=sys.stderr)
            return 2
        if isinstance(result, dict) and result.get("results") == []:
            print("工具调用成功，但本次检索未返回相关文献。", file=sys.stderr)

    print(format_result(result))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())