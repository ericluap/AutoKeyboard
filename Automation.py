import kivy
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
import Interpreter


class Layout(BoxLayout):
    def run(self):
        Interpreter.run(self.ids.input.text)


class AutomationApp(App):
    def build(self):
        return Layout()


if __name__ == '__main__':
    AutomationApp().run()
