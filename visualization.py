#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Visualization Module for Stock Management Application

Provides charts and summary widgets for the stock management application.
"""

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QFrame, QSizePolicy, QComboBox, QDateEdit)
from PySide6.QtCore import Qt, QDate, Slot, QMargins
from PySide6.QtGui import QColor, QPainter, QFont
from PySide6.QtCharts import QChart, QChartView, QBarSeries, QBarSet, QBarCategoryAxis, QValueAxis, QLineSeries

import sqlalchemy as sa
from sqlalchemy.sql import func
from datetime import datetime, timedelta

# Import models from main application
from stock_manager import Session, Item, LogEntry

class SummaryCard(QFrame):
    """A card widget displaying summary information"""
    def __init__(self, title, value, icon=None, parent=None):
        super().__init__(parent)
        self.setFrameShape(QFrame.StyledPanel)
        self.setFrameShadow(QFrame.Raised)
        self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        self.setStyleSheet("""
            SummaryCard {
                background-color: #f8f9fa;
                border-radius: 10px;
                border: 1px solid #dee2e6;
                padding: 10px;
            }
            QLabel[class="title"] {
                color: #333333;
                font-size: 16px;
                font-weight: bold;
                margin-bottom: 5px;
            }
            QLabel[class="value"] {
                color: #0066cc;
                font-size: 28px;
                font-weight: bold;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)  # Add more padding inside the card
        
        # Title
        title_label = QLabel(title)
        title_label.setProperty("class", "title")
        title_label.setAlignment(Qt.AlignCenter)
        
        # Value
        value_label = QLabel(str(value))
        value_label.setProperty("class", "value")
        value_label.setAlignment(Qt.AlignCenter)
        
        layout.addWidget(title_label)
        layout.addWidget(value_label)
        
        self.value_label = value_label  # Store reference for updates
    
    def update_value(self, value):
        """Update the displayed value"""
        self.value_label.setText(str(value))

class StockMovementChart(QWidget):
    """Chart showing monthly stock movement"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.update_chart()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Chart title
        title_label = QLabel("Monthly Stock Movement")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #333333;")
        
        # Chart view
        self.chart = QChart()
        self.chart.setAnimationOptions(QChart.SeriesAnimations)
        self.chart.setBackgroundVisible(False)
        self.chart.setMargins(QMargins(20, 20, 20, 20))
        self.chart.setBackgroundBrush(QColor("#f8f9fa"))
        self.chart.legend().setFont(QFont("Arial", 12))
        self.chart.legend().setAlignment(Qt.AlignBottom)
        
        self.chart_view = QChartView(self.chart)
        self.chart_view.setRenderHint(QPainter.Antialiasing)
        
        layout.addWidget(title_label)
        layout.addWidget(self.chart_view)
    
    def update_chart(self):
        """Update chart with latest data"""
        self.chart.removeAllSeries()
        
        # Get data for the last 6 months
        end_date = datetime.now()
        start_date = end_date - timedelta(days=180)  # ~6 months
        
        with Session() as session:
            # Get monthly counts of different actions
            results = session.query(
                func.strftime('%Y-%m', LogEntry.timestamp).label('month'),
                LogEntry.action,
                func.count(LogEntry.id).label('count')
            ).filter(
                LogEntry.timestamp.between(start_date, end_date)
            ).group_by(
                func.strftime('%Y-%m', LogEntry.timestamp),
                LogEntry.action
            ).order_by(
                func.strftime('%Y-%m', LogEntry.timestamp)
            ).all()
        
        # Organize data by action type
        months = []
        data = {}
        
        for month, action, count in results:
            if month not in months:
                months.append(month)
            
            if action not in data:
                data[action] = []
            
            # Ensure all months have data
            while len(data[action]) < len(months) - 1:
                data[action].append(0)
            
            data[action].append(count)
        
        # Create bar sets for each action type with improved colors
        bar_series = QBarSeries()
        
        # Define a better color palette
        colors = ["#4e79a7", "#f28e2c", "#e15759", "#76b7b2", "#59a14f", "#edc949"]
        
        for i, (action, counts) in enumerate(data.items()):
            # Ensure all actions have the same number of data points
            while len(counts) < len(months):
                counts.append(0)
            
            bar_set = QBarSet(action)
            # Set custom colors for better visibility
            bar_set.setColor(QColor(colors[i % len(colors)]))
            for count in counts:
                bar_set.append(count)
            
            bar_series.append(bar_set)
        
        self.chart.addSeries(bar_series)
        
        # Set up axes with improved fonts
        axis_x = QBarCategoryAxis()
        axis_x.append(months)
        axis_x.setLabelsFont(QFont("Arial", 10))
        self.chart.addAxis(axis_x, Qt.AlignBottom)
        bar_series.attachAxis(axis_x)
        
        axis_y = QValueAxis()
        axis_y.setRange(0, max([max(counts) for counts in data.values()]) if data else 10)
        axis_y.setTickCount(5)
        axis_y.setLabelFormat("%d")
        axis_y.setLabelsFont(QFont("Arial", 10))
        axis_y.setGridLineVisible(True)
        axis_y.setGridLineColor(QColor("#e0e0e0"))
        self.chart.addAxis(axis_y, Qt.AlignLeft)
        bar_series.attachAxis(axis_y)
        
        # Set chart title with better font
        self.chart.setTitle("Stock Movement by Month")
        self.chart.setTitleFont(QFont("Arial", 14, QFont.Bold))
        
        # Refresh chart
        self.chart.update()

class AssetUtilizationChart(QWidget):
    """Chart showing asset utilization"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.update_chart()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Chart title
        title_label = QLabel("Asset Utilization")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #333333;")
        
        # Chart view
        self.chart = QChart()
        self.chart.setAnimationOptions(QChart.SeriesAnimations)
        self.chart.setBackgroundVisible(False)
        self.chart.setMargins(QMargins(20, 20, 20, 20))
        self.chart.setBackgroundBrush(QColor("#f8f9fa"))
        self.chart.legend().setFont(QFont("Arial", 12))
        self.chart.legend().setAlignment(Qt.AlignBottom)
        
        self.chart_view = QChartView(self.chart)
        self.chart_view.setRenderHint(QPainter.Antialiasing)
        
        layout.addWidget(title_label)
        layout.addWidget(self.chart_view)
    
    def update_chart(self):
        """Update chart with latest data"""
        self.chart.removeAllSeries()
        
        with Session() as session:
            # Get checkout counts for shareable assets
            results = session.query(
                Item.name,
                func.count(LogEntry.id).label('checkout_count')
            ).join(
                LogEntry, LogEntry.item_id == Item.id
            ).filter(
                Item.type == 'shareable',
                LogEntry.action == 'Checkout'
            ).group_by(
                Item.id
            ).order_by(
                func.count(LogEntry.id).desc()
            ).limit(10).all()
        
        # Create bar series with improved styling
        bar_series = QBarSeries()
        bar_set = QBarSet("Checkout Count")
        bar_set.setColor(QColor("#4e79a7"))  # Set a nice blue color
        
        asset_names = []
        for name, count in results:
            asset_names.append(name)
            bar_set.append(count)
        
        bar_series.append(bar_set)
        self.chart.addSeries(bar_series)
        
        # Set up axes with improved fonts and grid lines
        axis_x = QBarCategoryAxis()
        axis_x.append(asset_names)
        axis_x.setLabelsFont(QFont("Arial", 10))
        # Rotate labels if names are long
        axis_x.setLabelsAngle(-45) if any(len(name) > 10 for name in asset_names) else None
        self.chart.addAxis(axis_x, Qt.AlignBottom)
        bar_series.attachAxis(axis_x)
        
        axis_y = QValueAxis()
        axis_y.setRange(0, max([count for _, count in results]) if results else 10)
        axis_y.setTickCount(5)
        axis_y.setLabelFormat("%d")
        axis_y.setLabelsFont(QFont("Arial", 10))
        axis_y.setGridLineVisible(True)
        axis_y.setGridLineColor(QColor("#e0e0e0"))
        self.chart.addAxis(axis_y, Qt.AlignLeft)
        bar_series.attachAxis(axis_y)
        
        # Set chart title with better font
        self.chart.setTitle("Most Borrowed Assets")
        self.chart.setTitleFont(QFont("Arial", 14, QFont.Bold))
        
        # Refresh chart
        self.chart.update()

class DashboardWidget(QWidget):
    """Main dashboard widget with summary cards and charts"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.update_data()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(20)  # Add more space between sections
        layout.setContentsMargins(20, 20, 20, 20)  # Add padding around the dashboard
        self.setStyleSheet("background-color: white;")
        
        # Dashboard title
        title_label = QLabel("Stock Management Dashboard")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("font-size: 22px; font-weight: bold; color: #333333; margin-bottom: 15px;")
        layout.addWidget(title_label)
        
        # Summary cards section
        cards_layout = QHBoxLayout()
        cards_layout.setSpacing(15)  # Add space between cards
        
        self.total_items_card = SummaryCard("Total Items", "0")
        self.low_stock_card = SummaryCard("Low Stock Items", "0")
        self.borrowed_assets_card = SummaryCard("Borrowed Assets", "0")
        
        cards_layout.addWidget(self.total_items_card)
        cards_layout.addWidget(self.low_stock_card)
        cards_layout.addWidget(self.borrowed_assets_card)
        
        # Charts section
        charts_layout = QHBoxLayout()
        charts_layout.setSpacing(15)  # Add space between charts
        
        self.stock_movement_chart = StockMovementChart()
        self.asset_utilization_chart = AssetUtilizationChart()
        
        charts_layout.addWidget(self.stock_movement_chart)
        charts_layout.addWidget(self.asset_utilization_chart)
        
        layout.addLayout(cards_layout)
        layout.addSpacing(15)  # Add space between cards and charts
        layout.addLayout(charts_layout)
    
    def update_data(self):
        """Update all dashboard components with latest data"""
        with Session() as session:
            # Total items count
            total_items = session.query(func.count(Item.id)).scalar()
            self.total_items_card.update_value(total_items)
            
            # Low stock items count
            low_stock = session.query(func.count(Item.id)).filter(
                Item.quantity < Item.min_threshold
            ).scalar()
            self.low_stock_card.update_value(low_stock)
            
            # Borrowed assets count
            borrowed = session.query(func.count(Item.id)).filter(
                Item.type == 'shareable',
                Item.status == 'In Use'
            ).scalar()
            self.borrowed_assets_card.update_value(borrowed)
        
        # Update charts
        self.stock_movement_chart.update_chart()
        self.asset_utilization_chart.update_chart()

# Function to integrate dashboard into main application
def integrate_dashboard(main_window):
    """Add dashboard tab to main window"""
    dashboard_widget = DashboardWidget()
    main_window.tab_widget.insertTab(0, dashboard_widget, "Dashboard")
    main_window.tab_widget.setCurrentIndex(0)
    
    # Connect signals to update dashboard when data changes
    main_window.standard_model.layoutChanged.connect(dashboard_widget.update_data)
    main_window.shareable_model.layoutChanged.connect(dashboard_widget.update_data)
    
    return dashboard_widget