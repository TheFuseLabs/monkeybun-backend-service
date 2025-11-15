# Market API Testing

## POST /market - Create Market

```json
{
  "market_name": "Summer Artisan Market",
  "contact_first_name": "Jane",
  "contact_last_name": "Smith",
  "email": "jane@summermarket.com",
  "phone": "+1234567890",
  "google_place_id": "ChIJN1t_tDeuEmsRUsoyG83frY4",
  "location_text": "Central Park, New York",
  "aesthetic": "Boho-chic, vintage, handmade",
  "market_size": "50-100 vendors",
  "target_vendors": "Artisans, crafters, local makers",
  "optional_rules": "No pets allowed. Bring your own bags.",
  "contract_url": "https://example.com/contract.pdf",
  "description": "A vibrant summer market featuring local artisans and crafters",
  "start_date": "2024-06-01",
  "end_date": "2024-08-31",
  "application_deadline": "2024-05-15T23:59:59Z",
  "is_published": false,
  "email_package_url": "https://example.com/email-package.pdf",
  "payment_instructions": "Payment via bank transfer or PayPal",
  "application_form": {
    "questions": [
      {
        "id": "q1",
        "type": "text",
        "label": "Tell us about your products and what makes them unique",
        "required": true,
        "placeholder": "Describe your products..."
      },
      {
        "id": "q2",
        "type": "single_choice",
        "label": "What category best describes your products?",
        "required": true,
        "options": [
          "Jewelry & Accessories",
          "Home & Decor",
          "Art & Prints",
          "Clothing & Apparel",
          "Food & Beverages",
          "Other"
        ]
      },
      {
        "id": "q3",
        "type": "multiple_choice",
        "label": "Which days can you attend? (Select all that apply)",
        "required": false,
        "options": ["Friday", "Saturday", "Sunday", "All three days"]
      }
    ]
  },
  "logo_url": "https://nojdwshibrejmzwdoptq.storage.supabase.co/storage/v1/s3/monkeybun-storage/market/236f7430-7fa0-44f5-81bc-96c6bf77dcd3.jpeg",
  "image_urls": [
    "https://nojdwshibrejmzwdoptq.storage.supabase.co/storage/v1/s3/monkeybun-storage/market/74dcc4e6-40bc-4d37-8dd4-3e03bf421e4b.jpeg",
    "https://nojdwshibrejmzwdoptq.storage.supabase.co/storage/v1/s3/monkeybun-storage/market/b763bc3e-584e-404b-9002-2e83f275603a.jpeg",
    "https://nojdwshibrejmzwdoptq.storage.supabase.co/storage/v1/s3/monkeybun-storage/market/caaf4632-58bb-420f-8996-a45101d00b20.jpeg",
    "https://nojdwshibrejmzwdoptq.storage.supabase.co/storage/v1/s3/monkeybun-storage/market/3be983e8-9046-41ef-a45c-5bb943024ec3.jpeg"
  ]
}
```

**Note:** All fields except `phone`, `aesthetic`, `target_vendors`, `optional_rules`, `contract_url`, `email_package_url`, `logo_url`, and `image_urls` are required.

---

## GET /market/{market_id} - Get Market

No request body. Use path parameter: `{market_id}` (UUID)

**Example:** `GET /market/123e4567-e89b-12d3-a456-426614174000`

---

## GET /market - Search Markets

No request body. Use query parameters:

**Query Parameters:**

- `city` (optional, string): Filter by city
- `country` (optional, string): Filter by country
- `is_published` (optional, boolean): Filter by published status
- `start_date_from` (optional, string, ISO date): Filter markets starting from this date
- `start_date_to` (optional, string, ISO date): Filter markets starting until this date
- `end_date_from` (optional, string, ISO date): Filter markets ending from this date
- `end_date_to` (optional, string, ISO date): Filter markets ending until this date
- `latitude` (optional, float): Latitude for location-based search
- `longitude` (optional, float): Longitude for location-based search
- `radius_km` (optional, float, 0-1000): Radius in kilometers for location-based search
- `limit` (optional, int, 1-100, default: 20): Number of results per page
- `offset` (optional, int, >=0, default: 0): Pagination offset

**Example:**

```
GET /market?city=New York&is_published=true&limit=10&offset=0
GET /market?latitude=40.7128&longitude=-74.0060&radius_km=50&limit=20
GET /market?start_date_from=2024-06-01&end_date_to=2024-08-31
```

---

## PUT /market/{market_id} - Update Market

All fields are optional. Only include fields you want to update.

```json
{
  "market_name": "Updated Market Name",
  "description": "Updated description",
  "is_published": true,
  "image_urls": [
    "https://example.com/image1.jpg",
    "https://example.com/image2.jpg"
  ],
  "logo_url": "https://example.com/logo.jpg"
}
```

**Minimal example (updating only one field):**

```json
{
  "is_published": true
}
```

**Full example (all fields):**

```json
{
  "market_name": "Winter Artisan Market",
  "contact_first_name": "John",
  "contact_last_name": "Doe",
  "email": "john@wintermarket.com",
  "phone": "+1987654321",
  "google_place_id": "ChIJN1t_tDeuEmsRUsoyG83frY4",
  "location_text": "Times Square, New York",
  "aesthetic": "Modern, minimalist",
  "market_size": "100-200 vendors",
  "target_vendors": "Local businesses",
  "optional_rules": "No smoking",
  "contract_url": "https://example.com/new-contract.pdf",
  "description": "Updated market description",
  "start_date": "2024-12-01",
  "end_date": "2024-12-31",
  "application_deadline": "2024-11-15T23:59:59Z",
  "is_published": true,
  "email_package_url": "https://example.com/new-email-package.pdf",
  "payment_instructions": "Payment via credit card only",
  "application_form": {
    "questions": [
      {
        "id": "q1",
        "type": "text",
        "label": "Tell us about your business",
        "required": true
      }
    ]
  },
  "logo_url": "https://example.com/new-logo.jpg",
  "image_urls": [
    "https://example.com/image1.jpg",
    "https://example.com/image2.jpg"
  ]
}
```

---

## DELETE /market/{market_id} - Delete Market

No request body. Use path parameter: `{market_id}` (UUID)

**Example:** `DELETE /market/123e4567-e89b-12d3-a456-426614174000`

---

## PUT /market/{market_id}/images/{image_id} - Update Market Image

```json
{
  "caption": "Updated image caption",
  "sort_order": 2
}
```

**Update only caption:**

```json
{
  "caption": "Main market entrance"
}
```

**Update only sort order:**

```json
{
  "sort_order": 0
}
```

**Note:** Both fields are optional. Include only the fields you want to update.

---

## DELETE /market/{market_id}/images/{image_id} - Delete Market Image

No request body. Use path parameters:

- `{market_id}` (UUID): Market ID
- `{image_id}` (UUID): Image ID

**Example:** `DELETE /market/123e4567-e89b-12d3-a456-426614174000/images/987fcdeb-51a2-43d7-b123-456789abcdef`

---

# Business API Testing

## POST /business - Create Business

```json
{
  "shop_name": "Artisan Jewelry Co",
  "email": "contact@artisanjewelry.com",
  "phone": "+1234567890",
  "website_url": "https://www.artisanjewelry.com",
  "instagram_handle": "@artisanjewelry",
  "tiktok_handle": "@artisanjewelry",
  "twitter_handle": "@artisanjewelry",
  "facebook_handle": "artisanjewelry",
  "category": "Jewelry & Accessories",
  "average_price_range": "$50-$200",
  "description": "Handcrafted artisan jewelry featuring unique designs and sustainable materials",
  "logo_url": "https://nojdwshibrejmzwdoptq.storage.supabase.co/storage/v1/s3/monkeybun-storage/business/236f7430-7fa0-44f5-81bc-96c6bf77dcd3.jpeg",
  "image_urls": [
    "https://nojdwshibrejmzwdoptq.storage.supabase.co/storage/v1/s3/monkeybun-storage/business/74dcc4e6-40bc-4d37-8dd4-3e03bf421e4b.jpeg",
    "https://nojdwshibrejmzwdoptq.storage.supabase.co/storage/v1/s3/monkeybun-storage/business/b763bc3e-584e-404b-9002-2e83f275603a.jpeg",
    "https://nojdwshibrejmzwdoptq.storage.supabase.co/storage/v1/s3/monkeybun-storage/business/caaf4632-58bb-420f-8996-a45101d00b20.jpeg"
  ]
}
```

**Minimal example (only required field):**

```json
{
  "shop_name": "My Shop"
}
```

**Note:** Only `shop_name` is required. Optional fields include: `phone`, `website_url`, `instagram_handle`, `tiktok_handle`, `twitter_handle`, `facebook_handle`, and `logo_url`.

---

## GET /business/{business_id} - Get Business

No request body. Use path parameter: `{business_id}` (UUID)

**Example:** `GET /business/123e4567-e89b-12d3-a456-426614174000`

---

## GET /business - Search Businesses

No request body. Use query parameters:

**Query Parameters:**

- `category` (optional, string): Filter by category
- `limit` (optional, int, 1-100, default: 20): Number of results per page
- `offset` (optional, int, >=0, default: 0): Pagination offset

**Example:**

```
GET /business?category=Jewelry&limit=10&offset=0
GET /business?category=Home%20%26%20Decor&limit=20
GET /business?limit=50&offset=20
```

---

## PUT /business/{business_id} - Update Business

All fields are optional. Only include fields you want to update.

```json
{
  "shop_name": "Updated Shop Name",
  "description": "Updated description",
  "category": "Updated Category",
  "image_urls": [
    "https://example.com/image1.jpg",
    "https://example.com/image2.jpg"
  ],
  "logo_url": "https://example.com/logo.jpg"
}
```

**Minimal example (updating only one field):**

```json
{
  "shop_name": "New Shop Name"
}
```

**Full example (all fields):**

```json
{
  "shop_name": "Premium Artisan Jewelry",
  "email": "newemail@artisanjewelry.com",
  "phone": "+1987654321",
  "website_url": "https://www.newartisanjewelry.com",
  "instagram_handle": "@newartisanjewelry",
  "tiktok_handle": "@newartisanjewelry",
  "twitter_handle": "@newartisanjewelry",
  "facebook_handle": "newartisanjewelry",
  "category": "Luxury Jewelry",
  "average_price_range": "$200-$500",
  "description": "Updated description for premium artisan jewelry",
  "logo_url": "https://example.com/new-logo.jpg",
  "image_urls": [
    "https://example.com/image1.jpg",
    "https://example.com/image2.jpg",
    "https://example.com/image3.jpg"
  ]
}
```

---

## DELETE /business/{business_id} - Delete Business

No request body. Use path parameter: `{business_id}` (UUID)

**Example:** `DELETE /business/123e4567-e89b-12d3-a456-426614174000`

---

## PUT /business/{business_id}/images/{image_id} - Update Business Image

```json
{
  "caption": "Updated image caption",
  "sort_order": 2
}
```

**Update only caption:**

```json
{
  "caption": "Featured product showcase"
}
```

**Update only sort order:**

```json
{
  "sort_order": 0
}
```

**Note:** Both fields are optional. Include only the fields you want to update.

---

## DELETE /business/{business_id}/images/{image_id} - Delete Business Image

No request body. Use path parameters:

- `{business_id}` (UUID): Business ID
- `{image_id}` (UUID): Image ID

**Example:** `DELETE /business/123e4567-e89b-12d3-a456-426614174000/images/987fcdeb-51a2-43d7-b123-456789abcdef`
