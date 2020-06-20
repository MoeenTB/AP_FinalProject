import os
import sys
from dateutil.parser import parse
import pandas as pd
from datetime import datetime
from PyQt5 import uic, QtCore, QtWidgets
from PyQt5.QtWidgets import (
    QApplication,
    QFrame,
    QDialog,
    QMainWindow,
    QFileDialog,
    QStyle,
)  # , QHBoxLayout, QVBoxLayout
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtGui import QIcon, QPalette, QImage
from PyQt5.QtCore import QUrl, Qt
from PyQt5.QtMultimediaWidgets import QVideoWidget
from PyQt5.uic import loadUi


Form = uic.loadUiType(os.path.join(os.getcwd(), "gui-intro.ui"))[0]


class LoginPage(QDialog):
    def __init__(self):
        super(LoginPage, self).__init__()
        loadUi("searchtag.ui", self)

    def shows(self, layout):
        data = pd.read_excel("tags.xlsx")
        firstline = pd.DataFrame(data, index=[0])
        if self.tableWidget.currentRow() == 0:
            dt = parse(str(list(firstline)[1]))
            t = str(list(firstline)[1])
        else:
            dt = parse(str(data.iat[self.tableWidget.currentRow(), 1]))
            t = str(data.iat[self.tableWidget.currentRow(), 1])
        pt = datetime.strptime(t, "%H:%M:%S")
        total_seconds = pt.second + pt.minute * 60 + pt.hour * 3600
        layout.videoplayer.setPosition(total_seconds * 1000)


class IntroWindow(QMainWindow, Form):
    def __init__(self):
        Form.__init__(self)
        QMainWindow.__init__(self)
        self.setWindowIcon(QIcon("logo.png"))

        p = self.palette()
        p.setColor(QPalette.Window, Qt.gray)
        self.setPalette(p)

        self.setupUi(self)

        videowidget = QVideoWidget()
        self.vertical.addWidget(videowidget)
        self.videoplayer = QMediaPlayer(None, QMediaPlayer.VideoSurface)
        self.videoplayer.setVideoOutput(videowidget)
        self.sliderfilm.setRange(0, 0)
        self.volume.setRange(0, 100)
        self.videoplayer.setVolume(100)
        self.volume.setValue(100)

        self.play.setEnabled(False)
        self.increaseRate.setEnabled(False)
        self.decreaseRate.setEnabled(False)

        #putting Icons on buttons

        self.increaseRate.setIcon(self.style().standardIcon(QStyle.SP_MediaSeekForward))
        self.decreaseRate.setIcon(self.style().standardIcon(QStyle.SP_MediaSeekBackward))
        self.play.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
        self.open.setIcon(self.style().standardIcon(QStyle.SP_DirHomeIcon))
        self.skipforward.setIcon(self.style().standardIcon(QStyle.SP_MediaSkipForward))
        self.skipback.setIcon(self.style().standardIcon(QStyle.SP_MediaSkipBackward))


        self.sliderfilm.sliderMoved.connect(self.setpos)
        self.videoplayer.positionChanged.connect(self.position)
        self.videoplayer.durationChanged.connect(self.changed)
        self.videoplayer.volumeChanged.connect(self.setvolpos)
        self.volume.sliderMoved.connect(self.setvolpos)
        self.actionOpen.triggered.connect(self.Loadvideo)
        self.actionSearch_By_Tag.triggered.connect(self.opensecond)
        self.actionFullscreen.triggered.connect(self.screen)
        self.skipforward.clicked.connect(self.skipforw)
        self.skipback.clicked.connect(self.skipbac)
        self.increaseRate.clicked.connect(self.incRate)
        self.decreaseRate.clicked.connect(self.decRate)
        self.play.clicked.connect(self.play_video)
        self.open.clicked.connect(lambda: self.Loadvideo(self.videoplayer))
        ####how to hid window flag
        # self.setWindowFlags(Qt.Window | Qt.FramelessWindowHint)
        # self.hide()
        # self.show()

    def mouseDoubleClickEvent(self, cls):
        if not self.isFullScreen():
            self.showFullScreen()
        else:
            self.showNormal()

    def keyPressEvent(self, e):
        if e.key() == Qt.Key_Escape:
            if self.isFullScreen():
                self.showNormal()

    def screen(self):
        if not self.isFullScreen():
            self.showFullScreen()
        else:
            self.showNormal()

    #forward media 5s
    def skipforw(self):
        self.videoplayer.setPosition(self.videoplayer.position()+5000)
    def skipbac(self):
        self.videoplayer.setPosition(self.videoplayer.position()-5000)

         #set increase rate
    def incRate(self):
        if self.videoplayer.playbackRate() == 0:
            x = self.videoplayer.playbackRate() + 1
        else:
            x = self.videoplayer.playbackRate()
        self.videoplayer.setPlaybackRate(x+.25)
    

    #set decrease rate
    def decRate(self):
        if self.videoplayer.playbackRate() == 0:
            x = self.videoplayer.playbackRate() + 1
        else:
            x = self.videoplayer.playbackRate()
        self.videoplayer.setPlaybackRate(x-.25)

    def opensecond(self):
        login_page = LoginPage()
        login_page.setWindowFlags(QtCore.Qt.WindowCloseButtonHint)
        data = pd.read_excel("tags.xlsx")
        firstline = pd.DataFrame(data, index=[0])
        x = pd.DataFrame(data, columns=[list(firstline)[0]])
        login_page.tableWidget.setRowCount(x.size)
        login_page.tableWidget.insertRow(1)
        login_page.tableWidget.setItem(
            0, 0, QtWidgets.QTableWidgetItem(list(firstline)[0])
        )
        login_page.tableWidget.setItem(
            0, 1, QtWidgets.QTableWidgetItem(str(list(firstline)[1]))
        )
        for i in range(x.size):
            for j in range(2):
                login_page.tableWidget.setItem(
                    i + 1, j, QtWidgets.QTableWidgetItem(str(data.iat[i, j]))
                )
        login_page.buttonBox.accepted.connect(lambda: login_page.shows(self))
        login_page.tableWidget.setHorizontalHeaderLabels(["Tag", "Time"])
        login_page.exec_()

    ##setting position of film
    def setpos(self, position):
        self.videoplayer.setPosition(position)

    def position(self, position):
        hour = int((position / 3600000) % 24)
        if hour < 10:
            hour = "0" + str(hour)
        minute = int((position / 60000) % 60)
        if minute < 10:
            minute = "0" + str(minute)
        second = int((position / 1000) % 60)
        if second < 10:
            second = "0" + str(second)
        self.label.setText(f"{hour}:{minute}:{second}")
        self.sliderfilm.setValue(position)

    def changed(self, duration):
        self.sliderfilm.setRange(0, duration)

    ##setting position of volume
    def setvolpos(self, position):
        self.videoplayer.setVolume(position)

    ##stop button
    # def stopp(self):
    #     self.stop.setEnabled(False)
    #     self.play.setText("Start")
    #     self.videoplayer.stop()
    #     self.videoplayer.setPosition(0)

    ##open button or open from menu bar
    def Loadvideo(self, videoplayer):
        filename, _ = QFileDialog.getOpenFileName(self, "Open Video")
        if filename != "":
            self.videoplayer.setPosition(0)
            types = (".mov" in filename) or (".png" in filename) or (".mp4" in filename)
            if types:
                if filename != "":
                    self.videoplayer.setMedia(
                        QMediaContent(QUrl.fromLocalFile(filename))
                    )
                    self.videoplayer.play()
                    self.play.setEnabled(True)
                    self.increaseRate.setEnabled(True)
                    self.decreaseRate.setEnabled(True)

    ##play button
    def play_video(self):
        if self.videoplayer.state() == QMediaPlayer.PlayingState:
            self.play.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
            self.videoplayer.pause()
        else:
            self.videoplayer.play()
            self.play.setIcon(self.style().standardIcon(QStyle.SP_MediaPause))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    w = IntroWindow()
    w.show()
    sys.exit(app.exec_())
