from kivy.app import App
from kivy.graphics import Color, Rectangle
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.scatter import Scatter
from kivy.core.window import Window

windowSize = (600, 1024)
gridColors = [(0.5,0.5,0.5,0.5), (0,0,1,0.5), (0,1,0,0.5), (0,1,1,0.5), (1,0,0,0.5), (1,1,0,0.5), (0.1,0.1,0.1,0.5)]
initialGridSize = 10

class Grid(GridLayout):
    layout: list[str]
    elementLayout: list = []
    squareSize: int = windowSize[0]
    selectedSlot: int = 0

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        temp = min(windowSize[0], windowSize[1])
        self.size = (temp, temp)
        self.cols = initialGridSize
        self.updateStats()

        self.layout = ["0" for i in range(self.cols ** 2)]
        with self.canvas:
            Color(rgba=gridColors[0])
            for i in range(self.cols):
                for j in range(self.cols):
                    self.elementLayout.append(Rectangle(pos=(j * self.squareSize, i * self.squareSize), size=(self.squareSize, self.squareSize)))
                
    def updateStats(self):
        self.squareSize = self.size[0] / self.cols
        print(self.squareSize)
        

    def on_touch_move(self, touch):
        super().on_touch_move(touch)

        relPos = (touch.pos[0] - self.pos[0], touch.pos[1] - self.pos[0])
        if (relPos[0] < 0 or relPos[1] < 0 or relPos[0] >= self.size[0] or relPos[1] >= self.size[1]):
            return
        tempGridPos = (int(relPos[0] / self.squareSize), int(relPos[1] / self.squareSize))
        print(tempGridPos)
        self.canvas.remove(self.elementLayout[tempGridPos[0] + self.cols * tempGridPos[1]])
        with self.canvas:
            Color(rgba=gridColors[self.selectedSlot])
            self.elementLayout[tempGridPos[0] + self.cols * tempGridPos[1]] = Rectangle(pos=(tempGridPos[0] * self.squareSize, tempGridPos[1] * self.squareSize), size=(self.squareSize, self.squareSize))
        self.layout[tempGridPos[0] + self.cols * tempGridPos[1]] = str(self.selectedSlot)


class GridView(Scatter):
    grid = Grid()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.do_rotation = False
        self.do_translation = False
        self.do_scale = False
        self.auto_bring_to_front = False
        self.scale_min = 0.5
        self.scale_max = 2.0
        
        self.add_widget(self.grid)
    pass

class SlotSelectButton(Button):
    slotNumber: int

    def __init__(self, slotNumber: int, **kwargs):
        super().__init__(**kwargs)
        self.slotNumber = slotNumber

class GridSpaceWindow(BoxLayout):
    gridView = GridView()
    selectView = BoxLayout()
    gridSettingsView = BoxLayout()
    gridBgButton = Button(text="Select Background Image")
    gridSizeLabel = Button(text="10", disabled=True)
    gridSizeChangeView = BoxLayout()
    gridSizeUp = Button(text="Up")
    gridSizeDown = Button(text="Down")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "vertical"

        if(self.selectView):
            self.selectView.orientation = "horizontal"
            self.selectView.size_hint_y = 1/6

            self.selectView.add_widget(SlotSelectButton(slotNumber = 0, text="Empty"))
            self.selectView.add_widget(SlotSelectButton(slotNumber = 1, text="Blue", background_color=(0/100, 0/100, 255/100)))
            self.selectView.add_widget(SlotSelectButton(slotNumber = 2, text="Green", background_color=(0/100, 255/100, 0/100)))
            self.selectView.add_widget(SlotSelectButton(slotNumber = 3, text="Cyan", background_color=(0/100, 255/100, 255/100)))
            self.selectView.add_widget(SlotSelectButton(slotNumber = 4, text="Red", background_color=(255/100, 0/100, 0/100)))
            self.selectView.add_widget(SlotSelectButton(slotNumber = 5, text="Yellow", background_color=(255/100, 255/100, 0/100)))
            for button in self.selectView.children:
                button.bind(on_press = self.slotSelect)

        if(self.gridSettingsView):
            self.gridSettingsView.size_hint_y = 1/12

            self.gridBgButton.size_hint_x = 0.8
            self.gridSettingsView.add_widget(self.gridBgButton)
            
            self.gridSizeLabel.size_hint_x = 0.1
            self.gridSettingsView.add_widget(self.gridSizeLabel)
            
            self.gridSizeChangeView.size_hint_x = 0.1
            self.gridSizeChangeView.orientation = "vertical"
            self.gridSizeChangeView.add_widget(self.gridSizeUp)
            self.gridSizeChangeView.add_widget(self.gridSizeDown)
            self.gridSettingsView.add_widget(self.gridSizeChangeView)

        self.add_widget(self.gridView)
        self.add_widget(self.selectView)
        self.add_widget(self.gridSettingsView)

    def slotSelect(self, instance):
        self.gridView.grid.selectedSlot = instance.slotNumber
        print(f"Button Number: {instance.slotNumber} | SelectedSlot: {self.gridView.grid.selectedSlot}")
                                
class DetailsWindow(BoxLayout):
    layoutDetails = BoxLayout()
    layoutText = TextInput()
    layoutGenerateButton = Button(text="Generate\nLayout")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.layoutText.size_hint_x = 0.8
        self.layoutDetails.add_widget(self.layoutText)

        self.layoutGenerateButton.size_hint_x = 0.2
        self.layoutDetails.add_widget(self.layoutGenerateButton)
        self.layoutGenerateButton.bind(on_release = self.generateLayout)

        self.add_widget(self.layoutDetails)     

    def generateLayout(self, instance):
        curApp = App.get_running_app()
        string = ""
        grid = curApp.root.gridSpace.gridView.grid
        for i in range(grid.cols-1, -1, -1):
            for j in range(grid.cols):
                string += grid.layout[i * grid.cols + j]
        self.layoutText.text = "\"Layout\": \"" + string + "\","

class MainWindow(BoxLayout):
    gridSpace = GridSpaceWindow()
    details = DetailsWindow()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.orientation = "vertical"

        self.details.size_hint_y = 1/6

        self.add_widget(self.gridSpace)
        self.add_widget(self.details)

class DBE(App):
    def build(self):
        return MainWindow()
    
if __name__ == '__main__' :
    Window.size = windowSize
    DBE().run()
