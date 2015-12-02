#!/usr/bin/kivy
from kivy.app import App
from kivy.logger import Logger
from kivy.uix.tabbedpanel import TabbedPanel
from kivy.uix.floatlayout import FloatLayout
from kivy.properties import ObjectProperty
from kivy.properties import StringProperty
from kivy.uix.popup import Popup
from os.path import join
from config import setup_all, insert_newlines, purge_processed, reset_database, setup_folders, setup_db
from spritemapper import analyze_spritesheet, slice_spritesheet


class Root(TabbedPanel):
    def __init__(self):
        super().__init__()
        self.popup = None
        self.new_files = []

    def dismiss_popup(self):
        self.popup.dismiss()

    def split_and_import(self):
        no_newlines = self.ids.path.text.replace('\n', '')
        Logger.info('Import path for file splitting: ' + no_newlines)
        self.new_files = slice_spritesheet(filename=no_newlines,
                                           x_size=int(self.ids.x_px_size.text),
                                           y_size=int(self.ids.y_px_size.text))
        input_dialog = InputDialog(okay=self.dismiss_popup,
                                   message="Enter a descriptive name for this import batch.")
        self.popup = Popup(title="Split and Import: Batch Name", content=input_dialog,
                           size_hint=(0.9, 0.9))
        self.popup.bind(on_dismiss=self.notify_split_complete)
        self.popup.open()

    def notify_split_complete(self, arg):
        info_dialog = InfoDialog(okay=self.dismiss_popup,
                                 message=str(len(self.new_files)) + " tiles have been added to the library.")
        self.popup = Popup(title="Split and Import: Complete", content=info_dialog,
                           size_hint=(0.9, 0.9))
        self.popup.open()

    def show_load(self):

        if is_int(self.ids.x_px_size.text) and is_int(self.ids.y_px_size.text):
            if not self.ids.x_px_size.text or int(self.ids.x_px_size.text) < 1:
                info_dialog = InfoDialog(okay=self.dismiss_popup,
                                         message="You must pick x-pixels per tile.")
                self.popup = Popup(title="Info", content=info_dialog,
                                   size_hint=(0.9, 0.9))
            elif not self.ids.y_px_size.text or int(self.ids.y_px_size.text) < 1:
                info_dialog = InfoDialog(okay=self.dismiss_popup,
                                         message="You must pick y-pixels per tile.")
                self.popup = Popup(title="Info", content=info_dialog,
                                   size_hint=(0.9, 0.9))
            else:
                load_dialog = LoadDialog(load=self.load, cancel=self.dismiss_popup)
                self.popup = Popup(title="Load file", content=load_dialog,
                                   size_hint=(0.9, 0.9))
        else:
            invalid_dialog = InfoDialog(okay=self.dismiss_popup,
                                        message="You must pick valid pixel values.")
            self.popup = Popup(title="Invalid Data", content=invalid_dialog,
                               size_hint=(0.9, 0.9))
        self.popup.open()

    def load(self, path, filename):
        if filename:
            x_tile_size_px = int(self.ids.x_px_size.text)
            y_tile_size_px = int(self.ids.y_px_size.text)
            sheet_data = analyze_spritesheet(join(path, filename[0]), x_tile_size_px, y_tile_size_px)

            sheet_mode = sheet_data[0]
            x_sheet_size_tiles = sheet_data[1]
            y_sheet_size_tiles = sheet_data[2]

            self.ids.path.text = insert_newlines(join(path, filename[0]),
                                                 every=40)
            self.ids.x_tile_size.text = str(x_sheet_size_tiles)
            self.ids.y_tile_size.text = str(y_sheet_size_tiles)
            self.ids.image_mode.text = sheet_mode

            self.ids.import_button.disabled = False

            self.dismiss_popup()

        else:
            self.dismiss_popup()
            info_dialog = InfoDialog(okay=self.dismiss_popup,
                                     message="Could not load file.")
            self.popup = Popup(title="Info", content=info_dialog,
                               size_hint=(0.9, 0.9))

    @staticmethod
    def reset_db():
        reset_database()
        setup_db()

    @staticmethod
    def reset_processed_folder():
        purge_processed()
        setup_folders()


class LoadDialog(FloatLayout):
    load = ObjectProperty(None)
    cancel = ObjectProperty(None)


class InfoDialog(FloatLayout):
    message = StringProperty(None)
    okay = ObjectProperty(None)


class InputDialog(FloatLayout):
    message = StringProperty(None)
    okay = ObjectProperty(None)


class PristineCarrotApp(App):
    pass


def is_int(s):
    s = str(s).strip()
    return s == '0' \
        or (s if s.find('..') > -1
            else s.lstrip('-+').rstrip('0').rstrip('.')).isdigit()


if __name__ == '__main__':
    setup_all()
    PristineCarrotApp().run()
