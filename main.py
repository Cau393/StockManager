#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Stock Management Application - Main Entry Point

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
                             QDialogButtonBox, QHeaderView, QFileDialog, 
                             QToolBar, QStatusBar, QMenu)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QIcon, QKeySequence, QAction

# Import the stock manager module
from stock_manager import (
    Item, LogEntry, Session, ItemTableModel, ItemDialog, 
    MainWindow as StockManagerWindow
)

# Import visualization module
from visualization import DashboardWidget, integrate_dashboard

# Import import/export module
from import_export import export_items, import_items

class EnhancedMainWindow(StockManagerWindow):
    """Enhanced main window with additional features"""
    def __init__(self):
        super().__init__()
        self.setup_enhanced_ui()
        
    def handle_item_selection(self, item_type, index):
        """Override parent method to handle item selection and update status bar"""
        row = index.row()
        if item_type == 'standard':
            item = self.standard_model.items[row]
            self.status_bar.showMessage(f"Selected: {item.name} - {item.category} - Quantity: {item.quantity}")
        else:  # shareable
            item = self.shareable_model.items[row]
            status_msg = f"Selected: {item.name} - {item.category} - Status: {item.status}"
            if item.status == 'In Use':
                status_msg += f" - Assigned to: {item.assigned_to}"
            self.status_bar.showMessage(status_msg)
        
    def setup_enhanced_ui(self):
        # Add toolbar
        self.toolbar = QToolBar("Main Toolbar")
        self.toolbar.setIconSize(QSize(24, 24))
        self.addToolBar(self.toolbar)
        
        # Add status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")
        
        # Add dashboard tab
        self.dashboard = integrate_dashboard(self)
        
        # Add import/export actions
        import_action = QAction("Import", self)
        import_action.setShortcut(QKeySequence("Ctrl+I"))
        import_action.triggered.connect(self.import_data)
        
        export_action = QAction("Export", self)
        export_action.setShortcut(QKeySequence("Ctrl+E"))
        export_action.triggered.connect(self.export_data)
        
        # Add actions to toolbar
        self.toolbar.addAction(import_action)
        self.toolbar.addAction(export_action)
        
        # Add File menu
        menu_bar = self.menuBar()
        file_menu = menu_bar.addMenu("&File")
        file_menu.addAction(import_action)
        file_menu.addAction(export_action)
        file_menu.addSeparator()
        
        exit_action = QAction("Exit", self)
        exit_action.setShortcut(QKeySequence("Ctrl+Q"))
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Add View menu
        view_menu = menu_bar.addMenu("&View")
        refresh_action = QAction("Refresh", self)
        refresh_action.setShortcut(QKeySequence("F5"))
        refresh_action.triggered.connect(self.refresh_data)
        view_menu.addAction(refresh_action)
        
        # Add Help menu
        help_menu = menu_bar.addMenu("&Help")
        about_action = QAction("About", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    def import_data(self):
        """Import data from CSV or Excel file"""
        file_dialog = QFileDialog(self)
        file_dialog.setWindowTitle("Import Data")
        file_dialog.setNameFilter("CSV Files (*.csv);;Excel Files (*.xlsx *.xls)")
        file_dialog.setFileMode(QFileDialog.ExistingFile)
        
        if file_dialog.exec_():
            file_path = file_dialog.selectedFiles()[0]
            success, message, count = import_items(file_path)
            
            if success:
                QMessageBox.information(self, "Import Successful", message)
                self.refresh_data()
                self.status_bar.showMessage(f"Imported {count} items")
            else:
                QMessageBox.warning(self, "Import Failed", message)
    
    def export_data(self):
        """Export data to CSV or Excel file"""
        # Determine which tab is active to set default export type
        current_tab = self.tab_widget.currentIndex()
        if current_tab == 0:  # Dashboard
            item_type = 'all'
        elif current_tab == 1:  # Standard Stock
            item_type = 'standard'
        else:  # Shareable Assets
            item_type = 'shareable'
        
        # Create dialog to select export options
        dialog = QDialog(self)
        dialog.setWindowTitle("Export Data")
        layout = QFormLayout(dialog)
        
        type_combo = QComboBox()
        type_combo.addItems(["All Items", "Standard Stock", "Shareable Assets"])
        if item_type == 'standard':
            type_combo.setCurrentIndex(1)
        elif item_type == 'shareable':
            type_combo.setCurrentIndex(2)
        else:
            type_combo.setCurrentIndex(0)
        
        layout.addRow("Export Type:", type_combo)
        
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(dialog.accept)
        button_box.rejected.connect(dialog.reject)
        layout.addRow(button_box)
        
        if dialog.exec_():
            # Map combo box selection to item type
            selection = type_combo.currentIndex()
            if selection == 0:
                item_type = 'all'
            elif selection == 1:
                item_type = 'standard'
            else:
                item_type = 'shareable'
            
            # Show file dialog
            file_dialog = QFileDialog(self)
            file_dialog.setWindowTitle("Export Data")
            file_dialog.setNameFilter("CSV Files (*.csv);;Excel Files (*.xlsx)")
            file_dialog.setAcceptMode(QFileDialog.AcceptSave)
            file_dialog.setDefaultSuffix(".csv")
            
            if file_dialog.exec_():
                file_path = file_dialog.selectedFiles()[0]
                success = export_items(file_path, item_type)
                
                if success:
                    QMessageBox.information(self, "Export Successful", 
                                          f"Data exported to {file_path}")
                    self.status_bar.showMessage(f"Exported to {file_path}")
                else:
                    QMessageBox.warning(self, "Export Failed", 
                                      "Failed to export data. Please check file path and permissions.")
    
    def refresh_data(self):
        """Refresh all data in the application"""
        self.standard_model.load_data()
        self.shareable_model.load_data()
        self.dashboard.update_data()
        self.status_bar.showMessage("Data refreshed")
    
    def show_about(self):
        """Show about dialog"""
        QMessageBox.about(self, "About Stock Manager", 
                         "<h1>Stock Manager</h1>"
                         "<p>Version 1.0</p>"
                         "<p>A production-ready stock management application.</p>"
                         "<p>Built with PySide6 and SQLAlchemy.</p>")

def main():
    app = QApplication(sys.argv)
    
    # Set application style
    app.setStyle("Fusion")
    
    # Create and show main window
    window = EnhancedMainWindow()
    window.show()
    
    sys.exit(app.exec())

if __name__ == '__main__':
    main()