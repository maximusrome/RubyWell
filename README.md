# RubyWell - Medicare Benefits Platform

A comprehensive full-stack platform for exploring and understanding Medicare Advantage plans and benefits. This project demonstrates advanced healthcare data processing, AI-powered document parsing, and modern web development practices.

## Overview

RubyWell is a healthcare technology platform that helps users navigate Medicare Advantage plans by providing detailed benefit information, plan comparisons, and intelligent document processing. The platform processes complex healthcare documents using AI and presents the data through intuitive web interfaces.

## Architecture

The platform consists of several interconnected services:

- **Frontend Applications**: Modern React/Next.js interfaces for plan exploration and user management
- **Backend APIs**: Flask and Node.js services for data management and processing
- **Document Processing**: AI-powered parsing of Medicare documents using GPT
- **Data Scraping**: Automated collection of plan data from major insurance providers
- **Infrastructure**: AWS-based deployment with serverless architecture

## Key Features

- **Plan Discovery**: Search and explore Medicare Advantage plans by location and criteria
- **Benefit Comparison**: Compare benefits across different plans and insurance companies
- **AI Document Processing**: Automated parsing of Evidence of Coverage (EOC) documents
- **Data Visualization**: Interactive maps and charts for plan data analysis
- **User Management**: Authentication, profiles, and personalized experiences
- **Admin Dashboard**: Management interfaces for plan data and user administration

## Technology Stack

### Frontend
- **React 18** with Next.js 14
- **TypeScript** for type safety
- **Tailwind CSS** for styling
- **D3.js** for data visualization
- **React Query** for state management

### Backend
- **Python Flask** for plan data APIs
- **Node.js** for document processing services
- **PostgreSQL** for relational data
- **MongoDB** for document storage
- **AWS Cognito** for authentication

### AI & Processing
- **OpenAI GPT** for document parsing
- **PDF processing** with custom extraction algorithms
- **Web scraping** for insurance provider data

### Infrastructure
- **AWS SST** for serverless deployment
- **Heroku** for API hosting
- **MongoDB Atlas** for cloud database

## Project Structure

```
RubyWell/
├── Benefits-FE/              # Main React/Next.js frontend application
├── Benefits-API/             # Flask API for plan data and management
├── supplemental-benefits-api/ # AI-powered document processing system
├── Script/                   # Data migration and utility scripts
├── rubycare/                 # Modern serverless application (AWS SST)
├── sample_pages/             # Learning and example projects
└── max-react/                # Additional React learning project
```

## Getting Started

Each project directory contains its own README with specific setup instructions. Start with the main frontend application:

```bash
cd Benefits-FE
npm install
npm run dev
```

## Development Highlights

- **Scalable Architecture**: Microservices design with clear separation of concerns
- **AI Integration**: Advanced document processing using GPT for healthcare data extraction
- **Data Pipeline**: Automated collection and processing of insurance plan data
- **Modern UI/UX**: Responsive design with accessibility considerations
- **Security**: HIPAA-compliant data handling and secure authentication
- **Performance**: Optimized for large datasets and real-time user interactions

## Contributing

This project demonstrates enterprise-level development practices including:
- Comprehensive error handling and logging
- Automated testing and CI/CD pipelines
- Code quality tools and linting
- Documentation and API specifications
- Security best practices for healthcare data

## License

This project is proprietary and confidential. All rights reserved.
// Final documentation
