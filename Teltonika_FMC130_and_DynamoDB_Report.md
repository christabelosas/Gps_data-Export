
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

| Field | Name | Description |
|--------|------|-------------|
| `ts` | Timestamp | Event time in milliseconds since epoch; represents when the GPS data was recorded. |
| `pr` | Priority | Message priority; defines whether the record is high or low importance for transmission. |
| `latlng` | Latitude and Longitude | GPS coordinates of the device in the format `latitude,longitude`. |
| `alt` | Altitude | Device’s altitude above sea level, measured in meters. |
| `ang` | Angle | Vehicle’s direction or heading in degrees (0–359). |
| `sat` | Satellites | Number of GPS satellites used to calculate position accuracy. |
| `sp` | Speed | Vehicle’s instantaneous speed in km/h. |
| `evt` | Event ID | Represents a triggered event type (e.g., movement, ignition, or custom alert). |
| `239` | Ignition | Digital input status; `1` indicates ignition ON, `0` indicates ignition OFF. |
| `240` | Movement | Movement detection flag; `1` when vehicle is moving, `0` when stationary. |
| `21` | GSM Signal | GSM network signal strength (0–5 scale or network-specific range). |
| `200` | Sleep Mode | Indicates if the device is in sleep mode (`1`) or active (`0`). |
| `69` | GNSS Status | General GNSS fix status; `1` indicates valid GPS fix, `0` means no fix. |
| `181` | GNSS PDOP | Position Dilution of Precision; lower values indicate higher GPS accuracy. |
| `182` | GNSS HDOP | Horizontal Dilution of Precision; reflects accuracy of horizontal positioning. |
| `66` | External Voltage | Voltage from the vehicle’s external power source, measured in millivolts. |
| `67` | Battery Voltage | Device’s internal battery voltage, measured in millivolts. |
| `68` | Battery Current | Battery current draw or charge rate, measured in milliamperes. |
| `241` | Active GSM Operator | Network operator code currently providing GSM connectivity. |
| `16` | Total Odometer | Total distance traveled by the vehicle, measured in meters. |
| `78` | iButton | iButton key ID or driver identification data (hexadecimal string). |

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

### Example (Simplified JSON After Decoding)

```json
{
    "company_id": "ees",
    "payload": {
        "reported": {
            "ts": 1745803078000,
            "pr": 0,
            "latlng": "-33.979753,18.489030",
            "alt": 3,
            "ang": 0,
            "sat": 18,
            "sp": 0,
            "evt": 0,
            "239": 0,
            "240": 0,
            "21": 5,
            "200": 0,
            "69": 1,
            "1": 0,
            "179": 1,
            "181": 11,
            "182": 5,
            "66": 15118,
            "67": 4096,
            "68": 0,
            "241": 65502,
            "16": 15056,
            "76": "0x0000000000000000",
            "78": "0x0000000000000000"
        }
    },
    "load_timestamp": 1745803078.0,
    "imei": 864636062694738.0,
    "timestamp": 1745803078.0
}

```

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
