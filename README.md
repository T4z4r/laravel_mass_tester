# Laravel Mass Tester

A Python GUI application for testing Laravel applications for mass assignment vulnerabilities.

## Description

This tool helps identify potential mass assignment vulnerabilities in Laravel projects by:

- Scanning local Laravel models for `$fillable` and `$guarded` properties
- Providing a safe interface for manual online endpoint testing

## Features

- **Local Project Scan**: Analyze Laravel model files to check for mass assignment protection
- **Online Endpoint Test**: Manually test API endpoints with custom payloads (requires confirmation)

## Requirements

- Python 3.x
- Tkinter (usually included with Python)
- Install dependencies: `pip install -r requirements.txt`

## Installation

1. Clone or download the repository
2. Install dependencies: `pip install -r requirements.txt`

## Usage

Run the application:

```bash
python laravel_mass_tester.py
```

### Local Scan

1. Select a Laravel project directory
2. Click "Scan Models" to analyze model files
3. Review results for potential vulnerabilities

### Online Test

1. Enter base URL and endpoint
2. Select HTTP method
3. Provide JSON payload
4. Click "Send Single Test" (requires confirmation)

## Warning

Online testing makes real HTTP requests to live servers. Use responsibly and only on systems you have permission to test.