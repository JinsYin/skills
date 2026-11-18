---
title: Map objects with MapStruct, never manual setters
impact: MEDIUM
tags: dto, mapstruct, converter
---

## Map objects with MapStruct, never manual setters

Map `Entity`, `Dto`, `Request`, and `Response` via MapStruct — never handwritten `setXxx(...)` chains, which compile cleanly when new fields are added and silently drop them at runtime.

Declare one `{Feature}Converter` per feature with `@Mapper(componentModel = "spring")`:

```java
@Mapper(componentModel = "spring")
public interface UserConverter {
    UserDetailResponse toResponse(UserEntity entity);
    List<UserListItemResponse> toListItems(List<UserEntity> entities);
    UserEntity toEntity(UserCreateRequest request);
    void updateEntity(@MappingTarget UserEntity entity, UserUpdateRequest request);
}
```

Declare explicit Converter methods for every conversion shape used — never assemble ad-hoc mappings inside Services.
