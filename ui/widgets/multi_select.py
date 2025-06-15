# ui/widgets/multi_select.py
# -*- coding: utf-8 -*-
"""
Custom multi-select widget that allows selecting multiple items from a list.
Can optionally allow adding new items to the list.

Version with extensive debugging and robust handling of checkbox state changes.
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QListWidget, QPushButton,
    QListWidgetItem, QLineEdit, QLabel, QDialog, QDialogButtonBox,
    QCheckBox, QScrollArea, QFrame, QMessageBox
)
from PyQt5.QtCore import Qt, Signal, QSize
from PyQt5.QtGui import QFont

class MultiSelectWidget(QWidget):
    """
    Widget for selecting multiple items from a list.
    Optionally allows adding custom items to the list.
    """
    selectionChanged = Signal(list)
    
    def __init__(self, items=None, allow_adding=False, parent=None):
        """
        Initialize the widget.
        
        Args:
            items (list): List of items to select from
            allow_adding (bool): Whether to allow adding custom items
            parent (QWidget): Parent widget
        """
        super().__init__(parent)
        
        self.items = items or []
        self.allow_adding = allow_adding
        self.selected_items = []
        
        font = QFont("Arial", 10)
        self.setFont(font)

        self.init_ui()
        
    def init_ui(self):
        """Initialize the UI components."""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Selected items display
        self.selection_display = QLineEdit()
        self.selection_display.setReadOnly(True)
        self.selection_display.setFont(QFont("Arial", 10))
        layout.addWidget(self.selection_display, 1)

        # Select button
        self.select_btn = QPushButton("Select...")
        self.select_btn.clicked.connect(self.show_selection_dialog)
        layout.addWidget(self.select_btn)
    
    def set_enabled(self, enable):
        self.selection_display.setEnabled(enable)
        self.select_btn.setEnabled(enable)

    def show_selection_dialog(self):
        """Show the dialog for selecting items."""
        # Create dialog with current selections
        dialog = MultiSelectDialog(
            self.items,
            self.selected_items,
            self.allow_adding,
            self
        )
        
        # Execute the dialog
        result = dialog.exec()
        print(f"Dialog result: {result}, Accepted: {result == QDialog.Accepted}")
        
        if result == QDialog.Accepted:
            # Explicitly get selected items
            new_selected = dialog.get_selected_items()
            
            # Debug
            print(f"New selected items from dialog: {new_selected}")
            
            # Update the widget's selections
            self.selected_items = new_selected.copy()
            
            # Update the display
            self.update_display()
            
            # Emit the selection changed signal
            self.selectionChanged.emit(self.selected_items)
        else:
            print("Dialog was rejected or closed")
            
    def update_display(self):
        """Update the display of selected items."""
        print(f"Updating display with: {self.selected_items}")
        
        if not self.selected_items:
            self.selection_display.setText("")
            self.selection_display.repaint()
            print("Display cleared - no selections")
            return
            
        if len(self.selected_items) <= 3:
            # Show all selected items if there are 3 or fewer
            display_text = ", ".join(self.selected_items)
        else:
            # Show the first 2 items and a count for the rest
            display_text = f"{self.selected_items[0]}, {self.selected_items[1]} +{len(self.selected_items) - 2} more"
            
        print(f"Setting display text to: '{display_text}'")
        self.selection_display.setText(display_text)
        self.selection_display.repaint()  # Force UI update
        
    def set_items(self, items):
        """
        Set the available items.
        
        Args:
            items (list): New list of available items
        """
        self.items = items
        
        # Remove selected items that are no longer in the list
        self.selected_items = [item for item in self.selected_items if item in self.items]
        self.update_display()
        # self.selectionChanged.emit(self.selected_items)
        
    def set_selected_items(self, selected_items):
        """
        Set the selected items.
        
        Args:
            selected_items (list): List of items to select
        """
        # For widgets with allow_adding=True, we accept items not in the original list
        if self.allow_adding:
            self.selected_items = selected_items.copy()
            
            # Add any new items to our items list
            for item in selected_items:
                if item not in self.items:
                    self.items.append(item)
        else:
            # Only select items that are in the available items list
            self.selected_items = [item for item in selected_items if item in self.items]
            
        self.update_display()
        
    def get_selected_items(self):
        """
        Get the selected items.
        
        Returns:
            list: List of selected items
        """
        return self.selected_items.copy()


class MultiSelectDialog(QDialog):
    """
    Dialog for selecting multiple items from a list.
    """
    def __init__(self, items, selected_items, allow_adding, parent=None):
        """
        Initialize the dialog.
        
        Args:
            items (list): List of available items
            selected_items (list): List of currently selected items
            allow_adding (bool): Whether to allow adding custom items
            parent (QWidget): Parent widget
        """
        super().__init__(parent)
        
        self.items = items.copy()
        self.selected_items = selected_items.copy()
        self.allow_adding = allow_adding
        self.checkboxes = {}  # Store checkboxes by item text
        
        self.setWindowTitle("Select Items")
        self.resize(400, 500)
        
        # Debug
        print(f"Dialog initialized with items: {len(self.items)}")
        print(f"Selected items at init: {self.selected_items}")
        
        self.init_ui()
        
    def init_ui(self):
        """Initialize the UI components."""
        layout = QVBoxLayout(self)
        
        # Search box
        search_layout = QHBoxLayout()
        search_layout.addWidget(QLabel("Search:"))
        
        self.search_box = QLineEdit()
        self.search_box.textChanged.connect(self.filter_items)
        search_layout.addWidget(self.search_box)
        
        layout.addLayout(search_layout)
        
        # Select all checkbox
        self.select_all_cb = QCheckBox("Select All")
        self.select_all_cb.clicked.connect(self.toggle_select_all)
        layout.addWidget(self.select_all_cb)
        
        # Items list
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.NoFrame)
        
        self.list_widget = QListWidget()
        self.list_widget.setSelectionMode(QListWidget.NoSelection)
        
        # Add items to the list
        self.populate_list()
        
        scroll_area.setWidget(self.list_widget)
        layout.addWidget(scroll_area)
        
        # Add new item widgets (only shown if allow_adding is True)
        if self.allow_adding:
            add_layout = QHBoxLayout()
            
            self.new_item_edit = QLineEdit()
            self.new_item_edit.setPlaceholderText("Enter new item...")
            add_layout.addWidget(self.new_item_edit)
            
            add_btn = QPushButton("Add")
            add_btn.clicked.connect(self.add_new_item)
            add_layout.addWidget(add_btn)
            
            layout.addLayout(add_layout)
            
        # Dialog buttons
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.on_accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        
    def populate_list(self):
        """Populate the list widget with items."""
        self.list_widget.clear()
        self.checkboxes.clear()
        
        for item_text in self.items:
            item = QListWidgetItem()
            item.setFont(QFont("Arial", 10))
            
            # Create checkbox for this item
            checkbox = QCheckBox(item_text)
            is_checked = item_text in self.selected_items
            checkbox.setChecked(is_checked)
            
            item.setSizeHint(checkbox.sizeHint())

            self.list_widget.addItem(item)

            # Store checkbox for direct access
            self.checkboxes[item_text] = checkbox
            
            # Connect with a custom method that handles sender identification
            checkbox.stateChanged.connect(self.on_checkbox_state_changed)
            
            self.list_widget.setItemWidget(item, checkbox)
            
        # Update select all checkbox
        self.update_select_all()
        
        # Debug
        print(f"Populated list with {len(self.items)} items")
        print(f"Selected items after populate: {self.selected_items}")
            
    def filter_items(self, text):
        """
        Filter items based on search text.
        
        Args:
            text (str): Search text
        """
        for i in range(self.list_widget.count()):
            item = self.list_widget.item(i)
            widget = self.list_widget.itemWidget(item)
            
            if text.lower() in widget.text().lower():
                item.setHidden(False)
            else:
                item.setHidden(True)
                
        # Update select all checkbox
        self.update_select_all()
                
    def on_checkbox_state_changed(self, state):
        """Handle checkbox state change by identifying the sender."""
        # Get the checkbox that sent the signal
        checkbox = self.sender()
        if not checkbox or not isinstance(checkbox, QCheckBox):
            return
            
        item_text = checkbox.text()
        checked = state == Qt.CheckState.Checked
        
        # Debug
        print(f"Checkbox '{item_text}' changed to: {checked}")
        
        # Update selected_items list
        if checked:
            if item_text not in self.selected_items:
                self.selected_items.append(item_text)
                print(f"Added '{item_text}' to selected items: {self.selected_items}")
        else:
            if item_text in self.selected_items:
                self.selected_items.remove(item_text)
                print(f"Removed '{item_text}' from selected items: {self.selected_items}")
                
        # Update select all checkbox
        self.update_select_all()
                
    def toggle_select_all(self, checked):
        """
        Toggle all items selection.
        
        Args:
            checked (bool): Whether to check or uncheck all items
        """
        print(f"Toggle select all: {checked}")
        
        # Block signals to avoid multiple updates
        for i in range(self.list_widget.count()):
            item = self.list_widget.item(i)
            checkbox = self.list_widget.itemWidget(item)
            checkbox.blockSignals(True)
            
        # Clear or fill selected_items
        if not checked:
            self.selected_items.clear()
            print("Cleared selected_items")
        else:
            # Only add visible items
            for i in range(self.list_widget.count()):
                item = self.list_widget.item(i)
                checkbox = self.list_widget.itemWidget(item)

                if checkbox:
                    item_text = checkbox.text()
                    
                    if item_text not in self.selected_items:
                        self.selected_items.append(item_text)
                        
            print(f"Selected all visible items: {self.selected_items}")
            
        # Update checkboxes to match selected_items
        for i in range(self.list_widget.count()):
            item = self.list_widget.item(i)
            checkbox = self.list_widget.itemWidget(item)

            if checkbox:
                item_text = checkbox.text()

                if not item.isHidden():
                    checkbox.setChecked(checked)
                else:
                    checkbox.setChecked(False)
                
        # Unblock signals
        for i in range(self.list_widget.count()):
            item = self.list_widget.item(i)
            checkbox = self.list_widget.itemWidget(item)
            checkbox.blockSignals(False)
                
    def update_select_all(self):
        """Update the state of the select all checkbox."""
        # Count visible and selected visible items
        visible_count = 0
        selected_visible_count = 0
        
        for i in range(self.list_widget.count()):
            item = self.list_widget.item(i)
            
            if not item.isHidden():
                visible_count += 1
                widget = self.list_widget.itemWidget(item)
                
                if widget.isChecked():
                    selected_visible_count += 1
                    
        # Update select all checkbox state
        if visible_count == 0:
            self.select_all_cb.setChecked(False)
            self.select_all_cb.setEnabled(False)
        else:
            self.select_all_cb.setEnabled(True)
            self.select_all_cb.setChecked(selected_visible_count == visible_count)
                
    def add_new_item(self):
        """Add a new custom item to the list."""
        new_item = self.new_item_edit.text().strip()
        
        if not new_item:
            return
            
        if new_item in self.items:
            QMessageBox.warning(
                self,
                "Duplicate Item",
                f"The item '{new_item}' already exists in the list."
            )
            return
            
        # Add to items list
        self.items.append(new_item)
        
        # Add to selected items
        self.selected_items.append(new_item)
        print(f"Added new item '{new_item}' to selected items: {self.selected_items}")
        
        # Clear the input
        self.new_item_edit.clear()
        
        # Refresh the list
        self.populate_list()

    def on_accept(self):
        """Custom accept handler to ensure checkboxes are checked correctly."""
        # Final scan of all checkboxes to ensure selected_items is up to date
        self.selected_items.clear()
        
        for i in range(self.list_widget.count()):
            checkbox = self.list_widget.itemWidget(self.list_widget.item(i))
            if checkbox.isChecked():
                self.selected_items.append(checkbox.text())
                
        print(f"Dialog accepted with selections: {self.selected_items}")
        self.accept()
        
    def get_selected_items(self):
        """
        Get the selected items.
        
        Returns:
            list: List of selected items
        """
        # Check again to be absolutely sure
        actual_selected = []
        for i in range(self.list_widget.count()):
            checkbox = self.list_widget.itemWidget(self.list_widget.item(i))
            if checkbox.isChecked():
                actual_selected.append(checkbox.text())
                
        # If there's a mismatch, print a warning and use the actual selections
        if set(actual_selected) != set(self.selected_items):
            print(f"WARNING: Mismatch between tracked selections {self.selected_items} and actual selections {actual_selected}")
            self.selected_items = actual_selected
            
        print(f"Returning selected items: {self.selected_items}")
        return self.selected_items.copy()