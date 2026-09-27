#!/usr/bin/env bash
set -euo pipefail

# 升级模型时只改这里
model="grok-4.7"
effort="xhigh"
allowed_models=("${model}[effort=${effort}]" "cursor-${model}-${effort}")
log_file="$(cd "$(dirname "$0")" && pwd)/logs/enforce-subagent-model.log"
hook_input="$(cat)"

deny() {
  python3 -c 'import json, sys; print(json.dumps({"permission": "deny", "user_message": sys.argv[1]}))' "$1"
  exit 2
}

if [[ "${CURSOR_HOOK_DEBUG:-}" == "1" ]]; then
  mkdir -p "$(dirname "$log_file")"
  printf '%s %s\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$hook_input" >>"$log_file"
fi

if ! actual_model="$(python3 -c '
import json, sys
data = json.loads(sys.stdin.read())
print(data.get("subagent_model") or "<missing>")
' <<<"$hook_input" 2>/dev/null)"; then
  deny "Subagent hook input is not valid JSON"
fi

for allowed_model in "${allowed_models[@]}"; do
  if [[ "$actual_model" == "$allowed_model" ]]; then
    printf '%s\n' '{"permission":"allow"}'
    exit 0
  fi
done

deny "Subagent model must be ${allowed_models[0]} or ${allowed_models[1]}; got $actual_model"
