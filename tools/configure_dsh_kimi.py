# AWIS: popup to configure the Moonshot/Kimi API key for dsh-tui's llm-chat MCP.
# Writes into ~/.dsh/profiles/dsh-tui/cordis.patch.yml (placeholder replacement),
# never echoes the key to the terminal. Pure stdlib (tkinter).
from __future__ import annotations

import re
import shutil
import subprocess
import sys
import tkinter as tk
from pathlib import Path
from tkinter import messagebox

PATCH = Path.home() / ".dsh" / "profiles" / "dsh-tui" / "cordis.patch.yml"
PLACEHOLDER = "填你的-Moonshot-key"


def _find_dsh() -> str | None:
    """Resolve the dsh executable; on Windows npm installs dsh.CMD which
    CreateProcess needs explicitly (bare 'dsh' is a POSIX shim script)."""
    return shutil.which("dsh")


def current_key(text: str) -> str:
    m = re.search(r"LLM_API_KEY:\s*'([^']*)'", text)
    return m.group(1) if m else ""


def apply_key(new_key: str) -> tuple[bool, str]:
    if not PATCH.exists():
        return False, f"找不到配置文件:\n{PATCH}"
    text = PATCH.read_text(encoding="utf-8")
    if "mcp-awis-llm-chat" not in text:
        return False, "配置文件里没有 mcp-awis-llm-chat 条目"
    new_text, n = re.subn(
        r"LLM_API_KEY:\s*'[^']*'", f"LLM_API_KEY: '{new_key}'", text, count=1
    )
    if n == 0:
        return False, "配置文件里找不到 LLM_API_KEY 行"
    PATCH.write_text(new_text, encoding="utf-8", newline="\n")
    # 校验补丁仍可被 dsh 解析
    dsh = _find_dsh()
    if dsh is None:
        return False, "已写入，但找不到 dsh 命令（未安装或不在 PATH）"
    try:
        r = subprocess.run(
            [dsh, "--profile", "dsh-tui", "--dump-config"],
            capture_output=True, text=True, timeout=60,
        )
        if r.returncode != 0:
            return False, f"已写入，但 dsh --dump-config 校验失败:\n{r.stderr[-300:]}"
    except (OSError, subprocess.TimeoutExpired) as exc:
        return False, f"已写入，但无法运行 dsh 校验: {exc}"
    return True, "配置成功"


def main() -> None:
    root = tk.Tk()
    root.title("AWIS · dsh-tui 评审配置")
    root.attributes("-topmost", True)
    root.resizable(False, False)

    text = PATCH.read_text(encoding="utf-8") if PATCH.exists() else ""
    existing = current_key(text)
    already_set = bool(existing) and existing != PLACEHOLDER

    pad = {"padx": 16, "pady": 6}
    tk.Label(
        root,
        text="为 dsh-tui 配置跨模型评审（llm-chat → Moonshot/Kimi API）",
        font=("Segoe UI", 11, "bold"),
    ).grid(row=0, column=0, columnspan=2, sticky="w", **pad)
    tk.Label(
        root,
        text="dsh 是 DeepSeek 系执行器，评审必须走 Kimi（异家族），\n"
             "key 只会写入本机 cordis.patch.yml，不会外传。",
        justify="left", fg="#555",
    ).grid(row=1, column=0, columnspan=2, sticky="w", **pad)

    if already_set:
        tk.Label(
            root,
            text=f"当前已配置: {existing[:6]}****（重新输入将覆盖）",
            fg="#2E7D32",
        ).grid(row=2, column=0, columnspan=2, sticky="w", **pad)

    tk.Label(root, text="Moonshot API Key:").grid(row=3, column=0, sticky="e", **pad)
    key_var = tk.StringVar()
    entry = tk.Entry(root, textvariable=key_var, width=42, show="•")
    entry.grid(row=3, column=1, sticky="w", **pad)
    entry.focus_set()

    show_var = tk.BooleanVar(value=False)

    def toggle_show() -> None:
        entry.config(show="" if show_var.get() else "•")

    tk.Checkbutton(root, text="显示", variable=show_var,
                   command=toggle_show).grid(row=4, column=1, sticky="w")

    status_var = tk.StringVar(value="")
    tk.Label(root, textvariable=status_var, fg="#B71C1C",
             wraplength=420, justify="left").grid(
        row=6, column=0, columnspan=2, sticky="w", **pad)

    def on_ok() -> None:
        key = key_var.get().strip()
        if not key:
            status_var.set("请输入 API key")
            return
        if key == PLACEHOLDER:
            status_var.set("不能仍是占位符")
            return
        ok, msg = apply_key(key)
        if ok:
            messagebox.showinfo(
                "AWIS",
                "已写入 cordis.patch.yml 并通过 dsh 解析校验。\n"
                "dsh-tui 里的 /night-shift 现在可以用 llm-chat(Kimi) 做跨模型评审了。",
                parent=root,
            )
            root.destroy()
        else:
            status_var.set(msg)

    btns = tk.Frame(root)
    btns.grid(row=5, column=0, columnspan=2, pady=10)
    tk.Button(btns, text="保存", width=12, command=on_ok,
              default="active").pack(side="left", padx=8)
    tk.Button(btns, text="取消", width=12,
              command=root.destroy).pack(side="left", padx=8)
    root.bind("<Return>", lambda _e: on_ok())
    root.bind("<Escape>", lambda _e: root.destroy())

    root.mainloop()


if __name__ == "__main__":
    sys.exit(main())
