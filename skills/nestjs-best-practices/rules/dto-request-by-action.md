---
title: Name Requests by action and enforce class-validator
impact: HIGH
tags: dto, request, validation
---

## Name Requests by action and enforce class-validator

Name bodies `{Name}{Action}Request`: `OrderCreateRequest`, `OrderUpdateRequest`. Create and update do not share a class — the required fields differ, and a shared class loosens both. Every constrained field has a `class-validator` decorator whose `message` is Chinese. The filter returns that message to the client (`envelope-factory-only`).

**Right:**

```ts
export class OrderCreateRequest {
  @ApiProperty({ description: '产品 ID', example: '1001' })
  @IsNotEmpty({ message: '产品 ID 不能为空' })
  productId!: string;

  @ApiProperty({ description: '数量', example: 2 })
  @IsInt({ message: '数量必须是整数' })
  @Min(1, { message: '数量必须大于等于 1' })
  @Max(999, { message: '数量必须小于等于 999' })
  quantity!: number;
}
```

Register one global pipe. `useGlobalPipes` in `main.ts` does not run in `@nestjs/testing`.

```ts
{ provide: APP_PIPE, useValue: new ValidationPipe({
  whitelist: true,
  forbidNonWhitelisted: true,
  transform: true,
})},
```

`whitelist` strips undeclared fields. `forbidNonWhitelisted` rejects them, so a typo is a 400 instead of a silently dropped update. Do not re-check null and range with `if` in the Controller.
