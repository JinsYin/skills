---
title: locations 构建期注入，未激活的 overlay 也要打进产物
impact: HIGH
impactDescription: 同镜像换形态部署时无法运行期覆盖，只能重新出包
tags: db, migration, flyway, build, deploy
---

## locations 构建期注入，未激活的 overlay 也要打进产物

Flyway 的 `spring.flyway.locations` 不要在配置文件里写死，用构建期 profile 注入占位符——哪套方言/形态由出包时决定，源码里保持单一写法。

```xml
<!-- 父 pom：每个 profile 注入自己的 locations -->
<profiles>
  <profile><id>gaussdb</id>      <!-- 分布式集群 -->
    <properties><spring.flyway.locations>classpath:db/migration/gauss-base,classpath:db/migration/gauss-distributed</spring.flyway.locations></properties>
  </profile>
  <profile><id>opengauss</id>    <!-- 单机 / 集中式 -->
    <properties><spring.flyway.locations>classpath:db/migration/gauss-base,classpath:db/migration/gauss-centralized</spring.flyway.locations></properties>
  </profile>
</profiles>
```

```yaml
# application.yml
spring:
  flyway:
    locations: "@spring.flyway.locations@"
```

**关键一条：注入的是「激活哪些 location」，不是「打包哪些文件」。** 所有 overlay 目录都在 `src/main/resources` 下，无论当次构建激不激活，都会一并进 jar 的 classpath。这不是冗余，而是运行期覆盖的前提：

**错误（按 profile 裁剪资源目录）：**

```xml
<!-- ❌ 只把激活的 overlay 打进包 -->
<resources><resource>
  <directory>src/main/resources</directory>
  <excludes><exclude>db/migration/gauss-centralized/**</exclude></excludes>
</resource></resources>
```

这样一来，同一个镜像换个形态的环境就跑不了，只能为该环境单独出一次包——而重新出包意味着上线的不是已经过测的那个产物。

**正确：全部打进去，部署时用环境变量覆盖。**

```bash
# 该环境形态与构建期 profile 不一致时，运行期改激活的 location 即可
SPRING_FLYWAY_LOCATIONS=classpath:db/migration/gauss-base,classpath:db/migration/gauss-centralized
```

典型场景：预发与生产用同一镜像，但预发是集中式主备、生产是分布式集群。构建期只能选一个 profile，差异靠部署清单里的这个 env 补齐。
