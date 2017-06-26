from PyQt4 import QtCore, QtGui, uic
import cv2
import numpy
import sys
import glob
from datetime import datetime
from gui3 import Ui_MainWindow
import os


class MyForm(QtGui.QMainWindow):
    def __init__(self, parent=None):
        super(MyForm, self).__init__()

        QtGui.QWidget.__init__(self, parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.setWindowTitle('GUI')
        self.ui.startButton.clicked.connect(self.start_clicked)
        self.ui.stopButton.clicked.connect(self.stop_clicked)
        self.ui.selectSaveDirButton.clicked.connect(self.select_save_clicked)
        self.ui.selectProcessDirButton.clicked.connect(self.select_process_clicked)
        self.ui.preprocessButton.clicked.connect(self.face_detection)
        self.ui.classificationButton.clicked.connect(self.emotion_detection)
        self.ui.saveNoteButton.clicked.connect(self.save_note)


        timer1 = QtCore.QTimer(self)
        timer1.timeout.connect(self.open)
        timer1.start(101)  # 30 Hz

        timer2 = QtCore.QTimer(self)
        timer2.timeout.connect(self.save)
        timer2.start(333)  # 1 za sekundu

    def open(self):
        # get data and display
        global cap, frame, faceCascade
        ret, frame = cap.read()

        # Our operations on the frame come here
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = faceCascade.detectMultiScale(
            gray,
            scaleFactor=1.05,
            minNeighbors=8,
            minSize=(55, 55),
            flags=cv2.cv.CV_HAAR_SCALE_IMAGE
        )
        for (x, y, w, h) in faces:

            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)

        height, width, channel = frame.shape
        bytesperline = 3 * width
        qimg = QtGui.QImage(frame, width, height, bytesperline, QtGui.QImage.Format_RGB888)
        image = QtGui.QPixmap.fromImage(qimg)
        if image.isNull():
            QtGui.QMessageBox.information(self, "Image Viewer","Cannot load")
            return
        lbl = QtGui.QLabel(self.ui.graphicsView)
        lbl.setPixmap(image)
        lbl.show()

    def save(self):
        global frame, count, running, save_directory
        if running:
            count += 1
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            # Display the resulting frame
            # cv2.imshow('frame', gray)
            frameTime = datetime.utcnow().strftime('%Y-%m-%d-%H-%M-%S-%f')[:-3]
            print str(save_directory) + '/' + frameTime + '.jpg'
            cv2.imwrite(str(save_directory) + '/' + frameTime + '.jpg', gray)
            self.ui.savedPicsNumber.setText('Ulozeno obrazku: ' + str(count))

    def start_clicked(self):
        global running
        running = True
        self.ui.startButton.setEnabled(False)
        self.ui.startButton.setText('Ukladam...')

    def stop_clicked(self):
        global running
        running = False
        self.ui.startButton.setEnabled(True)
        self.ui.startButton.setText('Start')

    def select_save_clicked(self):
        global save_directory
        save_directory = QtGui.QFileDialog.getExistingDirectory(self, "Vyberte adresar pro ukladani obrazku")
        self.ui.textSavePath.setText(save_directory)

    def select_process_clicked(self):
        global process_directory
        process_directory = QtGui.QFileDialog.getExistingDirectory(self, "Vyberte adresar pro zpracovani obrazku")
        self.ui.textProcessPath.setText(process_directory)

    def face_detection(self):
        global process_directory, save_directory
        faceDet = cv2.CascadeClassifier("haarcascade_frontalface_default.xml")
        faceDet2 = cv2.CascadeClassifier("haarcascade_frontalface_alt2.xml")
        faceDet3 = cv2.CascadeClassifier("haarcascade_frontalface_alt.xml")
        faceDet4 = cv2.CascadeClassifier("haarcascade_frontalface_alt_tree.xml")

        files = glob.glob(str(save_directory) + "\*.jpg")
        print files
        filenumber = 0
        for f in files:
            print f
            face_image = cv2.imread(f)  # Open image
            f_name = f[-24:]
            gray = cv2.cvtColor(face_image, cv2.COLOR_BGR2GRAY)  # Convert image to grayscale

            # Detect face using 4 different classifiers
            face = faceDet.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=10, minSize=(5, 5),
                                            flags=cv2.CASCADE_SCALE_IMAGE)
            face2 = faceDet2.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=10, minSize=(5, 5),
                                              flags=cv2.CASCADE_SCALE_IMAGE)
            face3 = faceDet3.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=10, minSize=(5, 5),
                                              flags=cv2.CASCADE_SCALE_IMAGE)
            face4 = faceDet4.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=10, minSize=(5, 5),
                                              flags=cv2.CASCADE_SCALE_IMAGE)

            # Go over detected faces, stop at first detected face, return empty if no face.
            if len(face) == 1:
                facefeatures = face
            elif len(face2) == 1:
                facefeatures == face2
            elif len(face3) == 1:
                facefeatures = face3
            elif len(face4) == 1:
                facefeatures = face4
            else:
                facefeatures = ""

            # Cut and save face
            for (x, y, w, h) in facefeatures:  # get coordinates and size of rectangle containing face
                print "face found in file: %s" % f
                gray = gray[y:y + h + 10, x:x + w + 10]  # Cut the frame to size

                try:
                    out = cv2.resize(gray, (350, 350))  # Resize face so all images have same size
                    cv2.imwrite(str(process_directory) + '/' + f_name, out)  # Write image
                except:
                    pass  # If error, pass file
            filenumber += 1  # Increment image number

    def emotion_detection(self):
        global process_directory

    def save_note(self):
        global save_directory
        f = open(save_directory + '/f_.txt', 'a')
        text = self.ui.textEditNote.toPlainText()
        f.write(text)

if __name__ == '__main__':
    global save_directory
    faceCascade = cv2.CascadeClassifier("haarcascade_frontalface_default.xml")
    # faceCascade = cv2.CascadeClassifier("lbpcascade_frontalface.xml")
    cap = cv2.VideoCapture(0)
    ret0, frame = cap.read()
    count = 0
    save_directory = os.path.abspath('E:/Emotions')
    running = False
    form_class = uic.loadUiType("gui3.ui")[0]
    app = QtGui.QApplication(sys.argv)
    myapp = MyForm()
    myapp.show()
    sys.exit(app.exec_())
