import sys
import os
from pathlib import Path
from PyQt5.QtGui import QIcon, QPixmap, QDesktopServices, QCursor, QPalette, QColor
from PyQt5.QtCore import QUrl, Qt, QTextStream, QFile
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QLabel, QLineEdit, QPushButton, QRadioButton, QComboBox, QFileDialog, QGraphicsPixmapItem, QGraphicsScene, QGraphicsView, QMessageBox, QCheckBox
from pytube import YouTube

class YouTubeDownloader(QMainWindow):
    def __init__(self):
        self.palette = QPalette()
        super().__init__()
        self.setWindowTitle("YouTube Video Downloader")
        self.setWindowIcon(QIcon("YTVD.ico"))
        self.resize(700, 300)
        self.init_ui()
    def init_ui(self):
        
        #Theme
        self.themeButton = QCheckBox('Dark Theme', self)
        self.themeButton.setCheckable(True)
        self.themeButton.clicked.connect(self.change_theme)
        self.themeButton.setGeometry(600, 10, 75, 25)
        self.setPalette(self.palette)

        self.read_theme()

        # Video URL
        self.url_label = QLabel("Video URL:", self)
        self.url_label.move(10, 10)
        self.url_entry = QLineEdit(self)
        self.url_entry.setGeometry(100, 10, 400, 20)

        # Resolutions
        self.res_label = QLabel("Select Resolution:", self)
        self.res_label.move(10, 50)
        self.res_combobox = QComboBox(self)
        self.res_combobox.setGeometry(100, 50, 200, 20)

        # Load Resolutions button
        self.load_resolutions_button = QPushButton("Load Resolutions", self)
        self.load_resolutions_button.setGeometry(310, 50, 100, 20)
        self.load_resolutions_button.clicked.connect(self.load_resolutions) 

        # Format
        self.format_label = QLabel("Select Format:", self)
        self.format_label.move(10, 90)
        self.mp4_radio = QRadioButton("mp4", self)
        self.mp4_radio.move(100, 90)
        self.mp4_radio.setChecked(True)
        self.mp3_radio = QRadioButton("mp3", self)
        self.mp3_radio.move(150, 90)
        self.mp3_radio.toggled.connect(self.disable_resolutions)

        # Save Path
        self.path_label = QLabel("Save Path:", self)
        self.path_label.move(10, 130)
        self.path_entry = QLineEdit(self)
        self.path_entry.setGeometry(100, 130, 300, 20)
        self.path_entry.setText(str(self.load_save_path()))

        # Change Path button
        self.change_path_button = QPushButton("Change Path", self)
        self.change_path_button.setGeometry(410, 130, 90, 25)
        self.change_path_button.clicked.connect(self.change_path)

        # Download button
        self.download_button = QPushButton("Download", self)
        self.download_button.setGeometry(200, 170, 100, 20)
        self.download_button.clicked.connect(self.download_video)
    
        # links
        self.scene = QGraphicsScene(self)
        self.view = QGraphicsView(self.scene, self)
        self.view.setGeometry(10, 190, 300, 100)
        self.view.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.view.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.view.setStyleSheet("background: transparent; border: none")
        image_files = ['bmc.png', 'linkedin.png', 'github.png']
        
        for i, filename in enumerate(image_files):
            pixmap = QPixmap(filename).scaled(50, 50)
            pixmap_item = QGraphicsPixmapItem(pixmap)
            pixmap_item.setPos(i * 100, self.view.height() - pixmap.height())
            pixmap_item.setCursor(QCursor(Qt.PointingHandCursor))
            self.scene.addItem(pixmap_item)
            pixmap_item.mousePressEvent = lambda event, file=filename: self.open_url(event, file)
            
    #Functions
    def change_theme (self):
        if self.themeButton.isChecked():
            self.palette.setColor(QPalette.Window, QColor(18, 18, 18))
            self.palette.setColor(QPalette.WindowText, QColor(255, 255, 255))
            self.setPalette(self.palette)
        else:
            self.palette.setColor(QPalette.Window, QColor(255,255,255))
            self.palette.setColor(QPalette.WindowText, QColor(0, 0, 0))
            self.setPalette(self.palette)
        self.save_theme()

    def save_theme(self):
        file = QFile('theme.txt')
        if file.open(QFile.WriteOnly | QFile.Text):
            text = 'black' if self.themeButton.isChecked() else 'white'
            stream = QTextStream(file)
            stream << text
            file.close()

    def read_theme(self):
        with open('theme.txt', 'r') as f:
            theme = f.read()
        if theme  == 'black':
            self.themeButton.setChecked(True)  
            self.change_theme()

    def open_url(self, event, filename):
        if event.button() == Qt.LeftButton:
            if filename == 'bmc.png':
                url = "https://www.buymeacoffee.com/bartue"
            elif filename == 'linkedin.png':
                url = "https://www.linkedin.com/in/bartuekinci"
            elif filename == 'github.png':
                url = "https://www.github.com/emirb42"
            QDesktopServices.openUrl(QUrl(url))
    
    def disable_checkbox(self):
        if self.mp3_radio.isChecked():
            self.load_resolutions_button.setEnabled(False)
            self.res_combobox.setEnabled(False)
        else:
            self.load_resolutions_button.setEnabled(True)
            self.res_combobox.setEnabled(True)

    def disable_resolutions(self):
        if self.mp3_radio.isChecked():
            self.load_resolutions_button.setEnabled(False)
            self.res_combobox.setEnabled(False)
        else:
            self.load_resolutions_button.setEnabled(True)
            self.res_combobox.setEnabled(True)

    def load_resolutions(self):
        if not self.url_entry.text():
            error_dialog = QMessageBox()
            error_dialog.setIcon(QMessageBox.Warning)
            error_dialog.setWindowTitle("Warning")
            error_dialog.setText("Please enter a Video URL first.")
            error_dialog.exec_()
            return
        video_url = self.url_entry.text()
        yt = YouTube(video_url)
        resolutions = [str(stream.resolution) for stream in yt.streams.filter(progressive=True)]
        self.res_combobox.clear()
        self.res_combobox.addItems(resolutions)

    def load_save_path(self):
        save_path = Path.home()
        if Path("path_settings.txt").exists():
            with open("path_settings.txt", "r") as f:
                save_path =f.read()
        self.save_save_path(save_path)
        return save_path

    def save_save_path(self, save_path):
        with open("path_settings.txt", "w") as f:
            f.write(str(save_path))

    def change_path(self):
        save_path = QFileDialog.getExistingDirectory(self, "Select Directory")
        if save_path:
            #It converts / into \\ so Python can work correctly
            save_path = save_path.replace("/", "\\")
            self.path_entry.setText(save_path)
            self.save_save_path(save_path)

    def download_video(self):
        video_url = self.url_entry.text()
        if self.mp4_radio.isChecked():
            format_type = "mp4"
        else:
            format_type = "mp3"
        save_path = self.path_entry.text()

        try:
            yt = YouTube(video_url)
            file_title = yt.title.replace('"', '') # " " karakterlerini kaldır
            if format_type == "mp4":
                video_streams = yt.streams.filter(progressive=True, file_extension='mp4').order_by('resolution')
                selected_resolution = self.res_combobox.currentText()
                selected_stream = video_streams.get_by_resolution(selected_resolution)
                if selected_stream is None:
                   selected_stream = video_streams.get_highest_resolution()
                selected_stream.download(output_path=save_path, filename=f"{file_title}.mp4")

            elif format_type == "mp3":
                audio_streams = yt.streams.filter(only_audio=True)
                audio_stream = audio_streams.first()
                audio_stream.download(output_path=save_path, filename=f"{file_title}.mp3")
        except Exception as e:
            print("Error:", e)



app = QApplication(sys.argv)
window = YouTubeDownloader()
widget = QWidget()
window.show()
sys.exit(app.exec_())