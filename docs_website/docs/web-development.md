# Web Development

Web endpoints in Mamba are first-class language constructs. You do not need to import a framework to spin up a high-performance web server.

## Defining Routes

Use the `route` keyword to declare HTTP endpoints. All routes automatically inject a `req` (Request) context object.

### GET Requests
```mamba
route GET "/api/user" {
    return json.stringify({
        "name": "Alex"
    })
}
```

### POST Requests
```mamba
route POST "/api/users" {
    let body = req.body()
    let user = json.parse(body)

    return json.stringify({
        "status": "created",
        "user": user["name"]
    })
}
```

## The Request Object (`req`)

Mamba exposes incoming HTTP request data via the native `req` object.

### Query Parameters
Access URL query strings (e.g., `?search=mamba`).
```mamba
let search_term = req.query("search")
```

### Headers
Read HTTP headers.
```mamba
let auth = req.header("Authorization")
```

### Body Payload
Access raw request bodies for POST/PUT endpoints.
```mamba
let raw_body = req.body()
```

## Supported HTTP Methods
Mamba's native router supports:
- `GET`
- `POST`
- `PUT`
- `DELETE`
- `OPTIONS` (Handled automatically with `Access-Control-Allow-Origin: *` for CORS support)
