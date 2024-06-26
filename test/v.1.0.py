import sys
import json
import csv
from datetime import datetime
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QMessageBox, QTabWidget, QLabel, QListWidget, QListWidgetItem, QStatusBar, QHBoxLayout
)
from PyQt5.QtGui import QFont, QIcon, QPixmap
from PyQt5.QtCore import QUrl, QByteArray, QTimer, Qt
from PyQt5.QtNetwork import QNetworkAccessManager, QNetworkRequest, QNetworkReply


from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox)
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import pyqtSignal, Qt

class LoginWindow(QWidget):
    login_successful = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Inicio de Sesión")
        self.setGeometry(550, 300, 280, 360)

        layout = QVBoxLayout()

        # Logo
        logo_label = QLabel()
        pixmap = QPixmap("app/logo.png").scaled(180, 180, Qt.KeepAspectRatio)
        logo_label.setPixmap(pixmap)
        logo_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(logo_label)

        # Etiquetas personalizadas de "Usuario" y "Contraseña"
        user_label = QLabel("Usuario")
        password_label = QLabel("Contraseña")
        
        # Configura estilos con el método setStyleSheet
        self.setStyleSheet("""
            QWidget {
                background-color: #ffffff;
            }
            QLabel {
                font-size: 28px;
                color: #34495e;
                margin-bottom: 10px;
            }
            QLineEdit {
                font-size: 28px;
                padding: 20px;
                margin: 10px 0;
                border: 2px solid #2980b9;
                border-radius: 8px;
                background-color: #f0f4f8;
            }
            QPushButton {
                background-color: #2980b9;
                color: #ffffff;
                border-radius: 8px;
                font-size: 40px;
                height: 60px;
                margin-top: 15px;
            }
        """)

        # Campo de entrada de "Usuario"
        layout.addWidget(user_label)
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Escribe tu usuario")
        layout.addWidget(self.username_input)

        # Campo de entrada de "Contraseña"
        layout.addWidget(password_label)
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Escribe tu contraseña")
        self.password_input.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.password_input)

        # Botón de inicio de sesión
        login_button = QPushButton("Iniciar Sesión")
        login_button.clicked.connect(self.login)
        layout.addWidget(login_button)

        self.setLayout(layout)

    def login(self):
        username = self.username_input.text()
        password = self.password_input.text()
        if username == "ficosa_pideu" and password == "1111":
            self.login_successful.emit()
            self.close()
        else:
            QMessageBox.warning(self, "Error de Inicio de Sesión", "Usuario o contraseña incorrectos")





















class TicketManagement(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.network_manager = QNetworkAccessManager(self)
        self.network_manager.finished.connect(self.on_network_reply)
        self.last_incidence = None
        self.csv_file = 'Incidencias_Pideu.csv'

    def initUI(self):
        self.setWindowTitle("Ticket Management")
        self.setGeometry(100, 100, 1200, 800)
        # Añadir una etiqueta global para la última incidencia en la barra de estado
        self.global_last_incidence_label = QLabel("Última incidencia confirmada: N/A")
        self.global_last_incidence_label.setFont(QFont('Arial', 12))

        self.status_bar = QStatusBar(self)
        self.status_bar.addWidget(self.global_last_incidence_label)  # Incluir la etiqueta en la barra de estado
        self.setStatusBar(self.status_bar)
        self.update_status_bar()

        timer = QTimer(self)
        timer.timeout.connect(self.update_status_bar)
        timer.start(1000)

        self.tabWidget = QTabWidget(self)
        self.setCentralWidget(self.tabWidget)
        self.status_bar = QStatusBar(self)
        self.setStatusBar(self.status_bar)
        self.update_status_bar()

        timer = QTimer(self)
        timer.timeout.connect(self.update_status_bar)
        timer.start(1000)

        # Definición de incidencias
        self.incidencias = {
            "WC47 NACP": ["Etiquetadora", "Fallo en elevador", "No atornilla tapa", "Fallo tolva",
                        "Fallo en paletizador", "No coge placa", "Palet atascado en la curva",
                        "Ascensor no sube", "No pone tornillo", "Fallo tornillo", "AOI no detecta pieza",
                        "No atornilla clips", "Fallo fijador tapa", "Secuencia atornillador",
                        "Fallo atornillador", "Fallo cámara visión"],
            "WC48 POWER 5F": ["Etiquetadora","AOI (fallo etiqueta)","AOI (malla)","Cámara no detecta Pcb","Cámara no detecta skeleton",
                        "Cámara no detecta foams","Cámara no detecta busbar","Cámara no detecta foam derecho","No detecta presencia power CP",
                        "Tornillo atascado en tolva","Cámara no detecta Power CP","Cámara no detecta Top cover","Detección de sealling mal puesto",
                        "Robot no coge busbar","Fallo etiqueta","Power atascado en prensa, cuesta sacar","No coloca bien el sealling"],
            "WC49 POWER 5H": ["La cámara no detecta Busbar","La cámara no detecta Top Cover","Screw K30 no lo detecta puesto","Atasco tuerca",
                        "Tornillo atascado","Etiquetadora","Detección de sealling mal puesto","No coloca bien el sealling","Power atascado en prensa, cuesta sacar",
                        "No lee QR"],
            "WV50 FILTER": ["Fallo cámara ferrite","NOK Soldadura Plástico","NOK Soldadura metal","Traza","NOK Soldad. Plástico+Metal","Robot no coloca bien filter en palet",
                        "No coloca bien la pcb","QR desplazado","Core enganchado","Robot no coge PCB","Fallo atornillador","Pieza enganchada en HV Test","Cover atascado",
                        "Robot no coloca bien ferrita","No coloca bien el core","Fallo Funcional","Fallo visión core","Fallo cámara cover","Repeat funcional","Fallo cámara QR",
                        "No coloca bien foam"],
            "SPL": ["Sensor de PCB detecta que hay placa cuando no la hay","No detecta marcas Power","Colisión placas","Fallo dispensación glue","Marco atascado en parte inferior",
                    "Soldadura defectuosa","Error en sensor de salida"] 
        }

        for name, incidences in self.incidencias.items():
            self.create_tab(name, incidences)

    def create_tab(self, name, incidences):
        tab = QWidget()
        self.tabWidget.addTab(tab, name)
        layout = QVBoxLayout(tab)

        title = QLabel(f"Incidencias - {name}")
        title.setFont(QFont('Arial', 16))
        layout.addWidget(title)

        listWidget = QListWidget()
        for incidence in incidences:
            item = QListWidgetItem(QIcon("app\logo.png"), incidence)
            item.setFont(QFont('Arial', 12))
            listWidget.addItem(item)
        layout.addWidget(listWidget)

        buttonLayout = QHBoxLayout()

        # Botón confirmar
        confirmButton = QPushButton("Confirmar")
        confirmButton.setIcon(QIcon("app\logo.png"))
        confirmButton.clicked.connect(lambda: self.on_confirm(name, listWidget.currentItem().text() if listWidget.currentItem() else ""))
        buttonLayout.addWidget(confirmButton)

        # Logo FICOSA más grande y alineado
        logoLabel = QLabel()
        pixmap = QPixmap("app\logo.png")  # Ruta del logo
        logoLabel.setPixmap(pixmap)
        logoLabel.setScaledContents(True)
        logoLabel.setMaximumSize(600, 60)  # Tamaño ajustado más grande
        buttonLayout.addWidget(logoLabel, 0, Qt.AlignRight | Qt.AlignBottom)

        layout.addLayout(buttonLayout)

        self.last_incidence_label = QLabel("Última incidencia confirmada: N/A")
        layout.addWidget(self.last_incidence_label)

    def on_confirm(self, name, incidence):
        if incidence:
            response = QMessageBox.question(self, "Confirmar Incidencia", f"¿Estás seguro de confirmar la incidencia '{incidence}' en {name}?", QMessageBox.Yes | QMessageBox.No)
            if response == QMessageBox.Yes:
                self.last_incidence = {"bloque": name, "incidencia": incidence, "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
                self.update_last_incidence()
                self.send_data_to_api(name, incidence)
                self.write_to_csv(name, incidence)
        else:
            QMessageBox.warning(self, "Selección Vacía", "Por favor, selecciona una incidencia.")
        self.update_last_incidence()

    def send_data_to_api(self, block, incidence):
        data = {"bloque": block, "incidencia": incidence}
        url = QUrl("http://fe80::a038:8aec:6233:c933%10:5000/report_incidence")
        req = QNetworkRequest(url)
        req.setHeader(QNetworkRequest.ContentTypeHeader, "application/json")
        self.network_manager.post(req, QByteArray(json.dumps(data).encode('utf-8')))

    def write_to_csv(self, block, incidence):
        with open(self.csv_file, 'a', newline='') as file:
            writer = csv.writer(file)
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            writer.writerow([block, incidence, timestamp])

    def on_network_reply(self, reply):
        err = reply.error()
        if err != QNetworkReply.NoError:
            error_message = reply.errorString()
            QMessageBox.warning(self, "Error de Red", f"Error al comunicar con la API: {error_message}")
        else:
            response = json.loads(reply.readAll().decode())
            QMessageBox.information(self, "Respuesta de la API", response.get("message", "No se recibió mensaje"))

    def update_status_bar(self):
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.status_bar.showMessage(f"Fecha y Hora Actual: {current_time}")

    def update_last_incidence(self):
        if self.last_incidence:
            last_incidence_info = f"Última incidencia confirmada: {self.last_incidence['bloque']} - {self.last_incidence['incidencia']} ({self.last_incidence['timestamp']})"
            self.global_last_incidence_label.setText(last_incidence_info)  # Actualizar la etiqueta global

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = TicketManagement()
    ex.show()
    sys.exit(app.exec_())
