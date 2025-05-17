# Stock Management Application

A production-ready stock management application built with PySide6 for tracking inventory and shareable assets.

## Features

### Main Dashboard with Two Tabs

- **Standard Stock**: CRUD interface for inventory items with fields:
  - ID (auto-generated)
  - Name
  - Category
  - Quantity
  - Min Threshold
  - Last Restock Date

- **Shareable Assets**: CRUD interface with additional fields:
  - Status (Available/In Use)
  - Assigned To
  - Due Date (optional)

### Visual Indicators

- Color-coded quantity levels:
  - Green: Quantity > Min Threshold
  - Orange: Quantity = Min Threshold
  - Red: Quantity < Min Threshold

- Icon badges for asset status:
  - 🔴 In Use
  - 🟢 Available

### Core Features

- **CRUD Operations**:
  - Add/Edit modal forms with validation
  - Soft delete with archiving
  - Bulk import/export (CSV/Excel)

- **Asset Tracking**:
  - Checkout system for shareables
  - Automatic restock alerts

- **Event Logging**:
  - Timeline widget showing stock changes
  - Filterable logs

## Installation

1. Clone the repository
2. Create a virtual environment (optional but recommended)
3. Install dependencies:

```bash
pip install -r requirements.txt
```

## Usage

Run the application:

```bash
python stock_manager.py
```

## Database Structure

The application uses SQLite with SQLAlchemy ORM. The database schema includes:

- `items` table: Stores all inventory items and shareable assets
- `logs` table: Tracks all actions performed on items

## Technical Stack

- **GUI Framework**: PySide6 (Qt for Python)
- **Database**: SQLAlchemy ORM + SQLite
- **Logging**: Custom tracking for all mutations
- **Styling**: QSS for modern themes
- **Packaging**: PyInstaller for distribution

## Development

### Adding New Features

The application follows an MVC-like pattern:

- Models: SQLAlchemy models in the main file
- Views: PySide6 UI components
- Controllers: Logic in the MainWindow class

### Building for Distribution

To create a standalone executable:

```bash
pyinstaller --onefile --windowed stock_manager.py
```