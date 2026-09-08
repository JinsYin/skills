#!/usr/bin/env bash
set -euo pipefail

expected_model="cursor-grok-4.6-xhigh"
hook_input="$(cat)"
actual_model="$(jq -r '.subagent_model // empty' <<<"$hook_input")"

if [[ "$actual_model" != "$expected_model" ]]; then
  jq -n \
    --arg expected "$expected_model" \
    --arg actual "${actual_model:-<missing>}" \
    '{permission: "deny", user_message: ("Subagent model must be " + $expected + "; got " + $actual)}'
  exit 0
fi

printf '%s\n' '{"permission":"allow"}'
