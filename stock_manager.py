#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Stock Management Application

A production-ready stock management application built with PySide6.
Features include inventory tracking, asset management, and visualization.
"""

import sys
import os
from datetime import datetime

from PySide6.QtWidgets import (QApplication, QMainWindow, QTabWidget, QVBoxLayout, 
                             QWidget, QTableView, QPushButton, QHBoxLayout, 
                             QLabel, QComboBox, QLineEdit, QMessageBox, 
                             QDialog, QFormLayout, QSpinBox, QDateEdit, 
                             QDialogButtonBox, QHeaderView, QFileDialog)
from PySide6.QtCore import Qt, QAbstractTableModel, QModelIndex, QDate, Signal, Slot
from PySide6.QtGui import QColor, QIcon, QPixmap

# Database imports
import sqlalchemy as sa
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

# Models
Base = declarative_base()

class Item(Base):
    __tablename__ = 'items'
    
    id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.String, nullable=False)
    type = sa.Column(sa.String, nullable=False)
    category = sa.Column(sa.String, nullable=False)
    quantity = sa.Column(sa.Integer, default=1)
    min_threshold = sa.Column(sa.Integer, default=0)
    status = sa.Column(sa.String, default='Available')
    assigned_to = sa.Column(sa.String, nullable=True)
    due_date = sa.Column(sa.DateTime, nullable=True)
    last_updated = sa.Column(sa.DateTime, default=datetime.now)
    
    logs = relationship("LogEntry", back_populates="item")
    
    def __repr__(self):
        return f"<Item(id={self.id}, name='{self.name}', type='{self.type}')>"

class LogEntry(Base):
    __tablename__ = 'logs'
    
    id = sa.Column(sa.Integer, primary_key=True)
    item_id = sa.Column(sa.Integer, sa.ForeignKey('items.id'))
    action = sa.Column(sa.String, nullable=False)
    details = sa.Column(sa.String, nullable=True)
    timestamp = sa.Column(sa.DateTime, default=datetime.now)
    
    item = relationship("Item", back_populates="logs")
    
    def __repr__(self):
        return f"<LogEntry(id={self.id}, action='{self.action}', timestamp='{self.timestamp}')>"

# Database setup
db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'stock_manager.db')
engine = sa.create_engine(f'sqlite:///{db_path}')
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)

# Table Models
class ItemTableModel(QAbstractTableModel):
    def __init__(self, data=None, item_type='standard'):
        super().__init__()
        self.item_type = item_type
        self.load_data(data)
        
    def load_data(self, data=None):
        with Session() as session:
            if data is None:
                self.items = session.query(Item).filter(Item.type == self.item_type).all()
            else:
                self.items = data
        self.layoutChanged.emit()
    
    def rowCount(self, parent=QModelIndex()):
        return len(self.items)
    
    def columnCount(self, parent=QModelIndex()):
        if self.item_type == 'standard':
            return 6  # ID, Name, Category, Quantity, Min Threshold, Last Updated
        else:  # shareable
            return 8  # ID, Name, Category, Status, Assigned To, Due Date, Quantity, Last Updated
    
    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid() or not (0 <= index.row() < len(self.items)):
            return None
            
        item = self.items[index.row()]
        col = index.column()
        
        if role == Qt.DisplayRole:
            if self.item_type == 'standard':
                if col == 0: return item.id
                elif col == 1: return item.name
                elif col == 2: return item.category
                elif col == 3: return item.quantity
                elif col == 4: return item.min_threshold
                elif col == 5: return item.last_updated.strftime('%Y-%m-%d %H:%M')
            else:  # shareable
                if col == 0: return item.id
                elif col == 1: return item.name
                elif col == 2: return item.category
                elif col == 3: return item.status
                elif col == 4: return item.assigned_to or ''
                elif col == 5: return item.due_date.strftime('%Y-%m-%d') if item.due_date else ''
                elif col == 6: return item.quantity
                elif col == 7: return item.last_updated.strftime('%Y-%m-%d %H:%M')
        
        elif role == Qt.BackgroundRole:
            # Color coding for quantity levels
            if (self.item_type == 'standard' and col == 3) or (self.item_type == 'shareable' and col == 6):
                if item.quantity < item.min_threshold:
                    return QColor(255, 200, 200)  # Light red
                elif item.quantity == item.min_threshold:
                    return QColor(255, 230, 180)  # Light orange
                else:
                    return QColor(0, 180, 0)  # Darker green for available items
            
            # Color coding for status
            if self.item_type == 'shareable' and col == 3:
                if item.status == 'In Use':
                    return QColor(255, 200, 200)  # Light red
                else:  # Available
                    return QColor(0, 180, 0)  # Darker green for available items
        
        # Enable item selection with mouse
        elif role == Qt.ItemIsSelectable:
            return True
        
        return None
    
    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role != Qt.DisplayRole:
            return None
            
        if orientation == Qt.Horizontal:
            if self.item_type == 'standard':
                headers = ['ID', 'Name', 'Category', 'Quantity', 'Min Threshold', 'Last Updated']
            else:  # shareable
                headers = ['ID', 'Name', 'Category', 'Status', 'Assigned To', 'Due Date', 'Quantity', 'Last Updated']
            return headers[section]
        
        return None

# Item Dialog
class ItemDialog(QDialog):
    def __init__(self, parent=None, item=None, item_type='standard'):
        super().__init__(parent)
        self.item = item
        self.item_type = item_type
        self.setup_ui()
        
    def setup_ui(self):
        self.setWindowTitle('Add Item' if not self.item else 'Edit Item')
        layout = QFormLayout(self)
        self.layout = layout  # Store layout reference for later use
        
        # Common fields
        self.name_edit = QLineEdit(self.item.name if self.item else '')
        self.category_edit = QLineEdit(self.item.category if self.item else '')
        self.quantity_spin = QSpinBox()
        self.quantity_spin.setRange(0, 10000)
        self.quantity_spin.setValue(self.item.quantity if self.item else 1)
        self.min_threshold_spin = QSpinBox()
        self.min_threshold_spin.setRange(0, 10000)
        self.min_threshold_spin.setValue(self.item.min_threshold if self.item else 0)
        
        layout.addRow('Name:', self.name_edit)
        layout.addRow('Category:', self.category_edit)
        layout.addRow('Quantity:', self.quantity_spin)
        layout.addRow('Min Threshold:', self.min_threshold_spin)
        
        # Shareable-specific fields
        if self.item_type == 'shareable':
            self.status_combo = QComboBox()
            self.status_combo.addItems(['Available', 'In Use'])
            if self.item:
                self.status_combo.setCurrentText(self.item.status)
            else:
                self.status_combo.setCurrentText('Available')
            
            # Connect status change signal to update UI
            self.status_combo.currentTextChanged.connect(self.update_fields_visibility)
                
            self.assigned_to_edit = QLineEdit(self.item.assigned_to if self.item and self.item.assigned_to else '')
            self.due_date_edit = QDateEdit()
            self.due_date_edit.setCalendarPopup(True)
            if self.item and self.item.due_date:
                self.due_date_edit.setDate(QDate.fromString(self.item.due_date.strftime('%Y-%m-%d'), 'yyyy-MM-dd'))
            else:
                self.due_date_edit.setDate(QDate.currentDate().addDays(7))
            
            layout.addRow('Status:', self.status_combo)
            
            # Store references to label widgets for later visibility control
            self.assigned_to_label = QLabel('Assigned To:')
            self.due_date_label = QLabel('Due Date:')
            
            layout.addRow(self.assigned_to_label, self.assigned_to_edit)
            layout.addRow(self.due_date_label, self.due_date_edit)
            
            # Initialize visibility based on current status
            self.update_fields_visibility(self.status_combo.currentText())
        
        # Buttons
        self.button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        layout.addRow(self.button_box)
    
    def update_fields_visibility(self, status):
        """Show or hide assigned_to and due_date fields based on status"""
        is_in_use = (status == 'In Use')
        
        # Show/hide assigned to field
        self.assigned_to_label.setVisible(is_in_use)
        self.assigned_to_edit.setVisible(is_in_use)
        
        # Show/hide due date field
        self.due_date_label.setVisible(is_in_use)
        self.due_date_edit.setVisible(is_in_use)
    
    def get_item_data(self):
        data = {
            'name': self.name_edit.text(),
            'category': self.category_edit.text(),
            'quantity': self.quantity_spin.value(),
            'min_threshold': self.min_threshold_spin.value(),
            'type': self.item_type
        }
        
        if self.item_type == 'shareable':
            data.update({
                'status': self.status_combo.currentText(),
                'assigned_to': self.assigned_to_edit.text() if self.assigned_to_edit.text() and self.status_combo.currentText() == 'In Use' else None,
                'due_date': datetime.strptime(self.due_date_edit.date().toString('yyyy-MM-dd'), '%Y-%m-%d') 
                            if self.status_combo.currentText() == 'In Use' else None
            })
        
        return data

# Main Window
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setup_ui()
        
    def setup_ui(self):
        self.setWindowTitle('Stock Manager')
        self.resize(1000, 600)
        
        # Central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # Tab widget
        self.tab_widget = QTabWidget()
        main_layout.addWidget(self.tab_widget)
        
        # Standard Stock Tab
        self.standard_tab = QWidget()
        standard_layout = QVBoxLayout(self.standard_tab)
        
        # Standard controls
        standard_controls = QHBoxLayout()
        standard_add_btn = QPushButton('Add Item')
        standard_add_btn.clicked.connect(lambda: self.add_item('standard'))
        standard_edit_btn = QPushButton('Edit Item')
        standard_edit_btn.clicked.connect(lambda: self.edit_item('standard'))
        standard_delete_btn = QPushButton('Delete Item')
        standard_delete_btn.clicked.connect(lambda: self.delete_item('standard'))
        standard_controls.addWidget(standard_add_btn)
        standard_controls.addWidget(standard_edit_btn)
        standard_controls.addWidget(standard_delete_btn)
        standard_controls.addStretch()
        
        # Standard table
        self.standard_table = QTableView()
        self.standard_model = ItemTableModel(item_type='standard')
        self.standard_table.setModel(self.standard_model)
        self.standard_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.standard_table.setSelectionBehavior(QTableView.SelectRows)
        self.standard_table.setSelectionMode(QTableView.SingleSelection)
        self.standard_table.clicked.connect(lambda index: self.handle_item_selection('standard', index))
        
        standard_layout.addLayout(standard_controls)
        standard_layout.addWidget(self.standard_table)
        
        # Shareable Assets Tab
        self.shareable_tab = QWidget()
        shareable_layout = QVBoxLayout(self.shareable_tab)
        
        # Shareable controls
        shareable_controls = QHBoxLayout()
        shareable_add_btn = QPushButton('Add Asset')
        shareable_add_btn.clicked.connect(lambda: self.add_item('shareable'))
        shareable_edit_btn = QPushButton('Edit Asset')
        shareable_edit_btn.clicked.connect(lambda: self.edit_item('shareable'))
        shareable_delete_btn = QPushButton('Delete Asset')
        shareable_delete_btn.clicked.connect(lambda: self.delete_item('shareable'))
        shareable_checkout_btn = QPushButton('Checkout Asset')
        shareable_checkout_btn.clicked.connect(self.checkout_asset)
        shareable_return_btn = QPushButton('Return Asset')
        shareable_return_btn.clicked.connect(self.return_asset)
        
        shareable_controls.addWidget(shareable_add_btn)
        shareable_controls.addWidget(shareable_edit_btn)
        shareable_controls.addWidget(shareable_delete_btn)
        shareable_controls.addWidget(shareable_checkout_btn)
        shareable_controls.addWidget(shareable_return_btn)
        shareable_controls.addStretch()
        
        # Shareable table
        self.shareable_table = QTableView()
        self.shareable_model = ItemTableModel(item_type='shareable')
        self.shareable_table.setModel(self.shareable_model)
        self.shareable_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.shareable_table.setSelectionBehavior(QTableView.SelectRows)
        self.shareable_table.setSelectionMode(QTableView.SingleSelection)
        self.shareable_table.clicked.connect(lambda index: self.handle_item_selection('shareable', index))
        
        shareable_layout.addLayout(shareable_controls)
        shareable_layout.addWidget(self.shareable_table)
        
        # Add tabs to tab widget
        self.tab_widget.addTab(self.standard_tab, 'Standard Stock')
        self.tab_widget.addTab(self.shareable_tab, 'Shareable Assets')
    
    def add_item(self, item_type):
        dialog = ItemDialog(self, item_type=item_type)
        if dialog.exec_():
            data = dialog.get_item_data()
            with Session() as session:
                new_item = Item(**data)
                session.add(new_item)
                
                # Add log entry
                log = LogEntry(
                    item=new_item,
                    action='Update',
                    details=f'Added new {item_type} item'
                )
                session.add(log)
                session.commit()
            
            # Refresh table
            if item_type == 'standard':
                self.standard_model.load_data()
            else:
                self.shareable_model.load_data()
    
    def edit_item(self, item_type):
        # Get selected item
        if item_type == 'standard':
            selected = self.standard_table.selectionModel().selectedRows()
            if not selected:
                QMessageBox.warning(self, 'No Selection', 'Please select an item to edit.')
                return
            item_id = self.standard_model.items[selected[0].row()].id
        else:  # shareable
            selected = self.shareable_table.selectionModel().selectedRows()
            if not selected:
                QMessageBox.warning(self, 'No Selection', 'Please select an asset to edit.')
                return
            item_id = self.shareable_model.items[selected[0].row()].id
        
        # Get item from database
        with Session() as session:
            item = session.query(Item).get(item_id)
            if not item:
                QMessageBox.warning(self, 'Error', 'Item not found in database.')
                return
            
            # Open dialog
            dialog = ItemDialog(self, item, item_type)
            if dialog.exec_():
                data = dialog.get_item_data()
                
                # Update item
                for key, value in data.items():
                    setattr(item, key, value)
                item.last_updated = datetime.now()
                
                # Add log entry
                log = LogEntry(
                    item=item,
                    action='Update',
                    details=f'Updated {item_type} item'
                )
                session.add(log)
                session.commit()
        
        # Refresh table
        if item_type == 'standard':
            self.standard_model.load_data()
        else:
            self.shareable_model.load_data()
    
    def delete_item(self, item_type):
        # Get selected item
        if item_type == 'standard':
            selected = self.standard_table.selectionModel().selectedRows()
            if not selected:
                QMessageBox.warning(self, 'No Selection', 'Please select an item to delete.')
                return
            item_id = self.standard_model.items[selected[0].row()].id
        else:  # shareable
            selected = self.shareable_table.selectionModel().selectedRows()
            if not selected:
                QMessageBox.warning(self, 'No Selection', 'Please select an asset to delete.')
                return
            item_id = self.shareable_model.items[selected[0].row()].id
        
        # Confirm deletion
        confirm = QMessageBox.question(
            self, 'Confirm Deletion',
            'Are you sure you want to delete this item? This action cannot be undone.',
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        
        if confirm == QMessageBox.Yes:
            with Session() as session:
                item = session.query(Item).get(item_id)
                if not item:
                    QMessageBox.warning(self, 'Error', 'Item not found in database.')
                    return
                
                # Delete item
                session.delete(item)
                session.commit()
            
            # Refresh table
            if item_type == 'standard':
                self.standard_model.load_data()
            else:
                self.shareable_model.load_data()
    
    def checkout_asset(self):
        # Get selected asset
        selected = self.shareable_table.selectionModel().selectedRows()
        if not selected:
            QMessageBox.warning(self, 'No Selection', 'Please select an asset to checkout.')
            return
        
        item_id = self.shareable_model.items[selected[0].row()].id
        
        # Get asset from database
        with Session() as session:
            item = session.query(Item).get(item_id)
            if not item:
                QMessageBox.warning(self, 'Error', 'Asset not found in database.')
                return
            
            if item.type != 'shareable':
                QMessageBox.warning(self, 'Error', 'Cannot checkout non-shareable items.')
                return
            
            if item.status == 'In Use':
                QMessageBox.warning(self, 'Error', 'Asset is already checked out.')
                return
            
            # Open dialog for checkout details
            dialog = QDialog(self)
            dialog.setWindowTitle('Checkout Asset')
            layout = QFormLayout(dialog)
            
            assigned_to_edit = QLineEdit()
            due_date_edit = QDateEdit()
            due_date_edit.setCalendarPopup(True)
            due_date_edit.setDate(QDate.currentDate().addDays(7))
            
            layout.addRow('Assigned To:', assigned_to_edit)
            layout.addRow('Due Date:', due_date_edit)
            
            button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
            button_box.accepted.connect(dialog.accept)
            button_box.rejected.connect(dialog.reject)
            layout.addRow(button_box)
            
            if dialog.exec_():
                assigned_to = assigned_to_edit.text()
                due_date = datetime.strptime(due_date_edit.date().toString('yyyy-MM-dd'), '%Y-%m-%d')
                
                if not assigned_to:
                    QMessageBox.warning(self, 'Error', 'Please enter who the asset is assigned to.')
                    return
                
                # Update asset
                item.status = 'In Use'
                item.assigned_to = assigned_to
                item.due_date = due_date
                item.last_updated = datetime.now()
                
                # Add log entry
                log = LogEntry(
                    item=item,
                    action='Checkout',
                    details=f'Checked out to {assigned_to}'
                )
                session.add(log)
                session.commit()
                
                # TODO: Send email notification
                # send_email(assigned_to, f"Asset {item.name} checked out")
                
                # Refresh table
                self.shareable_model.load_data()
    
    def return_asset(self):
        # Get selected asset
        selected = self.shareable_table.selectionModel().selectedRows()
        if not selected:
            QMessageBox.warning(self, 'No Selection', 'Please select an asset to return.')
            return
        
        item_id = self.shareable_model.items[selected[0].row()].id
        
        # Get asset from database
        with Session() as session:
            item = session.query(Item).get(item_id)
            if not item:
                QMessageBox.warning(self, 'Error', 'Asset not found in database.')
                return
            
            if item.type != 'shareable':
                QMessageBox.warning(self, 'Error', 'Cannot return non-shareable items.')
                return
            
            if item.status != 'In Use':
                QMessageBox.warning(self, 'Error', 'Asset is not checked out.')
                return
            
            # Update asset
            item.status = 'Available'
            item.assigned_to = None
            item.due_date = None
            item.last_updated = datetime.now()
            
            # Add log entry
            log = LogEntry(
                item=item,
                action='Return',
                details='Asset returned'
            )
            session.add(log)
            session.commit()
            
            # Refresh table
            self.shareable_model.load_data()
    
    def handle_item_selection(self, item_type, index):
        """Handle item selection in table views"""
        row = index.row()
        if item_type == 'standard':
            item = self.standard_model.items[row]
            # Display selection info (status bar is handled in EnhancedMainWindow)
            print(f"Selected: {item.name} - {item.category} - Quantity: {item.quantity}")
        else:  # shareable
            item = self.shareable_model.items[row]
            status_msg = f"Selected: {item.name} - {item.category} - Status: {item.status}"
            if item.status == 'In Use':
                status_msg += f" - Assigned to: {item.assigned_to}"
            # Display selection info (status bar is handled in EnhancedMainWindow)
            print(status_msg)

# Main application
def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()