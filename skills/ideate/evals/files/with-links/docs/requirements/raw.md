# Relay 需求

- 项目名：Relay，一个面向内部团队的 Webhook 转发服务。
- 解决的问题：各业务系统各自对接第三方 Webhook，重复实现验签与重试；Relay 统一接收、验签并转发到内部服务。
- 目标用户：内部平台团队。
- 核心能力：接收第三方 Webhook 并验签；失败按指数退避重试，最多 5 次。
- 交付物：一个 Docker 镜像形式的服务，部署在 K8s。技术栈 Go。
- 调研：需要调研 Svix 的重试与签名机制，文档 https://docs.svix.com/retries 和 https://docs.svix.com/receiving/verifying-payloads/how ；也调研 Hookdeck 的事件过滤，文档 https://hookdeck.com/docs/filters 。两个对象的调研记录都写在 ../research/webhook-services.md 。
- 技术参考（仅参考，不是选型）：Standard Webhooks 规范 https://www.standardwebhooks.com/ ，参考它的签名头格式。
