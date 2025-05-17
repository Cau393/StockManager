#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Import/Export Module for Stock Management Application

Provides functionality for importing and exporting data to/from CSV and Excel files.
"""

import os
import pandas as pd
from datetime import datetime

# Import models from main application
from stock_manager import Session, Item, LogEntry

def export_items(file_path, item_type='all'):
    """
    Export items to CSV or Excel file
    
    Args:
        file_path (str): Path to save the file
        item_type (str): Type of items to export ('all', 'standard', or 'shareable')
    
    Returns:
        bool: True if export was successful, False otherwise
    """
    try:
        with Session() as session:
            # Query items based on type
            query = session.query(Item)
            if item_type != 'all':
                query = query.filter(Item.type == item_type)
            
            items = query.all()
            
            # Convert to DataFrame
            data = []
            for item in items:
                item_dict = {
                    'id': item.id,
                    'name': item.name,
                    'type': item.type,
                    'category': item.category,
                    'quantity': item.quantity,
                    'min_threshold': item.min_threshold,
                    'last_updated': item.last_updated
                }
                
                # Add shareable-specific fields
                if item.type == 'shareable':
                    item_dict.update({
                        'status': item.status,
                        'assigned_to': item.assigned_to,
                        'due_date': item.due_date
                    })
                
                data.append(item_dict)
            
            df = pd.DataFrame(data)
            
            # Export based on file extension
            _, ext = os.path.splitext(file_path)
            if ext.lower() == '.csv':
                df.to_csv(file_path, index=False)
            elif ext.lower() in ['.xlsx', '.xls']:
                df.to_excel(file_path, index=False)
            else:
                return False
            
            return True
    except Exception as e:
        print(f"Export error: {e}")
        return False

def import_items(file_path):
    """
    Import items from CSV or Excel file
    
    Args:
        file_path (str): Path to the file to import
    
    Returns:
        tuple: (success, message, count)
            success (bool): True if import was successful
            message (str): Status message
            count (int): Number of items imported
    """
    try:
        # Read file based on extension
        _, ext = os.path.splitext(file_path)
        if ext.lower() == '.csv':
            df = pd.read_csv(file_path)
        elif ext.lower() in ['.xlsx', '.xls']:
            df = pd.read_excel(file_path)
        else:
            return False, "Unsupported file format. Use CSV or Excel.", 0
        
        # Validate required columns
        required_columns = ['name', 'type', 'category', 'quantity', 'min_threshold']
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            return False, f"Missing required columns: {', '.join(missing_columns)}", 0
        
        # Import items
        count = 0
        with Session() as session:
            for _, row in df.iterrows():
                # Check if item already exists (by name and category)
                existing_item = session.query(Item).filter(
                    Item.name == row['name'],
                    Item.category == row['category']
                ).first()
                
                if existing_item:
                    # Update existing item
                    existing_item.quantity = row['quantity']
                    existing_item.min_threshold = row['min_threshold']
                    existing_item.last_updated = datetime.now()
                    
                    # Update shareable-specific fields if applicable
                    if existing_item.type == 'shareable' and 'status' in row:
                        existing_item.status = row['status']
                        existing_item.assigned_to = row.get('assigned_to')
                        existing_item.due_date = row.get('due_date')
                    
                    # Add log entry
                    log = LogEntry(
                        item=existing_item,
                        action='Update',
                        details='Updated via import'
                    )
                    session.add(log)
                else:
                    # Create new item
                    item_data = {
                        'name': row['name'],
                        'type': row['type'],
                        'category': row['category'],
                        'quantity': row['quantity'],
                        'min_threshold': row['min_threshold']
                    }
                    
                    # Add shareable-specific fields if applicable
                    if row['type'] == 'shareable' and 'status' in row:
                        item_data.update({
                            'status': row['status'],
                            'assigned_to': row.get('assigned_to'),
                            'due_date': row.get('due_date')
                        })
                    
                    new_item = Item(**item_data)
                    session.add(new_item)
                    
                    # Add log entry
                    log = LogEntry(
                        item=new_item,
                        action='Update',
                        details='Added via import'
                    )
                    session.add(log)
                
                count += 1
            
            session.commit()
        
        return True, f"Successfully imported {count} items.", count
    except Exception as e:
        return False, f"Import error: {e}", 0