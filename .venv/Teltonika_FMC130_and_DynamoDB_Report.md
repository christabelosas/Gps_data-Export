
# 🛰️ Teltonika FMC130 & AVL Protocol Summary

## Overview of Teltonika FMC130
**Device Type:** Compact advanced GSM/GNSS tracker.  

**Main Capabilities:**
- Real-time tracking with high GNSS accuracy.
- Supports **4G LTE CAT1 fallback to 2G**.
- **Multiple input/output interfaces** (digital/analog) for sensors like ignition, temperature, fuel, door status, etc.
- Built-in **accelerometer** for motion and crash detection.
- **CAN adapter** support for reading vehicle data (speed, fuel level, RPM).
- **Bluetooth connectivity** for external sensors or driver ID.

**Primary Use Cases:**
- Fleet management  
- Vehicle tracking and route monitoring  
- Driver behavior analysis  
- Fuel consumption tracking  

---

## Key AVL Data Fields and Meanings
AVL (Automatic Vehicle Location) data contains a snapshot of telemetry and GPS info.

| Field | Description |
|-------|-------------|
| `timestamp` | Unix time when record was created |
| `latitude`, `longitude` | GPS coordinates |
| `altitude` | Meters above sea level |
| `angle` | Vehicle direction (0–359°) |
| `speed` | Speed in km/h |
| `satellites` | Number of satellites used |
| `io_elements` | Additional I/O parameters (sensor data) |
| `pr` | Priority or position report flag |
| `tr` | Trip status (moving or stopped) |
| `ignition` | Engine ON/OFF (digital input) |
| `battery_voltage` | Internal battery status |
| `gsm_signal` | GSM signal strength |
| `odometer` | Distance counter |
| `can_data` | CAN bus readings (RPM, fuel, temperature, etc.) |

---

## Data Packet Structure
Teltonika’s **AVL data packet** follows this pattern (Hexadecimal format):

```
| Preamble | Data Field Length | Codec ID | Number of Data | Data 1 | ... | Data N | Number of Data | CRC |
```

Each **Data Record** includes:
- **Timestamp** (8 bytes)
- **Priority**
- **GPS Element** (Longitude, Latitude, Altitude, Angle, Satellites, Speed)
- **IO Element Count**
- **IO Data** (Custom sensors / parameters)

Example (simplified JSON after decoding):
```json
{
  "timestamp": 1745803078000,
  "gps": {
    "lat": -33.979753,
    "lng": 18.489030,
    "alt": 3,
    "speed": 45,
    "sat": 18
  },
  "io": {
    "66": 15118,
    "239": 0,
    "16": 15056
  }
}
```

---

## Encoding of GPS and Sensor Data
- **GPS data** is stored as integers scaled by a factor (e.g., latitude/longitude × 10⁷).
- **IO Elements** are encoded as key-value pairs:
  - **1-byte, 2-byte, 4-byte, 8-byte** values depending on data type.
  - **Hexadecimal keys** represent parameter IDs (e.g., `0x10` = Ignition).
- **Angle** represents compass heading (0° = North).
- **Speed** in km/h.
- **Time** in milliseconds since epoch (Unix time).

---

## Example Scenarios
### Vehicle Moving
- `speed`: >0  
- `tr`: 1  
- `ignition`: ON  
- `gps`: changing coordinates  

### Vehicle Idle
- `speed`: 0  
- `ignition`: ON  
- `tr`: 0  

### Vehicle Off
- `speed`: 0  
- `ignition`: OFF  
- `battery_voltage`: drops to backup  

---

# ☁️ DynamoDB Research Report

## a. Costing Model

### On-Demand Capacity
- Pay per **read/write request unit**.
- Ideal for unpredictable traffic.
- **Cost:**  
  - Write: ~$1.25 per million writes  
  - Read: ~$0.25 per million reads  

### Provisioned Capacity
- You reserve **Read Capacity Units (RCU)** and **Write Capacity Units (WCU)**.
- 1 RCU = 1 strongly consistent read per second for items ≤4 KB.
- 1 WCU = 1 write per second for items ≤1 KB.
- **Auto Scaling** can adjust capacity based on traffic.

### Storage Costs
- ~$0.25 per GB-month of stored data.

### Cost Optimization
- Use **DAX (DynamoDB Accelerator)** for caching.  
- Apply **TTL** (Time to Live) to expire old data.  
- Use **on-demand to provisioned switching** for predictable workloads.  
- Compress large attributes.  

---

## b. Read/Write Operations

### Reading Data
```python
response = table.get_item(Key={'user_id': '123'})
item = response['Item']
```

### Query vs Scan

| Operation | Description | Use Case |
|------------|-------------|----------|
| `Query` | Searches by primary key or index | Fast and efficient |
| `Scan` | Reads every item in a table | Use sparingly |

### Batch Reads/Writes
```python
batch = boto3.client('dynamodb')
batch.batch_write_item(RequestItems={...})
```

### Write Operations
- `PutItem` → insert/replace  
- `UpdateItem` → modify attributes  
- `DeleteItem` → remove record  

---

## c. Database Type & Characteristics
- **Type:** Fully managed **NoSQL key-value and document store**.  
- **Primary Key:** Partition key (hash key).  
- **Composite Key:** Partition + Sort key for range queries.  
- **Indexes:**
  - **GSI (Global Secondary Index)** → query different keys.
  - **LSI (Local Secondary Index)** → same partition, different sort key.  
- **Consistency:**
  - **Eventually consistent** (faster, cheaper).
  - **Strongly consistent** (slower, immediate).

---

## d. Comparison with Other Databases

| Feature | DynamoDB | RDS (PostgreSQL) | MongoDB | Cassandra |
|----------|-----------|----------------|----------|------------|
| Type | NoSQL | Relational | NoSQL | NoSQL |
| Schema | Schema-less | Fixed schema | Flexible | Flexible |
| Scaling | Automatic | Manual | Sharding | Peer-to-peer |
| Query | Key-based | SQL | JSON-based | CQL |
| Best for | High-traffic, low-latency apps | Structured data | Semi-structured | Large-scale writes |
| Limitations | Limited query flexibility | Scaling limits | Management overhead | Complex setup |

### When to Use DynamoDB
✅ Real-time apps needing millisecond response  
✅ IoT telemetry or gaming leaderboards  
✅ High-availability, globally distributed systems  

---

## References
- [AWS DynamoDB Documentation](https://docs.aws.amazon.com/dynamodb/)  
- Teltonika FMC130 AVL Protocol Documentation  
- [AWS Pricing Calculator](https://calculator.aws/)  
