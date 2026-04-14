# Use Cases

## 1. Configuration promotion
Promote a config change only if required keys remain present and rollback is proven.

## 2. Schema or version migration
Apply a version bump and verify post-change invariants before the change is allowed to stick.

## 3. Controlled CI gate
Run SafeChange inside CI so risky deploy steps either complete safely or fail closed with a receipt.

## 4. Production-adjacent automation
Wrap one rollback-sensitive automation step in a boundary decision with replayable records.
