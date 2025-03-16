```mermaid
erDiagram
    USER {
        int id
        string first_name
        string last_name
        string email
        string password
        boolean is_admin
    }

    PLACE {
        int id
        string title
        string description
        float price
        float latitude
        float longitude
        int owner_id
    }

    REVIEW {
        int id
        string text
        int rating
        int user_id
        int place_id
    }

    AMENITY {
        int id
        string name
    }

    PLACE_AMENITY {
        int place_id
        int amenity_id
    }

    USER ||--o{ PLACE : owns
    USER ||--o{ REVIEW : writes
    PLACE ||--o{ REVIEW : has
    PLACE ||--o{ PLACE_AMENITY : has
    AMENITY ||--o{ PLACE_AMENITY : belongs_to
```
