import json
import re
from datetime import datetime, timedelta
from typing import List
import sys
from PyQt5.QtWidgets import QComboBox, QColorDialog, QDialog, QApplication, QWidget, QLabel, QLineEdit, QVBoxLayout, QHBoxLayout, QPushButton, QScrollArea, QGridLayout
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QFont
import re
from datetime import datetime, timedelta
from typing import List, Optional


DEFAULT_LOG_TYPES = ['damage', 'heal']

with open('config.json', 'r') as f:
    config = json.load(f)

LOG_FILE_PATH = config['logFilePath']
LOG_TIME = config['logMinutesAgo']
LOG_TYPE = config.get('logType')
TARGET_NAME = config.get('targetName')
OVERLAY_WIDTH = config['overlayWidth'] if config.get('overlayWidth') else 300
OVERLAY_HEIGHT = config['overlayHeight'] if config.get('overlayWidth') else 300
OVERLAY_OPACITY = config['overlayOpacity'] if config.get('overlayOpacity') else "30%"
OVERLAY_LOG_COLOR = config['overlayLogColor'] if config.get('overlayLogColor') else "lime"

minimize_state = False
scrollbar = None
frame = None
first_exec = True
selected_log_color = OVERLAY_LOG_COLOR

def openColorDialog():
    global selected_log_color
    
    color = QColorDialog.getColor()

    if color.isValid():
        selected_log_color = color.name()
            
def configure():
    # Use the global variables
    global LOG_FILE_PATH, TARGET_NAME, LOG_TIME, DEFAULT_LOG_TYPES

    # Create a dialog to ask for the configuration values
    dialog = QDialog()
    dialog.setWindowFlags(Qt.FramelessWindowHint)
    dialog.setWindowTitle("Settings")
    dialog.setMinimumWidth(300)
    dialog.setFont(QFont('Roboto', 10))
    dialog.setStyleSheet(f"color: white; background-color: rgba( 0, 0, 0, 10%  );")

    # Create the labels and line edits for the configuration values
    label_log_path = QLabel("Log file path:")
    edit_log_path = QLineEdit(LOG_FILE_PATH)
    
    label_overlay_width = QLabel("Overlay width:")
    edit_overlay_width = QLineEdit(str(OVERLAY_WIDTH))    
    
    label_overlay_height = QLabel("Overlay height:")
    edit_overlay_height = QLineEdit(str(OVERLAY_HEIGHT))
    
    label_overlay_opacity = QLabel("Overlay opacity %:")
    edit_overlay_opacity = QLineEdit(str(OVERLAY_OPACITY))

    label_target_name = QLabel("Target name:")
    edit_target_name = QLineEdit(TARGET_NAME)

    label_minutes_ago = QLabel("Minutes ago:")
    edit_minutes_ago = QLineEdit(str(LOG_TIME))

    label_log_type = QLabel("Log type:")
    combobox_log_type = QComboBox()
    combobox_log_type.addItems(DEFAULT_LOG_TYPES)
    combobox_log_type.setStyleSheet(f"color: black; background-color: rgba( 255, 255, 255, 50%  );")
    
    label_log_color = QLabel("Log color:")
    button_color_picker = QPushButton('Select color')
    button_color_picker.clicked.connect(openColorDialog)
    button_color_picker.setStyleSheet(f"color: black; background-color: rgba( 255, 255, 255, 50%  );")

    # Create the OK and Cancel buttons
    ok_button = QPushButton("OK")
    ok_button.setStyleSheet(f"color: black; background-color: rgba( 255, 255, 255, 50%  );")
    
    cancel_button = QPushButton("Cancel")
    cancel_button.setStyleSheet(f"color: black; background-color: rgba( 255, 255, 255, 50%  );")

    # Create a layout for the dialog
    layout = QGridLayout()
    
    # Create a label for the Settings text
    setting_label = QLabel("Settings")
    setting_label.setAlignment(Qt.AlignLeft)
    layout.addWidget(setting_label, 0, 0)
    
    # Create a label for the "by Xizde" text
    by_label = QLabel("by Xizde")
    by_label.setStyleSheet(f"color: {OVERLAY_LOG_COLOR};")
    by_label.setAlignment(Qt.AlignRight)
    layout.addWidget(by_label, 0, 1)

    # Add the labels and line edits to the layout
    layout.addWidget(label_log_path, 1, 0)
    layout.addWidget(edit_log_path, 1, 1)
    
    layout.addWidget(label_overlay_width, 2, 0)
    layout.addWidget(edit_overlay_width, 2, 1)
    
    layout.addWidget(label_overlay_height, 3, 0)
    layout.addWidget(edit_overlay_height, 3, 1)
    
    layout.addWidget(label_overlay_opacity, 4, 0)
    layout.addWidget(edit_overlay_opacity, 4, 1)  
      
    layout.addWidget(label_log_type, 5, 0)
    layout.addWidget(combobox_log_type, 5, 1)

    layout.addWidget(label_target_name, 6, 0)
    layout.addWidget(edit_target_name, 6, 1)

    layout.addWidget(label_minutes_ago, 7, 0)
    layout.addWidget(edit_minutes_ago, 7, 1)
    
    layout.addWidget(label_log_color, 8, 0)
    layout.addWidget(button_color_picker, 8, 1)

    # Add the OK and Cancel buttons to the layout
    layout.addWidget(ok_button, 9, 0)
    layout.addWidget(cancel_button, 9, 1)

    # Set the layout for the dialog
    dialog.setLayout(layout)

    # Set the focus to the OK button
    ok_button.setFocus()

    # Connect the OK and Cancel buttons to their respective functions
    ok_button.clicked.connect(lambda: apply_settings(dialog, edit_log_path, edit_target_name, edit_minutes_ago, edit_overlay_width, edit_overlay_height, edit_overlay_opacity, combobox_log_type.currentText()))
    cancel_button.clicked.connect(dialog.reject)

    # Show the dialog
    dialog.exec_()
    
def exit_application():
    app.quit()

def apply_settings(dialog, edit_log_path, edit_target_name, edit_minutes_ago, edit_overlay_width, edit_overlay_height, edit_overlay_opacity, combobox_log_type):
    # Use the global variables
    global LOG_FILE_PATH, TARGET_NAME, LOG_TIME, OVERLAY_HEIGHT, OVERLAY_WIDTH, OVERLAY_OPACITY, OVERLAY_LOG_COLOR, selected_log_color, LOG_TYPE

    # Update the configuration values
    LOG_FILE_PATH = edit_log_path.text()
    TARGET_NAME = edit_target_name.text()
    LOG_TIME = int(edit_minutes_ago.text())
    LOG_TYPE = combobox_log_type if combobox_log_type else LOG_TYPE
    OVERLAY_HEIGHT = int(edit_overlay_height.text())
    OVERLAY_WIDTH = int(edit_overlay_width.text())
    OVERLAY_OPACITY = edit_overlay_opacity.text()
    OVERLAY_LOG_COLOR = selected_log_color
    
    # Save new settings
    with open('config.json', 'w') as f:
        config = json.dumps({
            "overlayWidth": OVERLAY_WIDTH,
            "overlayHeight": OVERLAY_HEIGHT,
            "overlayOpacity": OVERLAY_OPACITY,
            "overlayLogColor": OVERLAY_LOG_COLOR,
            "logFilePath": LOG_FILE_PATH,
            "logMinutesAgo": LOG_TIME,
            "targetName": TARGET_NAME if TARGET_NAME else "",
            "logType": LOG_TYPE
        }, indent=4)
        f.write(config)
        f.close()
        
    # Close the dialog
    dialog.accept()

def update_widgets_opacity():
    global exit_button, config_button, minimize_button, previous_geometry, scroll_area
    
    config_button.setStyleSheet(f"background-color: rgba( 0, 0, 0, {OVERLAY_OPACITY}%  ); color: white;" );
    exit_button.setStyleSheet(f"background-color: rgba( 0, 0, 0, {OVERLAY_OPACITY}%  ); color: white;" );
    minimize_button.setStyleSheet(f"background-color: rgba( 0, 0, 0, {OVERLAY_OPACITY}%  ); color: white;" );
    scroll_area.setStyleSheet(f"background-color: rgba( 0, 0, 0, {OVERLAY_OPACITY}%  ); color: white;" );
    
    
def extract_attack_data(log_file_path: str, minutes_ago: int = 60, target_name: Optional[str] = None) -> List[dict]:
    # Compile regex pattern
    pattern = re.compile(r"\[(?P<log_time_str>.*?)\] (?P<character>.*?)\|r attacked (?P<receiver>.*?)\|r using.*\|cffff0000\-(?P<total>\d+)")

    # Calculate time range
    end_time = datetime.now()
    start_time = end_time - timedelta(minutes=minutes_ago)

    # Use generator expression to yield attack data
    with open(log_file_path, "r", encoding="utf8") as f:
        yield from (
            {"timestamp": log_time_str, "character": character, "target": receiver, "total": total}
            for line in f
            if "attacked" in line
            for match in [pattern.search(line)]
            if match
            for log_time_str, character, receiver, total in [match.groups()]
            if start_time <= datetime.strptime(log_time_str, "%m/%d/%y %H:%M:%S") <= end_time
            if not target_name or receiver == target_name
        )

def extract_heal_data(log_file_path: str, minutes_ago: int = 60, target_name: Optional[str] = None) -> List[dict]:
    pattern = re.compile(r"\[(?P<log_time_str>[^\]]+)\]\s(?P<character>[^|]+)\|r\stargeted\s(?P<receiver>[^|]+)\|[^|]+\|cff25fcff(?P<ability>[^|]+)\|[^|]+\|cff00ff00(?P<restored>[^|]+)\|r\shealth.")
    end_time = datetime.now()
    start_time = end_time - timedelta(minutes=minutes_ago)
    with open(log_file_path, "r", encoding="utf8") as f:
        yield from (
            {"timestamp": log_time_str, "character": character, "target": receiver, "total": total}
            for line in f
            if "targeted" in line 
            for match in [pattern.search(line)]
            if match
            for log_time_str, character, receiver, _, total in [match.groups()]
            if start_time <= datetime.strptime(log_time_str, "%m/%d/%y %H:%M:%S",) <= end_time
            if not target_name or receiver == target_name
        )
        
def format_number(n) -> str:
    if str(n).lower() in DEFAULT_LOG_TYPES:
        return n
    
    suffixes = ['', 'k', 'M', 'B', 'T']
    i = 0
    while n >= 1000 and i < len(suffixes)-1:
        n /= 1000.0
        i += 1
    if i == 0:
        return str(int(n))
    else:
        return str('{:,.1f}{}'.format(n, suffixes[i]))
    
# Function to update the overlay with the new configuration
def update_overlay():
    # Use the global variables
    global LOG_FILE_PATH, TARGET_NAME, LOG_TIME, scroll_content_layout, minimize_state, previous_geometry
    global first_exec, LOG_TYPE
    update_widgets_opacity()
    
    if first_exec:
        minimize_state = True
        first_exec = False
        
    if not minimize_state:    
        QTimer.singleShot(10, update_overlay)  # update every minute
    else:
        window.setGeometry(0, 0, OVERLAY_WIDTH, OVERLAY_HEIGHT)
        
        # Extract damage / heal based on config LOG_TYPE
        if LOG_TYPE == "damage":
            data_logs = extract_attack_data(log_file_path=LOG_FILE_PATH, minutes_ago=LOG_TIME, target_name=TARGET_NAME)
        elif LOG_TYPE == "heal":
            data_logs = extract_heal_data(log_file_path=LOG_FILE_PATH, minutes_ago=LOG_TIME, target_name=TARGET_NAME)

        # Aggregate the data by attacker
        damage_data = {}
        for log in data_logs:
            character = log["character"]
            if log["total"]:
                total = int(log["total"].replace(",", ""))

            damage_data[character] = damage_data.get(character, 0) + total

        # Sort the data by total in descending order
        sorted_data = sorted(damage_data.items(), key=lambda x: x[1], reverse=True)

        # Clear the layout
        while scroll_content_layout.count():
            child = scroll_content_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        # Setting titles
        sorted_data.insert(0, ("Rank - Name", LOG_TYPE.capitalize()))

        # Display the first 5 rows of sorted data
        for i, (attacker, total) in enumerate(sorted_data):
            label_attacker = QLabel(str(f'{i} {attacker}'))
            if attacker == 'Rank - Name':
                label_attacker = QLabel(str(attacker))
                label_attacker.setStyleSheet(f"color: white; background-color: rgba( 0, 0, 0, {OVERLAY_OPACITY}%  );")
            else:
                label_attacker.setStyleSheet(f"color: {OVERLAY_LOG_COLOR}; background-color: rgba( 0, 0, 0, {OVERLAY_OPACITY}%  );")
            label_attacker.setFont(QFont('Roboto', 10))
            
            label_total = QLabel(format_number(total))
            label_total.setFont(QFont('Roboto', 10))
            if str(total).lower() in DEFAULT_LOG_TYPES:
                label_total.setStyleSheet(f"color: white; background-color: rgba( 0, 0, 0, {OVERLAY_OPACITY}%  );")
            else:
                label_total.setStyleSheet(f"color: {OVERLAY_LOG_COLOR}; background-color: rgba( 0, 0, 0, {OVERLAY_OPACITY}%  );")
                
            scroll_content_layout.addWidget(label_attacker, i, 0)
            scroll_content_layout.addWidget(label_total, i, 1)
        
        update_widgets_opacity()
        # Schedule the next update
        QTimer.singleShot(10000, update_overlay)  # update every minute

def minimize_maximize_overlay():
    global window, minimize_state, scroll_area, previous_geometry, exit_button, config_button, minimize_button, maximize_button
    
    if minimize_state:
        # Save the previous window geometry
        previous_geometry = window.geometry()
        
        # Hide the scroll area and set the window height to 1
        scroll_area.hide()
        exit_button.setVisible(not minimize_state)
        config_button.setVisible(not minimize_state)
        minimize_button.setVisible(not minimize_state)
        maximize_button.setVisible(True)
        window.setGeometry(0, 0, 20, 20)
        minimize_state = False
    elif not minimize_state:   
        # Restore the previous window geometry
        window.setGeometry(previous_geometry)
        
        # Show the scroll area
        scroll_area.show()
        
        exit_button.setVisible(not minimize_state)
        config_button.setVisible(not minimize_state)
        minimize_button.setVisible(not minimize_state)
        maximize_button.setVisible(False)
        minimize_state = True
    
    # Update the overlay
    update_overlay()
        

# Create the GUI window
app = QApplication(sys.argv)

window = QWidget()
window.setGeometry(0, 0, OVERLAY_WIDTH, OVERLAY_HEIGHT)
previous_geometry = window.geometry()
window.setWindowTitle("ArcheRage - Damage/Heal Meter")

window.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)

window.setAttribute(Qt.WA_NoSystemBackground, True)
window.setAttribute(Qt.WA_TranslucentBackground, True)

# Create a vertical layout for the main window
layout = QVBoxLayout()
window.setLayout(layout)

# Create a horizontal layout for the buttons
button_layout = QHBoxLayout()

# Create the Configuration button
minimize_button = QPushButton("-")
minimize_button.setFont(QFont('Roboto', 8))
minimize_button.setStyleSheet(f"background-color: rgba( 0, 0, 0, {OVERLAY_OPACITY}%  ); color: white;" );
minimize_button.clicked.connect(minimize_maximize_overlay)
button_layout.addWidget(minimize_button)

# Create the Exit button
exit_button = QPushButton("Exit")
exit_button.setFont(QFont('Roboto', 8))
exit_button.setStyleSheet(f"background-color: rgba( 0, 0, 0, {OVERLAY_OPACITY}%  ); color: white;" );
exit_button.clicked.connect(exit_application)
button_layout.addWidget(exit_button)

# Create the Configuration button
config_button = QPushButton("Settings")
config_button.setFont(QFont('Roboto', 8))
config_button.setStyleSheet(f"background-color: rgba( 0, 0, 0, {OVERLAY_OPACITY}%  ); color: white;" );
config_button.clicked.connect(configure)
button_layout.addWidget(config_button)

# Add the button layout to the main layout
layout.addLayout(button_layout)

# Create the Configuration button
maximize_button = QPushButton("+")
maximize_button.setFont(QFont('Roboto', 8))
maximize_button.setStyleSheet(f"background-color: rgba( 0, 0, 0, {OVERLAY_OPACITY}%  ); color: white;" );
maximize_button.clicked.connect(minimize_maximize_overlay)
maximize_button.setVisible(False)
layout.addWidget(maximize_button)
    
# Create a scroll area for the data
scroll_area = QScrollArea()
scroll_content = QWidget()
scroll_content_layout = QGridLayout()
scroll_content.setLayout(scroll_content_layout)
scroll_area.setStyleSheet(f"background-color: rgba( 0, 0, 0, {OVERLAY_OPACITY}% );" );

scroll_area.setWidget(scroll_content)
scroll_area.setWidgetResizable(True)

layout.addWidget(scroll_area)

# Schedule the first update
QTimer.singleShot(0, update_overlay)

# Show the window and start the event loop
window.show()
sys.exit(app.exec_())