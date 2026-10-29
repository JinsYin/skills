package com.example.product;

import java.util.List;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
public class ProductController {
    private final ProductRepository repository;

    public ProductController(ProductRepository repository) {
        this.repository = repository;
    }

    // Product list: GET /api/products
    @GetMapping("/api/products")
    public List<Product> list() {
        return repository.findAll();
    }
}
