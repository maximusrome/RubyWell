# RubyWell Scripts

A collection of utility scripts and data migration tools for the RubyWell healthcare platform. These scripts demonstrate advanced data processing, API integration, and automation capabilities.

## Overview

The Scripts module contains specialized tools for data migration, API integration, and automated processing tasks. These utilities showcase proficiency in data manipulation, external API integration, and system automation.

## Script Categories

### Data Migration Scripts

#### WellCare Migration (`WellCareMigration.py`)
**Purpose**: Migrates plan data from WellCare systems to the RubyWell platform.

**Features:**
- Firebase integration for data storage
- Web scraping with BeautifulSoup
- Session management and authentication
- Geographic data processing
- Error handling and retry mechanisms

**Key Capabilities:**
- Automated plan discovery by zip code
- County and state-level data processing
- FIPS code mapping and validation
- Data transformation and normalization

#### Anthem Migration (`AnthemMigration.py`)
**Purpose**: Processes and migrates Anthem insurance plan data.

**Features:**
- API integration with Anthem systems
- Data validation and quality checks
- Batch processing capabilities
- Comprehensive error logging

### API Integration Scripts

#### WellCare API (`WellCare.py`)
**Purpose**: Comprehensive API client for WellCare insurance systems.

**Features:**
- RESTful API communication
- Authentication token management
- Rate limiting and retry logic
- Data transformation and validation

**Key Components:**
- Session management with cookie handling
- Request verification token processing
- Geographic data mapping
- Plan information extraction

#### Anthem API (`AnthemAPI.py`)
**Purpose**: Advanced API integration with Anthem insurance systems.

**Features:**
- OAuth authentication flow
- Complex API endpoint management
- Data pagination and streaming
- Comprehensive error handling

### Data Processing Scripts

#### Anthem Plan Script (`AnthemPlanScript.py`)
**Purpose**: Specialized processing for Anthem plan data.

**Features:**
- Plan data extraction and transformation
- Benefit information processing
- Cost structure analysis
- Data quality validation

#### Anthem Checker (`AnthemChecker.py`)
**Purpose**: Data validation and quality assurance for Anthem data.

**Features:**
- Automated data validation
- Quality metrics calculation
- Error detection and reporting
- Data completeness verification

## Technology Stack

### Core Technologies
- **Python 3.8+**: Primary scripting language
- **Requests**: HTTP client for API communication
- **BeautifulSoup**: HTML parsing and web scraping
- **Firebase Admin**: Cloud database integration
- **JSON**: Data serialization and processing

### Supporting Libraries
- **urllib**: URL processing and encoding
- **time**: Timing and rate limiting
- **json**: Data serialization
- **logging**: Comprehensive logging system

## Data Models

### Plan Information
```python
{
    "contractId": "H5521",
    "bidId": "333",
    "segmentId": "001",
    "planName": "Medicare Advantage Plan",
    "company": "WellCare",
    "region": "New York, NY",
    "zipCode": "10001",
    "fipsCode": "36061",
    "benefits": [...],
    "costs": {...}
}
```

### Geographic Data
```python
{
    "zipCode": "10001",
    "county": "New York",
    "state": "NY",
    "fipsCode": "36061",
    "primaryCity": "New York"
}
```

## Getting Started

### Prerequisites

- Python 3.8+
- Firebase Admin SDK credentials
- API keys for insurance providers
- Required Python packages

### Installation

1. Navigate to the scripts directory:
```bash
cd Script
```

2. Install Python dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
export FIREBASE_CREDENTIALS_PATH=path/to/credentials.json
export ANTHEM_API_KEY=your_anthem_api_key
export WELLCARE_API_KEY=your_wellcare_api_key
```

4. Run specific scripts:
```bash
python WellCareMigration.py
python AnthemMigration.py
python WellCare.py
```

## Development

### Project Structure

```
Script/
├── WellCareMigration.py    # WellCare data migration
├── AnthemMigration.py      # Anthem data migration
├── WellCare.py            # WellCare API client
├── AnthemAPI.py           # Anthem API integration
├── AnthemPlanScript.py    # Anthem plan processing
├── AnthemChecker.py       # Data validation
├── models.py              # Data models and schemas
├── requirements.txt       # Python dependencies
└── README.md             # This documentation
```

### Script Workflow

1. **Authentication**
   - Establish API connections
   - Handle authentication tokens
   - Manage session cookies

2. **Data Collection**
   - Fetch data from external APIs
   - Process geographic regions
   - Extract plan information

3. **Data Processing**
   - Transform and normalize data
   - Validate data quality
   - Handle errors and edge cases

4. **Data Storage**
   - Store processed data
   - Update existing records
   - Maintain data integrity

## Error Handling

### Comprehensive Error Management

- **Network Errors**: Automatic retry with exponential backoff
- **Authentication Failures**: Token refresh and re-authentication
- **Rate Limiting**: Dynamic request throttling
- **Data Validation**: Quality checks and error logging
- **Geographic Errors**: Fallback processing for failed regions

### Logging and Monitoring

- **Structured Logging**: Comprehensive error and info logging
- **Progress Tracking**: Real-time processing status
- **Error Reporting**: Detailed error analysis and reporting
- **Performance Metrics**: Processing time and success rates

## Performance Optimization

### Efficiency Strategies

- **Batch Processing**: Process multiple records concurrently
- **Connection Pooling**: Reuse HTTP connections
- **Caching**: Cache frequently accessed data
- **Rate Limiting**: Respectful API usage patterns
- **Memory Management**: Efficient data structure usage

### Scalability Considerations

- **Incremental Processing**: Process data in manageable chunks
- **Resume Capability**: Continue from last successful point
- **Parallel Processing**: Multi-threaded data processing
- **Resource Management**: Efficient memory and CPU usage

## Security

### Data Protection

- **API Key Management**: Secure storage of credentials
- **Data Encryption**: Sensitive data encryption
- **Access Controls**: Role-based access to scripts
- **Audit Logging**: Complete processing history

### Compliance

- **HIPAA Compliance**: Healthcare data protection
- **Data Privacy**: Secure handling of personal information
- **Access Logging**: Comprehensive audit trails
- **Error Handling**: Secure error reporting

## Testing

### Quality Assurance

- **Unit Testing**: Individual script testing
- **Integration Testing**: End-to-end workflow testing
- **Data Validation**: Automated data quality checks
- **Error Testing**: Comprehensive error scenario testing

### Test Coverage

- **API Integration**: External API testing
- **Data Processing**: Transformation and validation testing
- **Error Handling**: Exception and error scenario testing
- **Performance Testing**: Load and stress testing

## Monitoring and Analytics

### Performance Tracking

- **Processing Metrics**: Real-time script performance
- **Error Tracking**: Comprehensive error logging
- **Success Rates**: Processing success and failure rates
- **Resource Usage**: CPU, memory, and network monitoring

### Quality Metrics

- **Data Accuracy**: Validation of processed data
- **Completeness**: Coverage of target data sources
- **Timeliness**: Processing speed and efficiency
- **Reliability**: System uptime and availability

## License

This project is proprietary and confidential. All rights reserved.
