---
title: Run use-case transactions through CLS, and query only via txHost.tx
impact: CRITICAL
impactDescription: A repository that injects the root client commits before the use case finishes
tags: orm, drizzle, transaction, cls
---

## Run use-case transactions through CLS, and query only via txHost.tx

Open transactions with `@Transactional()` from `@nestjs-cls/transactional` on the Service method. Repositories inject `TransactionHost` and call `txHost.tx` only. A Repository that injects the root Drizzle client ignores the CLS transaction and commits its statement on its own.

Register the plugin once:

```ts
ClsModule.forRoot({
  plugins: [
    new ClsPluginTransactional({
      imports: [DbModule],
      adapter: new TransactionalAdapterDrizzleOrm({ drizzleInstanceToken: DRIZZLE }),
    }),
  ],
}),
```

```ts
type AppTxAdapter = TransactionalAdapterDrizzleOrm<AppDatabase>;

@Injectable()
export class OrderService {
  constructor(
    private readonly orders: OrderRepository,
    private readonly payments: PaymentService,
  ) {}

  @Transactional<AppTxAdapter>()
  async place(input: PlaceOrderDto) {
    const order = await this.orders.insert(input);
    await this.payments.reserve(order.id); // same transaction if it also uses txHost.tx
    return order;
  }
}
```

```ts
constructor(private readonly txHost: TransactionHost<AppTxAdapter>) {}

async insert(input: PlaceOrderDto) {
  return this.txHost.tx.insert(orderTable).values(/* ... */).returning();
}
```

With no transaction active, `txHost.tx` is the root client (adapter behavior since transactional 3). Repositories inject `TransactionHost` only, and they query through `txHost.tx` rather than `db.transaction()`. Nested `@Transactional()` joins the current transaction (default propagation). node-postgres is async: leave `transactionMode` unset.
