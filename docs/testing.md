# Market API Testing

## POST /market - Create Market

```json
{
  "market_name": "Summer Artisan Market",
  "contact_first_name": "Jane",
  "contact_last_name": "Smith",
  "email": "aryankhurana1511@gmail.com",
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
  "is_published": true,
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
  "logo_url": "https://nojdwshibrejmzwdoptq.storage.supabase.co/storage/v1/s3/monkeybun-public/market/c253e630-3969-4b3e-99ee-c5af5bf1e4cf.jpeg",
  "image_urls": [
    "https://nojdwshibrejmzwdoptq.storage.supabase.co/storage/v1/s3/monkeybun-public/market/0ad0ee38-e0c1-4c7f-ae9b-bad7ae6337e8.jpeg",
    "https://nojdwshibrejmzwdoptq.storage.supabase.co/storage/v1/s3/monkeybun-public/market/1673cebc-b07a-42f4-9613-777dc84da424.jpeg",
    "https://nojdwshibrejmzwdoptq.storage.supabase.co/storage/v1/s3/monkeybun-public/market/c6adfcfd-0331-4ffe-b5ed-d52e37e9f64b.jpeg",
    "https://nojdwshibrejmzwdoptq.storage.supabase.co/storage/v1/s3/monkeybun-public/market/612bdf16-7c5a-40be-9c20-d06767c2dbaa.jpeg"
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
  "logo_url": "https://nojdwshibrejmzwdoptq.storage.supabase.co/storage/v1/s3/monkeybun-public/market/c253e630-3969-4b3e-99ee-c5af5bf1e4cf.jpeg",
  "image_urls": [
    "https://nojdwshibrejmzwdoptq.storage.supabase.co/storage/v1/s3/monkeybun-public/market/0ad0ee38-e0c1-4c7f-ae9b-bad7ae6337e8.jpeg",
    "https://nojdwshibrejmzwdoptq.storage.supabase.co/storage/v1/s3/monkeybun-public/market/1673cebc-b07a-42f4-9613-777dc84da424.jpeg",
    "https://nojdwshibrejmzwdoptq.storage.supabase.co/storage/v1/s3/monkeybun-public/market/c6adfcfd-0331-4ffe-b5ed-d52e37e9f64b.jpeg"
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

---

# Application API Testing

## POST /application - Create Application

Apply to a market with your business. The `answers` field should match the questions in the market's `application_form`.

```json
{
  "market_id": "123e4567-e89b-12d3-a456-426614174000",
  "business_id": "987fcdeb-51a2-43d7-b123-456789abcdef",
  "answers": {
    "q1": "Our products are handcrafted using sustainable materials and traditional techniques passed down through generations.",
    "q2": "Jewelry & Accessories",
    "q3": ["Friday", "Saturday", "Sunday"]
  }
}
```

**Important:** Replace the UUIDs above with actual UUIDs from your database:

- `market_id`: The UUID of an existing market
- `business_id`: The UUID of an existing business that you own

**If using Postman/Insomnia variables:**

```json
{
  "market_id": "{{marketId}}",
  "business_id": "{{businessId}}",
  "answers": {
    "q1": "Our products are handcrafted using sustainable materials and traditional techniques passed down through generations.",
    "q2": "Jewelry & Accessories",
    "q3": ["Friday", "Saturday", "Sunday"]
  }
}
```

Make sure your variables are set as strings (UUIDs) in your testing tool, not as template syntax that gets evaluated incorrectly.

**Minimal example (no answers):**

```json
{
  "market_id": "123e4567-e89b-12d3-a456-426614174000",
  "business_id": "987fcdeb-51a2-43d7-b123-456789abcdef"
}
```

**Note:**

- Both `market_id` and `business_id` are required (UUIDs)
- `answers` is optional, but if provided, it must match the structure of the market's `application_form`
- Required questions in the application form must be answered
- Single choice questions must have a value from the options list
- Multiple choice questions must be an array of values from the options list
- You must own the business to create an application
- You cannot create duplicate applications for the same market and business

**Answer format examples:**

For a text question:

```json
{
  "q1": "Your answer text here"
}
```

For a single_choice question:

```json
{
  "q2": "Jewelry & Accessories"
}
```

For a multiple_choice question:

```json
{
  "q3": ["Friday", "Saturday"]
}
```

---

## GET /application/{application_id} - Get Application

No request body. Use path parameter: `{application_id}` (UUID)

**Example:** `GET /application/123e4567-e89b-12d3-a456-426614174000`

**Note:** You can view an application if:

- You own the business that created the application, OR
- You are the organizer of the market the application is for

---

## GET /application - Search Applications

No request body. Use query parameters:

**Query Parameters:**

- `market_id` (optional, UUID): Filter by market ID (requires market organizer access)
- `business_id` (optional, UUID): Filter by business ID (requires business owner access)
- `status` (optional, string): Filter by status - one of: `applied`, `accepted`, `declined`, `confirmed`
- `limit` (optional, int, 1-100, default: 20): Number of results per page
- `offset` (optional, int, >=0, default: 0): Pagination offset

**Note:** You must provide either `market_id` OR `business_id` (at least one is required)

**Examples:**

Get all applications for a business:

```
GET /application?business_id=987fcdeb-51a2-43d7-b123-456789abcdef
```

Get all applications for a market:

```
GET /application?market_id=123e4567-e89b-12d3-a456-426614174000
```

Get applications with status filter:

```
GET /application?business_id=987fcdeb-51a2-43d7-b123-456789abcdef&status=accepted
GET /application?market_id=123e4567-e89b-12d3-a456-426614174000&status=applied
```

Get applications with pagination:

```
GET /application?market_id=123e4567-e89b-12d3-a456-426614174000&limit=10&offset=0
```

**Authorization:**

- If filtering by `business_id`: You must own the business
- If filtering by `market_id`: You must be the market organizer

---

## GET /application/market/{market_id} - Get Applications for Market

No request body. Use path parameter: `{market_id}` (UUID) and optional query parameters:

**Query Parameters:**

- `status` (optional, string): Filter by status - one of: `applied`, `accepted`, `declined`, `confirmed`
- `limit` (optional, int, 1-100, default: 20): Number of results per page
- `offset` (optional, int, >=0, default: 0): Pagination offset

**Example:** `GET /application/market/123e4567-e89b-12d3-a456-426614174000`

**With filters:**

```
GET /application/market/123e4567-e89b-12d3-a456-426614174000?status=applied&limit=10&offset=0
GET /application/market/123e4567-e89b-12d3-a456-426614174000?status=accepted
```

**Note:** You must be the organizer of the market to view its applications.

---

## PUT /application/{application_id} - Update Application

All fields are optional. Only include fields you want to update.

**Update status:**

```json
{
  "status": "accepted"
}
```

**Update answers:**

```json
{
  "answers": {
    "q1": "Updated answer text",
    "q2": "Home & Decor",
    "q3": ["Saturday", "Sunday"]
  }
}
```

**Update notes and payment info:**

```json
{
  "notes_for_org": "Can provide additional setup assistance if needed",
  "payment_method": "bank_transfer",
  "payment_status": "pending"
}
```

**Note:** `payment_method` and `payment_status` are enums. See the payment update endpoint documentation for valid values. For updating payment information on accepted applications, it's recommended to use the dedicated `/payment` endpoint.

**Full example (all fields):**

```json
{
  "status": "confirmed",
  "notes_for_org": "Looking forward to participating!",
  "payment_method": "credit_card",
  "payment_status": "paid",
  "answers": {
    "q1": "Updated product description",
    "q2": "Art & Prints",
    "q3": ["All three days"]
  }
}
```

**Status values:**

- `applied` - Initial status when application is created
- `accepted` - Market organizer has accepted the application
- `declined` - Market organizer has declined the application
- `confirmed` - Business owner has confirmed participation

**Note:**

- You must own the business that created the application to update it
- When status changes, corresponding timestamp fields are automatically updated:
  - `accepted_at` when status changes to `accepted`
  - `declined_at` when status changes to `declined`
  - `confirmed_at` when status changes to `confirmed`
- If updating `answers`, they will be validated against the market's `application_form`

---

## DELETE /application/{application_id} - Delete Application

No request body. Use path parameter: `{application_id}` (UUID)

**Example:** `DELETE /application/123e4567-e89b-12d3-a456-426614174000`

**Note:** You must own the business that created the application to delete it.

---

## POST /application/{application_id}/accept - Accept Application

Market organizers can accept applications. This changes the status to `accepted` and sets the `accepted_at` timestamp.

**Request body:** Empty (or `{}`)

**Example:** `POST /application/123e4567-e89b-12d3-a456-426614174000/accept`

```json
{}
```

**Note:**

- Only the market organizer can accept applications for their market
- If the application is already accepted, an error will be returned
- When accepted, the `rejection_reason` field is cleared (set to null)

---

## POST /application/{application_id}/reject - Reject Application

Market organizers can reject applications with a reason. This changes the status to `declined`, sets the `declined_at` timestamp, and stores the rejection reason.

```json
{
  "rejection_reason": "We are looking for vendors with more experience in this category."
}
```

**Example:** `POST /application/123e4567-e89b-12d3-a456-426614174000/reject`

**Note:**

- Only the market organizer can reject applications for their market
- `rejection_reason` is required
- If the application is already declined, an error will be returned
- The rejection reason will be visible to the business owner when they view their applications

---

## GET /application/my-applications - Get My Applications

Get all applications for businesses owned by the current user. This is the "My Applications" view where users can see all their applications across all markets.

**Query Parameters:**

- `status` (optional, string): Filter by status - one of: `applied`, `accepted`, `declined`, `confirmed`
- `limit` (optional, int, 1-100, default: 20): Number of results per page
- `offset` (optional, int, >=0, default: 0): Pagination offset

**Examples:**

Get all my applications:

```
GET /application/my-applications
```

Get only rejected applications (to see rejection reasons):

```
GET /application/my-applications?status=declined
```

Get only accepted applications:

```
GET /application/my-applications?status=accepted
```

Get applications with pagination:

```
GET /application/my-applications?limit=10&offset=0
```

**Response includes:**

- All applications for businesses owned by the user
- `rejection_reason` field is included for declined applications
- Applications are ordered by creation date (newest first)

**Note:** This endpoint automatically filters applications to only show those for businesses owned by the authenticated user.

---

## PUT /application/{application_id}/payment - Update Payment

After an application is accepted, the business owner can update payment information. This is a manual process where the owner sets the payment method and payment status.

**Request body:**

```json
{
  "payment_method": "bank_transfer",
  "payment_status": "paid"
}
```

**Update only payment method:**

```json
{
  "payment_method": "credit_card"
}
```

**Update only payment status:**

```json
{
  "payment_status": "paid"
}
```

**Payment Method values:**

- `bank_transfer` - Bank transfer
- `credit_card` - Credit card
- `paypal` - PayPal
- `check` - Check
- `cash` - Cash
- `other` - Other payment method

**Payment Status values:**

- `pending` - Payment is pending
- `paid` - Payment has been completed
- `failed` - Payment failed
- `refunded` - Payment was refunded

**Example:** `PUT /application/123e4567-e89b-12d3-a456-426614174000/payment`

**Note:**

- Only the business owner can update payment information
- Payment can only be updated for applications with status `accepted`
- Both fields are optional - you can update just one or both
- Confirmation does not depend on payment status - the owner can confirm regardless of payment status

---

## POST /application/{application_id}/confirm - Confirm Application

After an application is accepted and payment is handled (manually), the business owner can confirm their participation. Confirmation does not require payment status to be "paid" - it's up to the owner's discretion.

**Request body:** Empty (or `{}`)

**Example:** `POST /application/123e4567-e89b-12d3-a456-426614174000/confirm`

```json
{}
```

**Note:**

- Only the business owner can confirm the application
- Only applications with status `accepted` can be confirmed
- Confirmation does not depend on payment status
- When confirmed, the status changes to `confirmed` and `confirmed_at` timestamp is set
- If the application is already confirmed, an error will be returned

**Typical workflow:**

1. Application is created (`applied` status)
2. Market organizer accepts application (`accepted` status)
3. Business owner updates payment information (payment method and status)
4. Business owner confirms participation (`confirmed` status)
