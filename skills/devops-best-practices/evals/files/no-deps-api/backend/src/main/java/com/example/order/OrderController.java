package com.example.order;

import java.util.List;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
public class OrderController {
    private final OrderRepository repository = new OrderRepository();

    // Slow query: simulates downstream latency
    @GetMapping("/api/orders")
    public List<String> list() {
        return repository.findAll();
    }
}
