---
title: Snowflake IDs as bigint columns in bigint mode, strings on the wire
impact: CRITICAL
impactDescription: mode 'number' corrupts IDs above 2^53; raw bigint crashes JSON.stringify
tags: orm, drizzle, primary-key, snowflake, bigint, json
---

## Snowflake IDs as bigint columns in bigint mode, strings on the wire

Generate primary keys in one `IdGenerator` provider (Snowflake, worker id from config, unique per process). Declare them `bigint('id', { mode: 'bigint' }).primaryKey()`. Do not use `serial`, `bigserial`, `identity`, or `uuid().defaultRandom()` — the last one emits `gen_random_uuid()`, which Gauss does not have (see `db-gauss-dialect`).

Two silent failures:

- `mode: 'number'` rounds values above `Number.MAX_SAFE_INTEGER` (2^53 − 1). Two ids collapse into one row lookup.
- A `bigint` that reaches `JSON.stringify` throws `TypeError: Do not know how to serialize a BigInt`, so the response becomes 500.

Keep `bigint` inside Repository and Service. Every Request, Response, and JWT claim uses a decimal `string`, converted in the Converter. Parse path params with one pipe.

**Wrong:**

```ts
export const userTable = pgTable('t_user', {
  id: serial('id').primaryKey(),
  orgId: bigint('org_id', { mode: 'number' }).notNull(),
});
```

**Right:**

```ts
export const userTable = pgTable('t_user', {
  id: bigint('id', { mode: 'bigint' }).primaryKey(),
  orgId: bigint('org_id', { mode: 'bigint' }).notNull(),
});

await this.txHost.tx.insert(userTable).values({
  id: this.ids.next(),
  ...values,
});

// Converter
id: row.id.toString(),
```

```ts
@Injectable()
export class ParseSnowflakePipe implements PipeTransform<string, bigint> {
  transform(value: string): bigint {
    if (!/^[0-9]{1,19}$/.test(value)) throw new BizException(ErrorCode.BAD_REQUEST);
    return BigInt(value);
  }
}
```

Leave `BigInt.prototype.toJSON` unset so a leaked bigint still throws. An external business key uses the same `bigint` or `varchar` column with no generator — the caller passes it in.
