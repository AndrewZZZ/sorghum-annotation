import wx
import wx.xrc
from wx.lib.evtmgr import eventManager
from CanvasPanel import CanvasPanel
import platform

class View ( wx.Frame ):

    def __init__( self, parent ):
        wx.Frame.__init__ ( self, parent, id = wx.ID_ANY, title = wx.EmptyString, pos = wx.DefaultPosition, size = wx.Size( 722,470 ), style = wx.DEFAULT_FRAME_STYLE|wx.TAB_TRAVERSAL )


        self.fileNameList = []

        self.SetSizeHints( wx.DefaultSize, wx.DefaultSize )

        self.statusBar = self.CreateStatusBar( 1, wx.STB_SIZEGRIP, wx.ID_ANY )
        self.menuBar = wx.MenuBar( 0 )
        self.menuFile = wx.Menu()
        self.menuFile.Append(101, 'Open')
        self.menuFile.Append(102, 'Save')
        self.menuBar.Append(self.menuFile, 'File')
        self.SetMenuBar( self.menuBar )

        mainGbSizer = wx.GridBagSizer( 5, 5 )
        mainGbSizer.SetFlexibleDirection( wx.BOTH )
        mainGbSizer.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_ALL )

        self.horToolBar = wx.ToolBar( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TB_HORIZONTAL )
        self.horToolBar.AddSeparator()

        self.thresholdLabel = wx.StaticText( self.horToolBar, wx.ID_ANY, u"Threshold", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.thresholdLabel.Wrap( -1 )
        self.horToolBar.AddControl( self.thresholdLabel )
        self.thresholdSlider = wx.Slider( self.horToolBar, wx.ID_ANY, 20, 0, 100, wx.DefaultPosition, wx.Size(100, -1), wx.SL_HORIZONTAL )
        self.thresholdSlider.Bind(wx.EVT_SLIDER, self.thresholdSliderChange)
        self.horToolBar.AddControl( self.thresholdSlider )
        self.thresholdTextCtrl = wx.TextCtrl( self.horToolBar, wx.ID_ANY, "20", wx.DefaultPosition, wx.Size(20,-1), 0 )
        if platform.system() == 'Linux':
            self.thresholdTextCtrl.SetSize(wx.Size(35, -1))
        self.thresholdTextCtrl.SetMaxLength( 2 )
        self.thresholdTextCtrl.Bind(wx.EVT_TEXT_ENTER, self.thresholdTextChange)
        self.horToolBar.AddControl( self.thresholdTextCtrl )
        self.horToolBar.Realize()
        mainGbSizer.Add( self.horToolBar, wx.GBPosition( 0, 1 ), wx.GBSpan( 1, 2 ), wx.EXPAND, 5 )

        self.verToolBar = wx.ToolBar( self, 2, wx.DefaultPosition, wx.DefaultSize, wx.TB_VERTICAL )
        self.verToolBar.SetToolBitmapSize(wx.Size(25, 25))
        stemAdd_bmp = wx.Bitmap(wx.Image('./icon/stem_add.png'))
        leafNew_bmp = wx.Bitmap(wx.Image('./icon/leaf_new.png'))
        leafAdd_bmp = wx.Bitmap(wx.Image('./icon/leaf_add.png'))
        leafMinus_bmp = wx.Bitmap(wx.Image('./icon/leaf_minus.png'))
        zoomIn_bmp = wx.Bitmap(wx.Image('./icon/zoom_in.png'))
        zoomOut_bmp = wx.Bitmap(wx.Image('./icon/zoom_out.png'))
        zoomBack_bmp = wx.Bitmap(wx.Image('./icon/zoom_back.png'))
        leafLassoMinus_bmp = wx.Bitmap(wx.Image('./icon/leaf_lasso_minus.png'))



        self.stemAdd = self.verToolBar.AddRadioTool(10, "stemAdd",
                                                    stemAdd_bmp, wx.NullBitmap,
                                                    "New stem", wx.EmptyString,  None)

        #self.stemAdd = self.verToolBar.AddRadioTool(10, "stemAdd",
        #                                            wx.ArtProvider.GetBitmap(wx.ART_PLUS, wx.ART_TOOLBAR),
        #                                            wx.NullBitmap, wx.EmptyString, "New stem", None)

        #self.stemMWAdd = self.verToolBar.AddRadioTool(20 , "stemMWAdd", wx.ArtProvider.GetBitmap( wx.ART_ADD_BOOKMARK, wx.ART_TOOLBAR ), wx.NullBitmap, wx.EmptyString, wx.EmptyString, None )
        #self.stemMWMinus = self.verToolBar.AddRadioTool(30 , "stemMWMinus", wx.ArtProvider.GetBitmap( wx.ART_DEL_BOOKMARK, wx.ART_TOOLBAR ), wx.NullBitmap, wx.EmptyString, wx.EmptyString, None )
        #self.verToolBar.AddSeparator()
        self.leafAdd = self.verToolBar.AddRadioTool(40 , "leafAdd",
                                                    leafNew_bmp, wx.NullBitmap,
                                                    "New Leaf", wx.EmptyString, None )
        self.leafMWAdd = self.verToolBar.AddRadioTool(50 , "leafMWAdd",
                                                      leafAdd_bmp, wx.NullBitmap,
                                                      "Leaf Area Add", wx.EmptyString, None )
        self.leafMWMinus = self.verToolBar.AddRadioTool(60 , "leafMWMinus",
                                                        leafMinus_bmp, wx.NullBitmap,
                                                        "Leaf Area Minus", wx.EmptyString, None )
        self.leafLassoMinus = self.verToolBar.AddRadioTool(61 , "leafLassoMinus",
                                                           leafLassoMinus_bmp, wx.NullBitmap,
                                                           "Leaf Area Minus Lasso", wx.EmptyString, None )
        #self.verToolBar.AddSeparator()
        self.zoomIn = self.verToolBar.AddRadioTool(70 , "zoomIn",
                                                   zoomIn_bmp, wx.NullBitmap,
                                                   "Zoom In", wx.EmptyString, None )
        self.zoomOut = self.verToolBar.AddRadioTool(80 , "zoomOut",
                                                    zoomOut_bmp, wx.NullBitmap,
                                                    "Zoom Out", wx.EmptyString, None )
        self.zoomOri = self.verToolBar.AddRadioTool(90 , "zoomBack",
                                                    zoomBack_bmp, wx.NullBitmap,
                                                    "Zoom to Origin", wx.EmptyString, None )
        #self.verToolBar.InsertSeparator(3)
        #self.verToolBar.InsertSeparator(6)
        self.verToolBar.Realize()
        self.verToolBar.Bind(wx.EVT_TOOL, self.OnTestTool)
        mainGbSizer.Add( self.verToolBar, wx.GBPosition( 1, 0 ), wx.GBSpan( 2, 1 ), wx.EXPAND, 5 )

        self.canvasPanel = CanvasPanel( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.RETAINED )
        mainGbSizer.Add( self.canvasPanel, wx.GBPosition( 1, 1 ), wx.GBSpan( 2, 1 ), wx.EXPAND |wx.ALL, 5 )
        self.rightSplitter = wx.SplitterWindow( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.SP_3D )
        self.rightSplitter.Bind( wx.EVT_IDLE, self.rightSplitterOnIdle )

        self.fileListPanle = wx.Panel( self.rightSplitter, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
        fileListSbSizer = wx.StaticBoxSizer( wx.StaticBox( self.fileListPanle, wx.ID_ANY, u"Images" ), wx.VERTICAL )

        self.fileListBox = wx.ListBox( self.fileListPanle, wx.ID_ANY, wx.DefaultPosition, wx.Size(150, -1), self.fileNameList, 0 )
        fileListSbSizer.Add( self.fileListBox, 1, wx.ALL, 5 )


        self.fileListPanle.SetSizer( fileListSbSizer )
        self.fileListPanle.Layout()
        fileListSbSizer.Fit( self.fileListPanle )
        self.sorghumTreePanel = wx.Panel( self.rightSplitter, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
        sorghumTreeSbSizer = wx.StaticBoxSizer( wx.StaticBox( self.sorghumTreePanel, wx.ID_ANY, u"Annotation" ), wx.VERTICAL )

        self.sorghumTreeCtrl = wx.TreeCtrl( sorghumTreeSbSizer.GetStaticBox(), wx.ID_ANY, wx.DefaultPosition, wx.Size(150, -1), wx.TR_DEFAULT_STYLE|wx.TR_FULL_ROW_HIGHLIGHT|wx.TR_HAS_BUTTONS )
        self.sorghumTreeRoot = self.sorghumTreeCtrl.AddRoot('Sorghum')
        self.sorghumTreeCtrl.SetItemData(self.sorghumTreeRoot, ('key', 'value'))
        leaf_1 = self.sorghumTreeCtrl.AppendItem(self.sorghumTreeRoot, 'Sorghum_1')
        self.sorghumTreeLeaf1 = self.sorghumTreeCtrl.AppendItem(leaf_1, "leaf_1")
        self.sorghumTreeCtrl.AppendItem(self.sorghumTreeLeaf1, 'Leaf_1 child')

        leaf_2 = self.sorghumTreeCtrl.AppendItem(self.sorghumTreeRoot, 'Sorghum_2')
        #self.sorghumTreeCtrl.Delete(leaf_2)

        self.sorghumTreeCtrl.Expand(self.sorghumTreeRoot)
        sorghumTreeSbSizer.Add( self.sorghumTreeCtrl, 1, wx.ALL, 5 )


        self.sorghumTreePanel.SetSizer( sorghumTreeSbSizer )
        self.sorghumTreePanel.Layout()
        sorghumTreeSbSizer.Fit( self.sorghumTreePanel )
        self.rightSplitter.SplitHorizontally( self.fileListPanle, self.sorghumTreePanel, 0 )
        mainGbSizer.Add( self.rightSplitter, wx.GBPosition( 1, 2 ), wx.GBSpan( 2, 1 ), wx.EXPAND, 5 )


        mainGbSizer.AddGrowableCol( 1 )
        mainGbSizer.AddGrowableRow( 1 )

        self.SetSizer( mainGbSizer )
        self.Layout()

        #eventManager.Register(self.OnCanvasLeftDown, wx.EVT_LEFT_DOWN, self.canvasPanel)

        self.Centre( wx.BOTH )
        self.Show()
    def __del__( self ):
        pass
    def rightSplitterOnIdle( self, event ):
        self.rightSplitter.SetSashPosition( 0 )
        self.rightSplitter.Unbind( wx.EVT_IDLE )
    def thresholdTextChange(self, evt):
        threshold = self.thresholdTextCtrl.GetValue()
        self.thresholdSlider.SetValue(int(threshold))
    def thresholdSliderChange(self, evt):
        threshold = self.thresholdSlider.GetValue()
        self.thresholdTextCtrl.SetValue(str(threshold))
    def setFileNameList(self, fileNameList):
        self.fileNameList = fileNameList
        self.fileListBox.Set(self.fileNameList)
    def OnCanvasLeftDown(self, evt):
        #self.SetStatusText(str(evt.GetPosition()))
        pass
    def OnTestTool(self, evt):
        print(str(evt.GetId()))


if __name__ == '__main__':
        app = wx.App()
        View(None)
        app.MainLoop()


