import logging
import os
import sounddevice as sd
import soundfile as sf
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QGroupBox,
    QPushButton,
    QSlider,
    QComboBox,
    QLabel,
    QStatusBar,
    QListWidget,
    QFileDialog,
    QMessageBox,
    QListWidgetItem,
    QMenuBar,
    QFormLayout,
    QDialog,
    QLineEdit,
    QInputDialog,
    QMenu,
    QDockWidget,
    QTabWidget,
    QCheckBox,
)
from PyQt5.QtCore import Qt, QTimer, QThread, pyqtSignal
from PyQt5.QtGui import QColor

from .audio_chain import AudioChain
from .widgets import JogWheelWidget
from .config import EFFECTS_LIST, SHORTCUTS
from .project_manager import ProjectManager
from .midi import MidiRouter
from .remote_control import RemoteServer
from .timeline import TimelineWidget, PianoRollWidget, AutomationEditor
from .stem_separator import RealTimeStemSeparator
from .groove_assistant import GrooveAssistant
from .sample_recommender import SampleRecommender


class StemThread(QThread):
    finished = pyqtSignal(object)

    def __init__(self, deck, separator, kind):
        super().__init__()
        self.deck = deck
        self.separator = separator
        self.kind = kind

    def run(self):
        stem = self.deck.get_stem(self.kind, self.separator)
        self.finished.emit(stem)

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class MusicaProOmnibusGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Musica Pro Omnibus")
        self.audio_chain = AudioChain()
        self.project_manager = ProjectManager()
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.midi = MidiRouter()
        self.midi.register(self.handle_midi)
        self.remote = RemoteServer(self.audio_chain)
        self.remote.start()
        self.stem_separator = RealTimeStemSeparator()
        self.groove_assistant = GrooveAssistant()
        self.sample_browser = SampleRecommender('samples')
        self.current_pattern = ['kick', None, 'snare', None]
        from ..user_settings import load_settings
        from ..sound_generator import SoundGenerator
        self.settings = load_settings()
        self.sound_gen = SoundGenerator(self.settings['api_key']) if self.settings.get('api_key') else None
        self.init_gui()
        self.audio_chain.configure()
        self.audio_timer = QTimer()
        self.audio_timer.timeout.connect(self.process_audio)
        self.audio_timer.start(50)

    def init_gui(self):
        menubar = QMenuBar(self)
        self.setMenuBar(menubar)

        file_menu = menubar.addMenu("File")
        file_menu.addAction("Save", self.save_project)
        file_menu.addAction("Load", self.load_project)
        file_menu.addAction("Add Clip", self.add_clip)
        self.record_action = file_menu.addAction("Start Recording")
        self.record_action.setCheckable(True)
        self.record_action.triggered.connect(self.toggle_recording)
        file_menu.addAction("Settings", self.open_settings)

        central = QWidget()
        main_layout = QHBoxLayout(central)
        self.setCentralWidget(central)

        left = QVBoxLayout()
        deck_controls = QGroupBox("Deck")
        dc_layout = QVBoxLayout(deck_controls)
        self.play_btn = QPushButton("Play")
        self.play_btn.clicked.connect(self.toggle_play)
        self.load_btn = QPushButton("Load")
        self.load_btn.clicked.connect(self.load_track)
        self.stem_btn = QPushButton("Stems")
        stem_menu = QMenu(self.stem_btn)
        stem_menu.addAction("Sadece Vokal Çal", lambda: self.play_stem('vocals'))
        stem_menu.addAction("Sadece Enstrümanları Çal", lambda: self.play_stem('accompaniment'))
        stem_menu.addAction("Tam Parçayı Çal", self.play_original)
        self.stem_btn.setMenu(stem_menu)
        dc_layout.addWidget(self.play_btn)
        dc_layout.addWidget(self.load_btn)
        dc_layout.addWidget(self.stem_btn)
        self.jog = JogWheelWidget()
        self.jog.jog_moved.connect(lambda v: self.jog_move(v))
        dc_layout.addWidget(self.jog)
        left.addWidget(deck_controls)

        fx_group = QGroupBox("Effects")
        fx_layout = QVBoxLayout(fx_group)
        self.fx_selector = QComboBox()
        self.fx_selector.addItems(EFFECTS_LIST)
        fx_add_btn = QPushButton("Add")
        fx_add_btn.clicked.connect(lambda: self.add_effect(self.fx_selector.currentText()))
        self.fx_list = QListWidget()
        self.fx_list.itemDoubleClicked.connect(lambda item: self.edit_effect(item.text()))
        fx_layout.addWidget(self.fx_selector)
        fx_layout.addWidget(fx_add_btn)
        fx_layout.addWidget(self.fx_list)
        left.addWidget(fx_group)
        main_layout.addLayout(left)

        right = QVBoxLayout()
        player_controls = QGroupBox("Player")
        pc_layout = QVBoxLayout(player_controls)
        self.player_list = QListWidget()
        pc_layout.addWidget(self.player_list)
        load_playlist = QPushButton("Load Playlist")
        load_playlist.clicked.connect(self.load_playlist)
        pc_layout.addWidget(load_playlist)
        self.timeline = TimelineWidget()
        self.piano_roll = PianoRollWidget()
        self.piano_roll.step_clicked.connect(self.toggle_step)
        self.automation_editor = AutomationEditor()
        self.automation_editor.point_added.connect(self.add_automation_point)

        self.detail_tabs = QTabWidget()
        self.detail_tabs.addTab(self.piano_roll, "Piano Roll")
        self.detail_tabs.addTab(self.timeline, "Audio")
        self.detail_tabs.addTab(self.automation_editor, "Automation")

        groove_controls = QHBoxLayout()
        self.groove_style = QComboBox()
        self.groove_style.addItems(["funk", "house"])
        groove_btn = QPushButton("Groove")
        groove_btn.clicked.connect(self.apply_groove)
        self.live_mode = QCheckBox("Live Synth")
        self.live_mode.toggled.connect(lambda v: setattr(self.audio_chain.production_tracks[0], 'live_mode', v))
        groove_controls.addWidget(self.groove_style)
        groove_controls.addWidget(groove_btn)
        groove_controls.addWidget(self.live_mode)

        right.addWidget(self.detail_tabs)
        right.addLayout(groove_controls)
        sample_group = QGroupBox("Ak\u0131ll\u0131 Sample Taray\u0131c\u0131s\u0131")
        sample_layout = QVBoxLayout(sample_group)
        self.sample_list = QListWidget()
        refresh_btn = QPushButton("Yenile")
        refresh_btn.clicked.connect(self.update_sample_browser)
        gen_btn = QPushButton("Ses Üret")
        gen_btn.clicked.connect(self.generate_sound)
        sample_layout.addWidget(self.sample_list)
        sample_layout.addWidget(refresh_btn)
        sample_layout.addWidget(gen_btn)
        right.addWidget(sample_group)
        self.update_sample_browser()
        right.addWidget(player_controls)
        main_layout.addLayout(right)

    def toggle_play(self):
        deck = self.audio_chain.dj_decks[0]
        if deck.playing:
            deck.pause()
            self.play_btn.setText("Play")
        else:
            deck.play()
            self.play_btn.setText("Pause")

    def load_track(self):
        file, _ = QFileDialog.getOpenFileName(self, "Load Track", "", "Audio Files (*.flac *.m4a *.alac *.wav)")
        if file:
            if self.audio_chain.dj_decks[0].load_track(file):
                self.status_bar.showMessage(os.path.basename(file))
            else:
                QMessageBox.critical(self, "Error", "Track could not be loaded")

    def load_playlist(self):
        path = QFileDialog.getExistingDirectory(self, "Playlist Folder")
        if path:
            self.audio_chain.player.load_playlist(path)
            self.player_list.clear()
            for track in self.audio_chain.player.playlist:
                self.player_list.addItem(os.path.basename(track))

    def add_effect(self, name):
        self.audio_chain.effect_rack.add_effect(name)
        self.fx_list.addItem(QListWidgetItem(name))

    def edit_effect(self, name):
        fx = self.audio_chain.effect_rack.get_effect(name)
        if fx is None:
            return
        params = fx.get_params()
        dialog = QDialog(self)
        dialog.setWindowTitle(name)
        form = QFormLayout(dialog)
        widgets = {}
        for key, val in params.items():
            slider = QSlider(Qt.Horizontal)
            slider.setRange(0, 100)
            slider.setValue(int(val * 100) if isinstance(val, float) else int(val))
            form.addRow(key, slider)
            widgets[key] = slider
        ok = QPushButton("OK")
        ok.clicked.connect(dialog.accept)
        form.addRow(ok)
        if dialog.exec_():
            new_params = {
                k: (widgets[k].value() / 100 if isinstance(params[k], float) else widgets[k].value())
                for k in params
            }
            fx.set_params(**new_params)
            self.status_bar.showMessage(f"Effect updated: {name}")

    def jog_move(self, value):
        deck = self.audio_chain.dj_decks[0]
        deck.position = max(0, deck.position + value * 100)

    def process_audio(self):
        block_size = self.audio_chain.device_manager.current_device["default_buffer_size"]
        output = self.audio_chain.process(block_size)
        sd.play(output, self.audio_chain.fs)

    def handle_midi(self, msg):
        if msg.type == 'note_on' and msg.velocity > 0:
            track = self.audio_chain.production_tracks[0]
            pos = self.audio_chain.player.position / self.audio_chain.fs if self.audio_chain.player.playing else 0
            track.add_midi_note(msg.note, msg.velocity, pos, 0.5)
            self.update_piano_roll()
            self.update_timeline()

    def save_project(self):
        name, _ = QFileDialog.getSaveFileName(self, "Save Project", self.project_manager.directory, "Project (*.json)")
        if name:
            base = os.path.splitext(os.path.basename(name))[0]
            self.project_manager.save_project(base, self.audio_chain)
            self.status_bar.showMessage(f"Project saved: {base}")

    def load_project(self):
        name, _ = QFileDialog.getOpenFileName(self, "Load Project", self.project_manager.directory, "Project (*.json)")
        if name:
            base = os.path.splitext(os.path.basename(name))[0]
            self.project_manager.load_project(base, self.audio_chain)
            self.update_piano_roll()
            self.update_timeline()
            self.status_bar.showMessage(f"Project loaded: {base}")

    def play_stem(self, kind: str):
        deck = self.audio_chain.dj_decks[0]
        if deck.audio is None:
            return
        self.status_bar.showMessage("Stem'ler ayrıştırılıyor...")
        thread = StemThread(deck, self.stem_separator, kind)
        thread.finished.connect(lambda stem: self._set_stem(deck, stem, kind))
        thread.start()
        self._stem_thread = thread

    def _set_stem(self, deck, stem, kind):
        if stem is not None:
            deck.audio = stem
            deck.position = 0
            self.status_bar.showMessage(f"Stem playing: {kind}")

    def play_original(self):
        deck = self.audio_chain.dj_decks[0]
        if deck.original_audio is not None:
            deck.audio = deck.original_audio
            deck.position = 0
            self.status_bar.showMessage("Original track playing")

    def apply_groove(self):
        style = self.groove_style.currentText()
        self.current_pattern = self.groove_assistant.suggest(self.current_pattern, style)
        self.update_piano_roll()
        self.status_bar.showMessage(f"Groove applied: {style}")

    def update_sample_browser(self):
        deck = self.audio_chain.dj_decks[0]
        tempo = deck.bpm or 120
        key = deck.key or "C"
        results = self.sample_browser.recommend(tempo, key)
        self.sample_list.clear()
        for name in results:
            self.sample_list.addItem(name)

    def update_piano_roll(self):
        scene = self.piano_roll.scene()
        scene.clear()
        track = self.audio_chain.production_tracks[0]
        for note in track.midi_notes:
            x = note["start"] * 50
            width = note["duration"] * 50
            y = (127 - note["note"]) * 2
            rect = scene.addRect(x, y, width, 2)
            color_val = int(note["velocity"] / 127 * 255)
            rect.setBrush(QColor(color_val, 0, 255 - color_val))

    def toggle_step(self, index: int):
        if index >= len(self.current_pattern):
            self.current_pattern.extend([None] * (index + 1 - len(self.current_pattern)))
        self.current_pattern[index] = None if self.current_pattern[index] else 'kick'
        self.update_piano_roll()

    def toggle_recording(self, checked=False):
        if self.audio_chain.recorder.recording:
            self.audio_chain.stop_recording()
            self.record_action.setText("Start Recording")
            self.status_bar.showMessage("Recording stopped")
        else:
            fname, _ = QFileDialog.getSaveFileName(self, "Save Recording", "", "WAV Files (*.wav)")
            if fname:
                self.audio_chain.start_recording(fname)
                self.record_action.setText("Stop Recording")
                self.status_bar.showMessage(f"Recording to {os.path.basename(fname)}")
            else:
                self.record_action.setChecked(False)

    def add_clip(self):
        file, _ = QFileDialog.getOpenFileName(self, "Add Clip", "", "Audio Files (*.wav *.flac)")
        if file:
            with sf.SoundFile(file) as f:
                audio = f.read()
            self.audio_chain.production_tracks[0].add_clip(audio, 0.0)
            self.update_timeline()
            self.status_bar.showMessage("Clip added")

    def add_automation_point(self, time, value):
        track = self.audio_chain.production_tracks[0]
        track.automation.add_point(time, value)

    def update_timeline(self):
        scene = self.timeline.scene()
        self.timeline.clear_clips()
        track = self.audio_chain.production_tracks[0]
        for clip in track.clips:
            self.timeline.add_waveform(clip['waveform'], clip['start'])

    def generate_sound(self):
        if not self.sound_gen:
            QMessageBox.warning(self, "API Anahtarı", "Önce Ayarlar'dan API anahtarınızı girin.")
            return
        text, ok = QInputDialog.getText(self, "Metinden Ses", "Açıklama girin")
        if ok and text:
            audio, sr = self.sound_gen.generate(text)
            if audio is not None:
                fname = QFileDialog.getSaveFileName(self, "Kaydet", "", "WAV Files (*.wav)")[0]
                if fname:
                    sf.write(fname, audio, sr)
                    self.status_bar.showMessage(f"Ses kaydedildi ({fname})")

    # --------------------------------------------------------------
    def open_settings(self):
        from ..user_settings import load_settings, save_settings
        from ..sound_generator import SoundGenerator
        settings = load_settings()
        dialog = QDialog(self)
        dialog.setWindowTitle("Ayarlar")
        form = QFormLayout(dialog)
        api_edit = QLineEdit(settings.get("api_key", ""))
        share_cb = QCheckBox("Açık Müzik Kütüphanesi'ne katkı sağla")
        share_cb.setChecked(settings.get("share_data", False))
        usage = QLabel(f"Bu ayki API kullanımı: {settings.get('monthly_api_calls',0)}")
        form.addRow("Hugging Face API", api_edit)
        form.addRow(usage)
        form.addRow(share_cb)
        ok = QPushButton("Kaydet")
        ok.clicked.connect(dialog.accept)
        form.addRow(ok)
        if dialog.exec_():
            settings["api_key"] = api_edit.text().strip()
            settings["share_data"] = share_cb.isChecked()
            save_settings(settings)
            if settings["api_key"]:
                self.sound_gen = SoundGenerator(settings["api_key"])
            else:
                self.sound_gen = None

