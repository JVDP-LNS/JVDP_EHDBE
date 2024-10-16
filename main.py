from kivy.app import App
from kivy.graphics import Color, Rectangle, Line
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.image import Image
from kivy.uix.button import Button
from kivy.uix.scatter import Scatter
from kivy.core.window import Window
from kivy.uix.layout import Layout
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition
from kivy import platform

if platform == "android":
    from android.permissions import Permission, request_permissions # type: ignore
    request_permissions([Permission.READ_EXTERNAL_STORAGE, Permission.WRITE_EXTERNAL_STORAGE])
    Window.maximize()

windowSize = (450, 800)
gridColors = [(0,0,0,0), (0,0,1,0.5), (0,1,0,0.5), (0,1,1,0.5), (1,0,0,0.5), (1,1,0,0.5), (0.1,0.1,0.1,0.5)]
initialGridSize = 10


class Grid(Layout):
    layout: list[str]
    elementLayout: list
    gridLinesHorizontal: list = []
    gridLinesVertical: list = []
    squareSize: int
    selectedSlot: int = 0
    canvasBG = None
    imageLayout = Scatter(do_rotation = False, rotation = 90, do_scale = False, do_translation = False)
    imageBG = Image()
    cols = initialGridSize

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)

        temp = min(windowSize[0], windowSize[1])
        self.size = (temp, temp)
        self.updateStats()

        with self.canvas:
            Color(rgb=(0.1, 0.1, 0.1))
            self.canvasBG = Rectangle(pos=self.pos, size=(temp, temp)) # Background
        self.imageBG.size = self.size
        self.imageLayout.size = self.size
        self.imageLayout.pos = (self.size[0], 0)
        self.imageLayout.add_widget(self.imageBG)
        self.add_widget(self.imageLayout)

        self.layout = ["0" for i in range(self.cols ** 2)]
        self.elementLayout = [None for i in range(self.cols **2)]
        with self.canvas.after:
            Color(rgb=(0,0,0))
            for i in range(1, self.cols):
                self.gridLinesVertical.append(Line(points=[i * self.squareSize, 0, i * self.squareSize, self.size[1]]))
                self.gridLinesHorizontal.append(Line(points=[0, i * self.squareSize, self.size[1], i * self.squareSize]))
                
    def updateStats(self) -> None:
        self.squareSize = self.size[0] / self.cols

    def increaseGridSize(self, sizeDiff: int) -> None:
        newLayout: list[str] = []
        newElementLayout: list = []
        newCols = self.cols + sizeDiff
        newSquareSize: int = self.size[0] / newCols
        index: int = 0

        for lineV, lineH in zip(self.gridLinesVertical, self.gridLinesHorizontal):
            temp = (index+1) * newSquareSize
            lineV.points = ([temp, 0, temp, self.size[1]])
            lineH.points = ([0, temp, self.size[1], temp])
            index += 1
        
        index = 0
        
        for i in range(sizeDiff):
            for j in range(newCols):
                newLayout.append("0")
                newElementLayout.append(None)
            temp: int = (self.cols + i) * newSquareSize

            with self.canvas.after:
                Color(rgb=(0,0,0))
                self.gridLinesVertical.append(Line(points=[temp, 0, temp, self.size[1]]))
                self.gridLinesHorizontal.append(Line(points=[0, temp, self.size[1], temp]))
            
        for i in range(self.cols):
            for j in range(self.cols):
                newLayout.append(self.layout[index])
                if(self.elementLayout[index]):
                    self.elementLayout[index].pos = (j * newSquareSize, (sizeDiff + i) * newSquareSize)
                    self.elementLayout[index].size = (newSquareSize, newSquareSize)
                newElementLayout.append(self.elementLayout[index])
                index += 1
            for j in range(sizeDiff):
                newLayout.append("0")
                newElementLayout.append(None)
        
        self.cols = newCols
        self.squareSize = newSquareSize
        self.layout = newLayout
        self.elementLayout = newElementLayout

    def decreaseGridSize(self, sizeDiff: int) -> None:
        if(sizeDiff >= self.cols):
            if(self.cols > 1):
                sizeDiff = self.cols - 1
            else: 
                return

        newLayout: list[str] = []
        newElementLayout: list = []
        newCols = self.cols - sizeDiff
        newSquareSize: int = self.size[0] / newCols
        index: int = 0

        for i in range(sizeDiff):
            self.canvas.after.remove(self.gridLinesHorizontal.pop())
            self.canvas.after.remove(self.gridLinesVertical.pop())

        for lineV, lineH in zip(self.gridLinesVertical, self.gridLinesHorizontal):
            temp = (index+1) * newSquareSize
            lineV.points = ([temp, 0, temp, self.size[1]])
            lineH.points = ([0, temp, self.size[1], temp])
            index += 1
        
        index = 0

        for i in range(self.cols):
            for j in range(self.cols):
                if (i < sizeDiff or j >= self.cols - sizeDiff):
                    if(self.elementLayout[index]):
                        self.canvas.remove(self.elementLayout[index])
                else:
                    newLayout.append(self.layout[index])
                    if(self.elementLayout[index]):
                        self.elementLayout[index].pos = (j * newSquareSize, (i - sizeDiff) * newSquareSize)
                        self.elementLayout[index].size = (newSquareSize, newSquareSize)
                    newElementLayout.append(self.elementLayout[index])
                index += 1
        
        self.cols = newCols
        self.squareSize = newSquareSize
        self.layout = newLayout
        self.elementLayout = newElementLayout

    def setGridBG(self, path: str) -> None:
        self.imageBG.source = path
        self.imageLayout.pos = (0,0)

    def hideGridBG(self) -> None:
        self.imageBG.size = (0,0)

    def showGridBG(self) -> None:
        # self.imageBG.size = self.size
        pass

    def on_touch_move(self, touch):
        super().on_touch_move(touch)

        relPos = (touch.pos[0] - self.pos[0], touch.pos[1] - self.pos[0])
        if (relPos[0] < 0 or relPos[1] < 0 or relPos[0] >= self.size[0] or relPos[1] >= self.size[1]):
            return
        tempGridPos = (int(relPos[0] / self.squareSize), int(relPos[1] / self.squareSize))
        print(tempGridPos)
        if(self.elementLayout[tempGridPos[0] + self.cols * tempGridPos[1]]):
            self.canvas.remove(self.elementLayout[tempGridPos[0] + self.cols * tempGridPos[1]])
        if(self.selectedSlot > 0):
            with self.canvas:
                Color(rgba=gridColors[self.selectedSlot])
                self.elementLayout[tempGridPos[0] + self.cols * tempGridPos[1]] = Rectangle(pos=(tempGridPos[0] * self.squareSize, tempGridPos[1] * self.squareSize), size=(self.squareSize, self.squareSize))
        else:
            self.elementLayout[tempGridPos[0] + self.cols * tempGridPos[1]] = None
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
        self.size = (Window.size[0], Window.size[0])
        
        self.add_widget(self.grid)


class SlotSelectButton(Button):
    slotNumber: int

    def __init__(self, slotNumber: int, **kwargs):
        super().__init__(**kwargs)
        self.slotNumber = slotNumber


class GridSpaceWindow(BoxLayout):
    gridView = GridView()
    selectView = BoxLayout()
    gridSettingsView = BoxLayout()
    gridBGButton = Button(text="Select Background Image")
    gridSizeInput = TextInput(text="10", background_color=gridColors[0], foreground_color=(1,1,1), multiline=False)
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

            self.gridBGButton.size_hint_x = 0.8
            self.gridBGButton.bind(on_release=self.getGridBG)
            self.gridSettingsView.add_widget(self.gridBGButton)
            
            self.gridSizeInput.size_hint_x = 0.1
            self.gridSizeInput.bind(on_text_validate=self.gridSizeInputSubmit)
            self.gridSettingsView.add_widget(self.gridSizeInput)
            
            self.gridSizeChangeView.size_hint_x = 0.1
            self.gridSizeChangeView.orientation = "vertical"
            self.gridSizeUp.bind(on_release=self.gridSizeUpFunction)
            self.gridSizeChangeView.add_widget(self.gridSizeUp)
            self.gridSizeDown.bind(on_release=self.gridSizeDownFunction)
            self.gridSizeChangeView.add_widget(self.gridSizeDown)

            self.gridSettingsView.add_widget(self.gridSizeChangeView)

        self.add_widget(self.gridView)
        self.add_widget(self.selectView)
        self.add_widget(self.gridSettingsView)

    def slotSelect(self, instance):
        self.gridView.grid.selectedSlot = instance.slotNumber
        print(f"Button Number: {instance.slotNumber} | SelectedSlot: {self.gridView.grid.selectedSlot}")

    def getGridBG(self, instance):
        from plyer import filechooser
        filechooser.open_file(on_selection=self.imageSelected)

    def imageSelected(self, image):
        if len(image) > 0:
            self.gridView.grid.setGridBG(image[0])
    
    def gridSizeInputSubmit(self, instance):
        grid = self.gridView.grid
        curGridCols = grid.cols
        sizeDiff = int(instance.text) - grid.cols
        if(sizeDiff > 0):
            grid.increaseGridSize(sizeDiff)
        elif(sizeDiff < 0):
            grid.decreaseGridSize(-sizeDiff)
        instance.text = str(grid.cols)

    def gridSizeUpFunction(self, instance):
        grid = self.gridView.grid
        grid.increaseGridSize(1)
        self.gridSizeInput.text = str(grid.cols)

    def gridSizeDownFunction(self, instance):
        grid = self.gridView.grid
        grid.decreaseGridSize(1)
        self.gridSizeInput.text = str(grid.cols)

                                
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
        grid = self.parent.gridSpace.gridView.grid
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
        self.screenManager = ScreenManager()
        self.mainWindow = MainWindow()
        screen = Screen(name="Main Screen")
        screen.add_widget(self.mainWindow)
        self.screenManager.add_widget(screen)
        return self.screenManager
    
if __name__ == '__main__' :
    Window.size = windowSize
    DBE().run()
