#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Logging Utilities for Stock Management Application

Provides custom decorators for tracking mutations and logging events.
"""

import functools
from datetime import datetime

# Import models from main application
from stock_manager import Session, LogEntry

def log_action(action_type):
    """
    Decorator to log actions performed on items
    
    Args:
        action_type (str): Type of action being performed (e.g., 'Update', 'Checkout', 'Return')
    
    Returns:
        function: Decorated function
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Execute the original function
            result = func(*args, **kwargs)
            
            # Extract item and details from arguments or result
            item = None
            details = None
            
            # Try to find item in arguments
            for arg in args:
                if hasattr(arg, '__tablename__') and getattr(arg, '__tablename__') == 'items':
                    item = arg
                    break
            
            # If not found in args, check kwargs
            if item is None and 'item' in kwargs:
                item = kwargs['item']
            
            # If still not found, check if result is an item
            if item is None and hasattr(result, '__tablename__') and getattr(result, '__tablename__') == 'items':
                item = result
            
            # Get details from kwargs if available
            if 'details' in kwargs:
                details = kwargs['details']
            
            # Log the action if we have an item
            if item is not None:
                with Session() as session:
                    log = LogEntry(
                        item_id=item.id,
                        action=action_type,
                        details=details or f'{action_type} action performed',
                        timestamp=datetime.now()
                    )
                    session.add(log)
                    session.commit()
            
            return result
        return wrapper
    return decorator

def log_checkout(func):
    """
    Decorator specifically for checkout operations
    
    Args:
        func: Function to decorate
    
    Returns:
        function: Decorated function
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # Execute the original function
        result = func(*args, **kwargs)
        
        # Extract item and user from arguments
        item_id = None
        user = None
        
        # Check if first argument is self (instance method)
        if len(args) > 0 and hasattr(args[0], 'checkout_asset'):
            # For class methods, item_id and user might be in different positions
            if len(args) > 1:
                item_id = args[1]  # Assuming item_id is the second argument
            if len(args) > 2:
                user = args[2]  # Assuming user is the third argument
        else:
            # For standalone functions
            if len(args) > 0:
                item_id = args[0]  # Assuming item_id is the first argument
            if len(args) > 1:
                user = args[1]  # Assuming user is the second argument
        
        # Check kwargs if not found in args
        if item_id is None and 'item_id' in kwargs:
            item_id = kwargs['item_id']
        if user is None and 'user' in kwargs:
            user = kwargs['user']
        
        # Log the checkout action
        if item_id is not None:
            with Session() as session:
                log = LogEntry(
                    item_id=item_id,
                    action='Checkout',
                    details=f'Checked out to {user}' if user else 'Checked out',
                    timestamp=datetime.now()
                )
                session.add(log)
                session.commit()
        
        return result
    return wrapper

def log_return(func):
    """
    Decorator specifically for return operations
    
    Args:
        func: Function to decorate
    
    Returns:
        function: Decorated function
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # Execute the original function
        result = func(*args, **kwargs)
        
        # Extract item_id from arguments
        item_id = None
        
        # Check if first argument is self (instance method)
        if len(args) > 0 and hasattr(args[0], 'return_asset'):
            # For class methods, item_id might be in different position
            if len(args) > 1:
                item_id = args[1]  # Assuming item_id is the second argument
        else:
            # For standalone functions
            if len(args) > 0:
                item_id = args[0]  # Assuming item_id is the first argument
        
        # Check kwargs if not found in args
        if item_id is None and 'item_id' in kwargs:
            item_id = kwargs['item_id']
        
        # Log the return action
        if item_id is not None:
            with Session() as session:
                log = LogEntry(
                    item_id=item_id,
                    action='Return',
                    details='Asset returned',
                    timestamp=datetime.now()
                )
                session.add(log)
                session.commit()
        
        return result
    return wrapper

def log_restock(func):
    """
    Decorator specifically for restock operations
    
    Args:
        func: Function to decorate
    
    Returns:
        function: Decorated function
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # Execute the original function
        result = func(*args, **kwargs)
        
        # Extract item_id and quantity from arguments
        item_id = None
        quantity = None
        
        # Check if first argument is self (instance method)
        if len(args) > 0 and hasattr(args[0], 'restock_item'):
            # For class methods
            if len(args) > 1:
                item_id = args[1]  # Assuming item_id is the second argument
            if len(args) > 2:
                quantity = args[2]  # Assuming quantity is the third argument
        else:
            # For standalone functions
            if len(args) > 0:
                item_id = args[0]  # Assuming item_id is the first argument
            if len(args) > 1:
                quantity = args[1]  # Assuming quantity is the second argument
        
        # Check kwargs if not found in args
        if item_id is None and 'item_id' in kwargs:
            item_id = kwargs['item_id']
        if quantity is None and 'quantity' in kwargs:
            quantity = kwargs['quantity']
        
        # Log the restock action
        if item_id is not None:
            with Session() as session:
                log = LogEntry(
                    item_id=item_id,
                    action='Restock',
                    details=f'Restocked with {quantity} units' if quantity else 'Restocked',
                    timestamp=datetime.now()
                )
                session.add(log)
                session.commit()
        
        return result
    return wrapper

# Example usage:
"""
@log_action('Update')
def update_item(item, **kwargs):
    # Update item logic here
    pass

@log_checkout
def checkout_item(item_id, user):
    # Checkout logic here
    pass

@log_return
def return_item(item_id):
    # Return logic here
    pass

@log_restock
def restock_item(item_id, quantity):
    # Restock logic here
    pass
"""