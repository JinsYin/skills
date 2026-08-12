---
title: 不写死本机路径，继承启动 shell 的环境
impact: MEDIUM
impactDescription: 写死的 JAVA_HOME 等路径换机器即失效，且该文件是入库的
tags: proc, process-compose, portability
---

## 不写死本机路径，继承启动 shell 的环境

`process-compose.yml` 是入库文件，会被所有人用。写死 `JAVA_HOME: ${HOME}/.sdkman/candidates/java/21.0.1` 之后，其他人克隆下来仍可能因安装方式或版本不同而跑不起来，而且修法是改一个入库文件——改完又会误提交回去。

process-compose 继承启动它的 shell 环境，因此**版本选择应该交给 shell**（sdkman / nvm / asdf / direnv），文件里只描述进程本身。

**错误：**

```yaml
processes:
  app:
    environment:
      - "JAVA_HOME=${HOME}/.sdkman/candidates/java/21.0.5-tem"
```

**正确（在文件头注释里声明前提，必要时用守护进程强制）：**

```yaml
# JDK 说明：后端进程要求 JDK 21，process-compose 继承启动它的 shell 环境，
#   请在 `process-compose up -D` 前确保当前 shell 的 JDK 为 21。
#   不写死 JAVA_HOME 以保持跨机器 / 跨安装方式可移植。
```

`environment` 里适合放的是**与本机无关的固定值**：功能开关、本地固定的弱密码、mock 服务的接入凭据。这些换机器不变，写进去反而消除了不确定性。

判据是一句话：**这一行换台机器还成立吗？** 不成立就不该出现在入库文件里。
