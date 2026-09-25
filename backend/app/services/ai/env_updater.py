import os
from pathlib import Path
from app.config import get_settings


def update_env_file(updates: dict[str, str], env_path: Path | None = None) -> None:
    if env_path is None:
        env_path = Path(".env")
    
    if not env_path.exists():
        env_path.write_text("", encoding="utf-8")
        
    content = env_path.read_text(encoding="utf-8")
    lines = content.splitlines()
    new_lines = []
    keys_updated = set()

    for line in lines:
        stripped = line.strip()
        if stripped and not stripped.startswith("#") and "=" in stripped:
            k, _ = stripped.split("=", 1)
            k = k.strip()
            if k in updates:
                new_lines.append(f"{k}={updates[k]}")
                keys_updated.add(k)
                continue
        new_lines.append(line)

    for k, v in updates.items():
        if k not in keys_updated:
            new_lines.append(f"{k}={v}")

    env_path.write_text("\n".join(new_lines) + "\n", encoding="utf-8")

    # Update current process environment
    for k, v in updates.items():
        os.environ[k] = v

    # Clear Pydantic lru_cache for settings
    get_settings.cache_clear()
