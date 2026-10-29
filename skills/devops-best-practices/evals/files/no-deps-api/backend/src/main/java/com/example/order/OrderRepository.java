package com.example.order;

import java.util.List;

public class OrderRepository {
    public List<String> findAll() {
        try { Thread.sleep(800); } catch (InterruptedException e) { Thread.currentThread().interrupt(); }
        return List.of("A-1", "A-2");
    }
}
