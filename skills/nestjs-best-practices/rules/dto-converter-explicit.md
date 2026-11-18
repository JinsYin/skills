---
title: Map with an explicit Converter return type
impact: HIGH
impactDescription: A cast or a spread hides a new required field until production
tags: dto, converter, mapping
---

## Map with an explicit Converter return type

One `{Name}Converter` per feature. Each method's return type is the destination class, and the method returns an object literal. TypeScript then errors when a required field is missing. A cast, a rest spread of the row, or `plainToInstance` without `excludeExtraneousValues` copies new columns (including `passwordHash`) the moment they appear on the table.

**Wrong:**

```ts
return row as unknown as UserDetailResponse; // ❌
return { ...row, id: row.id.toString() };    // ❌ extra columns ride along
```

**Right:**

```ts
@Injectable()
export class UserConverter {
  toDetail(row: UserRow): UserDetailResponse {
    return {
      id: row.id.toString(),
      name: row.name,
      createdAt: formatDateTime(row.createdAt),
    };
  }
}
```

Do not map ad hoc inside Services. A new view gets a new method.
