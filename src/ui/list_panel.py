#!/usr/bin/env python3
"""
List panel for D3-Mind-Flow-Editor saved diagrams
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QListWidget, QListWidgetItem,
    QPushButton, QLabel, QLineEdit, QComboBox, QMenu, QMessageBox
)
from PySide6.QtCore import Qt, Signal, QTimer
from PySide6.QtGui import QAction

from ..database.models import Diagram, DiagramType
from ..database.db_manager import DatabaseManager
from ..utils.logger import logger


class DiagramListItem(QListWidgetItem):
    """Custom list item for diagrams"""
    
    def __init__(self, diagram: Diagram):
        super().__init__()
        self.diagram = diagram
        self._update_display()
    
    def _update_display(self):
        """Update display text and tooltip"""
        # Format: "Title (Type) - Description"
        type_name = DiagramType.display_names().get(self.diagram.diagram_type, self.diagram.diagram_type)
        display_text = f"{self.diagram.title} ({type_name})"
        
        if self.diagram.description:
            display_text += f" - {self.diagram.description[:50]}"
            if len(self.diagram.description) > 50:
                display_text += "..."
        
        self.setText(display_text)
        
        # Detailed tooltip
        tooltip = f"""タイトル: {self.diagram.title}
種類: {type_name}
説明: {self.diagram.description}
作成日: {self.diagram.created_at.strftime('%Y-%m-%d %H:%M') if self.diagram.created_at else 'N/A'}
更新日: {self.diagram.updated_at.strftime('%Y-%m-%d %H:%M') if self.diagram.updated_at else 'N/A'}"""
        
        self.setToolTip(tooltip)


class ListPanel(QWidget):
    """Panel for displaying saved diagrams list"""
    
    # Signals
    diagram_selected = Signal(Diagram)
    diagram_deleted = Signal(int)
    
    def __init__(self, db_manager: DatabaseManager):
        super().__init__()
        
        self.db_manager = db_manager
        
        # Search timer for debouncing
        self.search_timer = QTimer()
        self.search_timer.setSingleShot(True)
        self.search_timer.timeout.connect(self._perform_search)
        
        self._setup_ui()
        self._setup_connections()
        self.refresh()
        
        logger.debug("List panel initialized")
    
    def _setup_ui(self):
        """Setup UI layout"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        
        # Header
        header_layout = QHBoxLayout()
        
        title_label = QLabel("保存済み図表")
        title_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        header_layout.addWidget(title_label)
        
        header_layout.addStretch()
        
        # Refresh button
        self.refresh_button = QPushButton("🔄")
        self.refresh_button.setToolTip("リストを更新")
        self.refresh_button.setMaximumWidth(30)
        header_layout.addWidget(self.refresh_button)
        
        layout.addLayout(header_layout)
        
        # Filter controls
        filter_layout = QVBoxLayout()
        
        # Search box
        search_layout = QHBoxLayout()
        search_label = QLabel("検索:")
        search_layout.addWidget(search_label)
        
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("タイトルまたは説明で検索")
        search_layout.addWidget(self.search_edit)
        
        filter_layout.addLayout(search_layout)
        
        # Type filter
        type_layout = QHBoxLayout()
        type_label = QLabel("種類:")
        type_layout.addWidget(type_label)
        
        self.type_combo = QComboBox()
        self.type_combo.addItem("すべて", "")
        display_names = DiagramType.display_names()
        for type_key, display_name in display_names.items():
            self.type_combo.addItem(display_name, type_key)
        type_layout.addWidget(self.type_combo)
        
        filter_layout.addLayout(type_layout)
        
        layout.addLayout(filter_layout)
        
        # List widget
        self.list_widget = QListWidget()
        self.list_widget.setAlternatingRowColors(True)
        self.list_widget.setContextMenuPolicy(Qt.CustomContextMenu)
        layout.addWidget(self.list_widget)
        
        # Statistics label
        self.stats_label = QLabel()
        self.stats_label.setStyleSheet("color: gray; font-size: 11px;")
        layout.addWidget(self.stats_label)
        
        # Bottom buttons
        button_layout = QHBoxLayout()
        
        self.load_button = QPushButton("読み込み")
        self.load_button.setEnabled(False)
        self.load_button.setToolTip("選択した図を読み込み")
        button_layout.addWidget(self.load_button)
        
        self.duplicate_button = QPushButton("複製")
        self.duplicate_button.setEnabled(False)
        self.duplicate_button.setToolTip("選択した図を複製")
        button_layout.addWidget(self.duplicate_button)
        
        self.delete_button = QPushButton("削除")
        self.delete_button.setEnabled(False)
        self.delete_button.setToolTip("選択した図を削除")
        self.delete_button.setStyleSheet("QPushButton { color: #d32f2f; }")
        button_layout.addWidget(self.delete_button)
        
        layout.addLayout(button_layout)
    
    def _setup_connections(self):
        """Setup signal connections"""
        # Search and filter
        self.search_edit.textChanged.connect(self._on_search_changed)
        self.type_combo.currentTextChanged.connect(self.refresh)
        self.refresh_button.clicked.connect(self.refresh)
        
        # List interactions
        self.list_widget.itemClicked.connect(self._on_item_clicked)
        self.list_widget.itemDoubleClicked.connect(self._on_item_double_clicked)
        self.list_widget.customContextMenuRequested.connect(self._show_context_menu)
        self.list_widget.itemSelectionChanged.connect(self._on_selection_changed)
        
        # Buttons
        self.load_button.clicked.connect(self._load_selected)
        self.duplicate_button.clicked.connect(self._duplicate_selected)
        self.delete_button.clicked.connect(self._delete_selected)
    
    def _on_search_changed(self):
        """Handle search text change with debouncing"""
        self.search_timer.start(300)  # 300ms delay
    
    def _perform_search(self):
        """Perform the actual search"""
        self.refresh()
    
    def _on_item_clicked(self, item: QListWidgetItem):
        """Handle item click"""
        if isinstance(item, DiagramListItem):
            logger.debug(f"Diagram clicked: {item.diagram.title}")
    
    def _on_item_double_clicked(self, item: QListWidgetItem):
        """Handle item double click - load diagram"""
        if isinstance(item, DiagramListItem):
            self.diagram_selected.emit(item.diagram)
            logger.debug(f"Diagram double-clicked (loaded): {item.diagram.title}")
    
    def _on_selection_changed(self):
        """Handle selection change"""
        has_selection = bool(self.list_widget.currentItem())
        self.load_button.setEnabled(has_selection)
        self.duplicate_button.setEnabled(has_selection)
        self.delete_button.setEnabled(has_selection)
    
    def _show_context_menu(self, position):
        """Show context menu"""
        item = self.list_widget.itemAt(position)
        if not isinstance(item, DiagramListItem):
            return
        
        menu = QMenu(self)
        
        # Load action
        load_action = QAction("読み込み", self)
        load_action.triggered.connect(lambda: self.diagram_selected.emit(item.diagram))
        menu.addAction(load_action)
        
        menu.addSeparator()
        
        # Duplicate action
        duplicate_action = QAction("複製", self)
        duplicate_action.triggered.connect(lambda: self._duplicate_diagram(item.diagram))
        menu.addAction(duplicate_action)
        
        # Delete action
        delete_action = QAction("削除", self)
        delete_action.triggered.connect(lambda: self._delete_diagram(item.diagram))
        menu.addAction(delete_action)
        
        menu.exec(self.list_widget.mapToGlobal(position))
    
    def _load_selected(self):
        """Load selected diagram"""
        current_item = self.list_widget.currentItem()
        if isinstance(current_item, DiagramListItem):
            self.diagram_selected.emit(current_item.diagram)
    
    def _duplicate_selected(self):
        """Duplicate selected diagram"""
        current_item = self.list_widget.currentItem()
        if isinstance(current_item, DiagramListItem):
            self._duplicate_diagram(current_item.diagram)
    
    def _delete_selected(self):
        """Delete selected diagram"""
        current_item = self.list_widget.currentItem()
        if isinstance(current_item, DiagramListItem):
            self._delete_diagram(current_item.diagram)
    
    def _duplicate_diagram(self, diagram: Diagram):
        """Duplicate a diagram"""
        try:
            # Create new diagram with same content
            new_diagram = Diagram(
                title=f"{diagram.title} (複製)",
                description=diagram.description,
                diagram_type=diagram.diagram_type,
                mermaid_data=diagram.mermaid_data,
                node_styles=diagram.node_styles
            )
            
            # Save to database
            diagram_id = self.db_manager.save_diagram(new_diagram)
            
            # Refresh list
            self.refresh()
            
            logger.info(f"Diagram duplicated: {diagram.title} -> ID: {diagram_id}")
            QMessageBox.information(self, "成功", f"図「{diagram.title}」を複製しました。")
            
        except Exception as e:
            error_msg = f"複製に失敗しました: {e}"
            logger.error(error_msg)
            QMessageBox.critical(self, "エラー", error_msg)
    
    def _delete_diagram(self, diagram: Diagram):
        """Delete a diagram with confirmation"""
        reply = QMessageBox.question(
            self, "削除確認", 
            f"図「{diagram.title}」を削除しますか？\\n\\nこの操作は取り消せません。",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                success = self.db_manager.delete_diagram(diagram.id)
                
                if success:
                    self.refresh()
                    self.diagram_deleted.emit(diagram.id)
                    logger.info(f"Diagram deleted: {diagram.title} (ID: {diagram.id})")
                    QMessageBox.information(self, "成功", f"図「{diagram.title}」を削除しました。")
                else:
                    QMessageBox.warning(self, "警告", "図が見つかりませんでした。")
                    
            except Exception as e:
                error_msg = f"削除に失敗しました: {e}"
                logger.error(error_msg)
                QMessageBox.critical(self, "エラー", error_msg)
    
    def refresh(self):
        """Refresh the diagram list"""
        try:
            # Get search and filter criteria
            search_query = self.search_edit.text().strip()
            filter_type = self.type_combo.currentData()
            
            # Get diagrams from database
            if search_query:
                diagrams = self.db_manager.search_diagrams(search_query)
                # Additional filter by type if specified
                if filter_type:
                    diagrams = [d for d in diagrams if d.diagram_type == filter_type]
            else:
                diagrams = self.db_manager.get_all_diagrams(filter_type if filter_type else None)
            
            # Clear and populate list
            self.list_widget.clear()
            
            for diagram in diagrams:
                item = DiagramListItem(diagram)
                self.list_widget.addItem(item)
            
            # Update statistics
            self._update_statistics(len(diagrams))
            
            logger.debug(f"List refreshed: {len(diagrams)} diagrams loaded")
            
        except Exception as e:
            error_msg = f"リスト更新に失敗しました: {e}"
            logger.error(error_msg)
            self.stats_label.setText(f"エラー: {e}")
    
    def _update_statistics(self, visible_count: int):
        """Update statistics display"""
        try:
            stats = self.db_manager.get_statistics()
            total_count = stats['total_count']
            
            # Create stats text
            if visible_count == total_count:
                stats_text = f"合計 {total_count} 件"
            else:
                stats_text = f"{visible_count} / {total_count} 件"
            
            # Add type breakdown if showing all
            if visible_count == total_count and total_count > 0:
                type_counts = stats['type_counts']
                type_parts = []
                for type_key, count in type_counts.items():
                    if count > 0:
                        type_name = DiagramType.display_names().get(type_key, type_key)
                        type_parts.append(f"{type_name}: {count}")
                
                if type_parts:
                    stats_text += f" ({', '.join(type_parts)})"
            
            self.stats_label.setText(stats_text)
            
        except Exception as e:
            logger.warning(f"Failed to update statistics: {e}")
            self.stats_label.setText(f"統計更新エラー: {e}")
    
    def get_selected_diagram(self) -> Diagram:
        """Get currently selected diagram"""
        current_item = self.list_widget.currentItem()
        if isinstance(current_item, DiagramListItem):
            return current_item.diagram
        return None
    
    def select_diagram(self, diagram_id: int):
        """Select diagram by ID"""
        for i in range(self.list_widget.count()):
            item = self.list_widget.item(i)
            if isinstance(item, DiagramListItem) and item.diagram.id == diagram_id:
                self.list_widget.setCurrentItem(item)
                break