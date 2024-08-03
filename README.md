# ShortURL Project-First Version

## Overview
This project entails the creation of a state-of-the-art URL shortener service. The service allows users to shorten long URLs, retrieve original URLs from short URLs, and manage URL mappings efficiently. The backend leverages FastAPI, DynamoDB, and Docker on AWS for robust performance and scalability.

## Use Cases

1. **Redirect a Short URL to the Original URL**
   - Users can provide a valid short URL and be redirected to the corresponding original URL.

2. **Generate a Short URL from the Original URL**
   - Users submit a long URL, which the system shortens and returns as a short URL.

3. **List All Short URL and Original URL Pairs**
   - The system stores and allows retrieval of all short URL and original URL pairs.

4. **Handle Already Shortened URLs**
   - If a user submits an already shortened URL, the system will validate and inform the user accordingly.

5. **Deal with Extremely Long URLs**
   - The system will validate the length and format of very long URLs and inform the user if they exceed typical length limits.

## Functional Requirements

1. **Create Short URLs**
   - Securely generate and store short URLs for long URLs, ensuring no collisions.

2. **Get Original URL from a Short URL**
   - Redirect users from a short URL to the original URL.

3. **List All URL Pairs**
   - Store and retrieve all URL mappings.

4. **Edge Cases**
   - Handle shortening of already shortened URLs.
   - Manage extremely long URLs exceeding typical limits.

## Non-Functional Requirements

1. **Collision-Free Short URLs**
   - Ensure unique short URLs by regenerating in case of a collision.

2. **Secure URLs**
   - Shortened links should not be guessable.

3. **Performant Public APIs**
   - Ensure high availability and real-time URL redirection with minimal latency.

4. **Encoding and ID Generation**
   - Implement a hash function (e.g., base62) and use UUID for unique ID generation.

## Assumptions

1. The service will be accessed by fewer than 100 users.
2. Scalability is not a primary concern.
3. Short URLs do not need TTL (Time to Live) initially.

## Solution Design

### Architecture
- **Client**: A simple CLI developed in Python for user interaction.
- **Backend**: FastAPI web server handling HTTP requests and CRUD operations.
- **Database**: DynamoDB storing original and shortened URLs.

### Components

1. **CLI Program (Client)**
   - Input: Long URL
   - Process: Validate URL, check database, generate unique ID, convert to short URL, save mapping to DB.
   - Output: Short URL

2. **API Server (Backend)**
   - Handle API routes, perform CRUD operations on the database.

3. **DynamoDB (Database)**
   - Store mappings of original URLs and short URLs, ensuring persistence.

## API Endpoints

### POST /shorten_url
- **Description**: Shorten a given URL or bind to a provided custom short URL.
- **Input**: 
  - `url` (required): The original URL.
  - `short_url` (optional): A custom short URL.
- **Output**: 
  - `short_url`: The shortened URL.
  - `original_url`: The original URL.
- **Errors**:
  - Invalid URL format.
  - Short URL not available.

### GET /list_urls
- **Description**: Retrieve all shortened URLs and their corresponding original URLs.
- **Output**: List of URL mappings.
- **Errors**:
  - No URLs found.

### GET /redirect/{short_url}
- **Description**: Redirect to the original URL associated with the short URL.
- **Input**: 
  - `short_url`: The shortened URL.
- **Output**: Redirection to the original URL.
- **Errors**:
  - Short URL does not exist.

### POST /update_url
- **Description**: Modify the original URL associated with a short URL.
- **Input**: 
  - `new_long_url`: The new original URL.
  - `short_url`: The short URL.
- **Output**: 
  - `short_url`: The short URL.
  - `new_long_url`: The new original URL.
- **Errors**:
  - Short URL or old long URL does not exist.

## Data Format and Database Schema

### URL Table
| Key     | Value1     | Value2     | Value3      | Value4    |
|---------|------------|------------|-------------|-----------|
| ID      | short URL  | long URL   | expire_date | timestamp |

### URL Object
- **ID**: String
- **Short URL**: String
- **Original URL**: String
- **Expire Date**: Number (optional)
- **Timestamp**: String

## Testing

### Unit Tests
1. **Create Short URL**
   - **Positive Tests**:
     - No collisions, no custom URL.
     - With collisions, no custom URL.
     - No collisions, with custom URL.
   - **Negative Tests**:
     - With collisions, with custom URL.
     - Invalid long URL.

### Integration Tests
1. **Shorten URL and Verify Database Write**
   - **Positive Tests**:
     - No collisions, no custom URL.
     - With collisions, no custom URL.
     - No collisions, with custom URL.
   - **Negative Tests**:
     - Collision with custom URL.
     - New long URL with existing custom short URL.

## Workflow
1. **Shorten URL and Verify Database Write**
   - Submit long URL, receive short URL, verify DB entry.

2. **Access Shortened URL and Follow Redirection**
   - Access short URL, verify redirection to original URL.

3. **Handle Custom Short URL Collision**
   - Submit custom short URL that exists, receive error.

## Assumptions
- Less than 100 users.
- Scalability not a primary concern.
- No TTL required initially.
