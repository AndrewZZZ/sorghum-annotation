import numpy as np
import SegTool
import logging
from Segmap import Segmap
from Segmap import Sorghum
from View import View
from DataModel import DataModel
import wx
from SelectedArea import SelectedArea
from wx.lib.evtmgr import eventManager
from scipy import misc
class Controller():
    def __init__(self):
        self.dataModel = DataModel('./images', './segmaps')
        self.dataModel.getImageList()
        self.opStack=[]
        self.app = wx.App()
        self.view = View(None)
        self.view.setFileNameList(self.dataModel.imageNameList)
        self.TOOL_STEM_NEW = 10
        self.TOOL_STEM_ADD = 20
        self.TOOL_STEM_MINUS = 30
        self.TOOL_LEAF_NEW = 40
        self.TOOL_LEAF_ADD = 50
        self.TOOL_LEAF_MINUS = 60
        self.TOOL_LEAF_LASSO_MINUS = 61
        self.TOOL_ZOOM_IN = 70
        self.TOOL_ZOOM_OUT = 80
        self.TOOL_ZOOM_BACK = 90
        self.curTool = self.TOOL_STEM_NEW
        self.curImageIdx = 0
        self.curImageName = self.dataModel.imageNameList[self.curImageIdx]
        self.curImage = self.dataModel.getImageByIdx(self.curImageIdx)
        self.curSegmap = Segmap(self.dataModel.getSegmapByIdx(self.curImageIdx), self.dataModel.loadDependcy(self.curImageName))
        self.curThreshold = self.view.thresholdSlider.GetValue()
        self.curSorghumId = None
        self.curLeafId = None
        self.curSelectedId = -1
        self.curSelectedType = 'sorghum'
        self.curZoom = 1.0
        self.leafSA = SelectedArea(np.zeros((self.curSegmap.height, self.curSegmap.width)), type=SelectedArea.TYPE_LEAF)
        self.stemSA = SelectedArea(np.zeros((self.curSegmap.height, self.curSegmap.width)), type=SelectedArea.TYPE_STEM)
        eventManager.Register(self.OnCanvasLeftDown, wx.EVT_LEFT_DOWN, self.view.canvasPanel)
        eventManager.Register(self.OnCanvasMotion, wx.EVT_MOTION, self.view.canvasPanel)
        eventManager.Register(self.OnCanvasLeftUp, wx.EVT_LEFT_UP, self.view.canvasPanel)
        eventManager.Register(self.OnToolChange, wx.EVT_TOOL, self.view.verToolBar)
        eventManager.Register(self.OnThresholdSliderChange, wx.EVT_SLIDER, self.view.thresholdSlider)
        eventManager.Register(self.OnThresholdTextChange, wx.EVT_TEXT_ENTER, self.view.thresholdTextCtrl)
        eventManager.Register(self.OnFileChange, wx.EVT_LISTBOX, self.view.fileListBox)
        eventManager.Register(self.OnTreeKeyDown, wx.EVT_KEY_DOWN, self.view.sorghumTreeCtrl)
        eventManager.Register(self.OnTreeRightDown, wx.EVT_TREE_SEL_CHANGED, self.view.sorghumTreeCtrl)
        self.logger = logging.getLogger('Controller')
        self.logger.setLevel(logging.DEBUG)
        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)
        self.logger.addHandler(ch)
        self.logger.info('init')
        self.init()
    def init(self):
        self.view.sorghumTreeCtrl.DeleteChildren(self.view.sorghumTreeRoot)
        self.refreshTree()
        init_image = self.dataModel.npyToBitmap(self.curImage)
        init_mask = self.dataModel.npyToBitmap(self.curSegmap.segmapImage)
        init_focusMask = self.dataModel.npyToBitmap(self.curSegmap.getSorghumMaskById(-1))
        self.view.canvasPanel.setImage(init_image)
        self.view.canvasPanel.setMask(init_mask)
        self.view.canvasPanel.setFocusMask(init_focusMask)
        self.app.MainLoop()
    def changeTool(self, tool):
        self.curTool = tool
        self.opStack = []

    def OnCanvasLeftDown(self, evt):
        self.logger.debug('On canvas LeftDown, tool_id: %d', self.curTool)
        #pos = evt.GetPosition()
        self.logger.debug("Origin Click Pos: (%s, %s)", evt.GetX(), evt.GetY())
        scale = self.view.canvasPanel.GetScaleX()
        self.logger.debug("Scale get from canvasPanle: %s", scale)
        pos = self.view.canvasPanel.CalcGlobalPosition(evt.GetX(), evt.GetY())
        self.logger.debug("Scale factor: %s; Transformed Pos: %s", self.curZoom, pos)

        self.logger.debug('Current Point Sorghum ID: %d, Stem ID: %s, Leaf ID: %s',
                          self.curSegmap.getIdOnPos(pos[1], pos[0], type='sorghum'),
                          self.curSegmap.getIdOnPos(pos[1], pos[0], type='stem'),
                          self.curSegmap.getIdOnPos(pos[1], pos[0], type='leaf'),
                          )
        self.view.SetStatusText(str(pos))
        if self.curTool == self.TOOL_STEM_NEW:
            self.logger.debug('opStack length: %d', len(self.opStack))
            if len(self.opStack) >= 3:
                self.view.SetStatusText('New Stem Added')
                self.opStack.append(pos)
                self.logger.debug('Points for new stem: (%d,%d),(%d,%d),(%d,%d),(%d,%d)',
                           self.opStack[0][0], self.opStack[0][1],
                           self.opStack[1][0], self.opStack[1][1],
                           self.opStack[2][0], self.opStack[2][1],
                           self.opStack[3][0], self.opStack[3][1])
                self.stemSA.newArea(self.curSegmap.sorghumMap,
                           self.opStack[0][0], self.opStack[0][1],
                           self.opStack[1][0], self.opStack[1][1],
                           self.opStack[2][0], self.opStack[2][1],
                           self.opStack[3][0], self.opStack[3][1],
                           mwMode=SelectedArea.MW_MODE_FOUR_POINT
                           )
                self.curSegmap.newSorghum(self.stemSA)
                self.logger.debug('sA shape: %s', self.stemSA.areaMask.shape)
                self.dataModel.saveSegmap(self.curSegmap, self.curImageName)
                self.view.canvasPanel.setMask(self.dataModel.npyToBitmap(self.curSegmap.segmapImage))
                #self.view.canvasPanel.setMask(self.dataModel.npyToBitmap(misc.imread('./segmaps/test_image_bak.png')))
                self.logger.debug('Tool New Stem Done')
                self.logger.debug('Segmap nonzero: %d ', np.count_nonzero(self.curSegmap.segmapImage))
                self.curSorghumId = self.stemSA.id
                self.logger.debug('Id update after new Sorghum: %d', self.stemSA.id)
                self.view.sorghumTreeCtrl.AppendItem(self.view.sorghumTreeRoot, 'Sorghum_%d' % (self.stemSA.id), data=['sorghum', self.stemSA.id])
                treeNewSorghum = self.view.sorghumTreeCtrl.GetLastChild(self.view.sorghumTreeRoot)
                self.view.sorghumTreeCtrl.SelectItem(treeNewSorghum)
                #self.view.canvasPanel.Refresh()
                self.refreshCanvas()
                self.opStack.clear()
                self.stemSA.clear()
                #self.refreshTree()

            else:
                self.view.SetStatusText("Please click point #%s " % (len(self.opStack) + 2))
                self.opStack.append(pos)
        elif self.curTool ==self.TOOL_STEM_ADD:
            pass
        elif self.curTool == self.TOOL_STEM_MINUS:
            pass
        elif self.curTool == self.TOOL_LEAF_NEW:
            self.logger.debug('Tool \'New Leaf\', Pos: (%d, %d)', pos[0], pos[1])
            self.leafSA.newArea(self.curSegmap.sorghumMap, pos[1], pos[0], threshold= self.curThreshold, image=self.curImage)
            leafId = self.curSegmap.newLeaf(self.curSorghumId, self.leafSA)
            self.curLeafId =leafId
            self.dataModel.saveSegmap(self.curSegmap, self.curImageName)
            self.view.canvasPanel.setMask(self.dataModel.npyToBitmap(self.curSegmap.segmapImage))
            #self.view.canvasPanel.Refresh()
            self.refreshCanvas()
            self.leafSA.clear()
            treeItem = self.view.sorghumTreeCtrl.GetFocusedItem()
            treeItemData = self.view.sorghumTreeCtrl.GetItemData(treeItem)
            if treeItemData[0] == 'sorghum':
                addRoot = treeItem
            else:
                addRoot = self.view.sorghumTreeCtrl.GetItemParent(treeItem)
            parentSorghumId = self.curSegmap.getLeafParent(leafId)
            newLeafNode = self.view.sorghumTreeCtrl.AppendItem(addRoot, 'Leaf_%d' % (leafId), data=['leaf', parentSorghumId, leafId])
            self.view.sorghumTreeCtrl.SelectItem(newLeafNode)
            #self.refreshTree()
            # change segmap
            # save segmap
            # update canvas
            # TODO dont save segmap into file, only if user choose to do so. Need a attr in DataModel: modified_Segmap
        elif self.curTool == self.TOOL_LEAF_ADD:
            self.logger.debug('Tool \'Leaf Minus\', Pos: (%d, %d)', pos[0], pos[1])
            self.logger.debug('current leaf id: %s', self.curLeafId)
            self.leafSA.modifyArea(self.curLeafId, self.curSegmap.sorghumMap, self.curImage, pos[1], pos[0], self.curThreshold, opMode=SelectedArea.MODIFY_MODE_ADD)
            self.curSegmap.modifyLeaf(self.curLeafId, self.leafSA, mode='add')
            self.dataModel.saveSegmap(self.curSegmap, self.curImageName)
            self.view.canvasPanel.setMask(self.dataModel.npyToBitmap(self.curSegmap.segmapImage))
            #self.view.canvasPanel.Refresh()
            self.refreshCanvas()
            self.leafSA.clear()
            pass
        elif self.curTool == self.TOOL_LEAF_MINUS:
            self.logger.debug('Tool \'Leaf Minus\', Pos: (%d, %d)', pos[0], pos[1])
            self.logger.debug('current leaf id: %s', self.curLeafId)
            self.leafSA.modifyArea(self.curLeafId, self.curSegmap.sorghumMap, self.curImage, pos[1], pos[0], self.curThreshold, opMode=SelectedArea.MODIFY_MODE_ADD)
            self.curSegmap.modifyLeaf(self.curLeafId, self.leafSA, mode='minus')
            self.dataModel.saveSegmap(self.curSegmap, self.curImageName)
            self.view.canvasPanel.setMask(self.dataModel.npyToBitmap(self.curSegmap.segmapImage))
            #self.view.canvasPanel.Refresh()
            self.refreshCanvas()
            self.leafSA.clear()
            pass
        elif self.curTool == self.TOOL_LEAF_LASSO_MINUS:
            self.opStack.append(list(pos))
            pass
        elif self.curTool == self.TOOL_ZOOM_IN:
            perPos = self.view.canvasPanel.CalcUnscrolledPosition(evt.GetX(), evt.GetY())
            self.curZoom += 0.1
            self.view.canvasPanel.SetScale(self.curZoom, self.curZoom)
            unscaleX, unscaleY = self.view.canvasPanel.CalcUnscrolledPosition(evt.GetX(), evt.GetY())
            newPos = self.view.canvasPanel.CalcUnscrolledPosition(evt.GetX(), evt.GetY())
            curX, curY = self.view.canvasPanel.GetViewStart()
            scrollRate = self.view.canvasPanel.GetScrollPixelsPerUnit()
            self.logger.debug("before scroll pos: %s, %s", curX, curY)
            scrollX = round( curX + (newPos[0] * 0.1) / scrollRate[0] )
            scrollY = round( curY + (newPos[1] * 0.1) / scrollRate[1] )
            self.logger.debug("scrolled pos: %s, %s", scrollX, scrollY)
            self.view.canvasPanel.Scroll(scrollX, scrollY)
            #self.view.canvasPanel.Refresh()
            self.refreshCanvas()
            pass
        elif self.curTool == self.TOOL_ZOOM_OUT:
            perPos = self.view.canvasPanel.CalcUnscrolledPosition(evt.GetX(), evt.GetY())
            self.curZoom -= 0.1
            self.view.canvasPanel.SetScale(self.curZoom, self.curZoom)
            unscaleX, unscaleY = self.view.canvasPanel.CalcUnscrolledPosition(evt.GetX(), evt.GetY())
            newPos = self.view.canvasPanel.CalcUnscrolledPosition(evt.GetX(), evt.GetY())
            curX, curY = self.view.canvasPanel.GetViewStart()
            scrollRate = self.view.canvasPanel.GetScrollPixelsPerUnit()
            self.logger.debug("before scroll pos: %s, %s", curX, curY)
            scrollX = round( curX - (newPos[0] * 0.1) / scrollRate[0] )
            scrollY = round( curY - (newPos[1] * 0.1) / scrollRate[1] )
            self.logger.debug("scrolled pos: %s, %s", scrollX, scrollY)
            self.view.canvasPanel.Scroll(scrollX, scrollY)
            #self.view.canvasPanel.Refresh()
            self.refreshCanvas()
            pass
        elif self.curTool == self.TOOL_ZOOM_BACK:
            self.curZoom = 1.0
            self.view.canvasPanel.SetScale(self.curZoom, self.curZoom)
            #self.view.canvasPanel.Refresh()
            self.refreshCanvas()

    def OnCanvasMotion(self, evt):
        pos = self.view.canvasPanel.CalcGlobalPosition(evt.GetX(), evt.GetY())
        if evt.Dragging():
            if self.curTool == self.TOOL_LEAF_MINUS:
                self.logger.debug('Tool \'Leaf Minus\', Pos: (%d, %d)', pos[0], pos[1])
                self.logger.debug('current leaf id: %s', self.curLeafId)
                sA = SelectedArea(np.zeros((self.curSegmap.height, self.curSegmap.width)), type=SelectedArea.TYPE_LEAF)
                sA.modifyArea(self.curLeafId, self.curSegmap.sorghumMap, self.curImage, pos[1], pos[0],
                              self.curThreshold, opMode=SelectedArea.MODIFY_MODE_ADD)
                self.curSegmap.modifyLeaf(self.curLeafId, sA, mode='minus')
                self.dataModel.saveSegmap(self.curSegmap, self.curImageName)
                self.view.canvasPanel.setMask(self.dataModel.npyToBitmap(self.curSegmap.segmapImage))
                #self.view.canvasPanel.Refresh()
                self.refreshCanvas()
            elif self.curTool == self.TOOL_LEAF_LASSO_MINUS:
                self.opStack.append(list(pos))
                pass
    def OnCanvasLeftUp(self, evt):
        pos = self.view.canvasPanel.CalcGlobalPosition(evt.GetX(), evt.GetY())
        if self.curTool == self.TOOL_LEAF_LASSO_MINUS:
            #self.logger.debug('Lasso minus point list: %s', self.opStack)
            self.logger.debug('Lasso minus')
            self.logger.debug('current leaf id: %s', self.curLeafId)
            #sA = SelectedArea(np.zeros((self.curSegmap.height, self.curSegmap.width)), type=SelectedArea.TYPE_LEAF)
            #sA.lassoArea(self.curLeafId, self.curSegmap.sorghumMap, self.opStack)
            self.leafSA.lassoArea(self.curLeafId, self.curSegmap.sorghumMap, self.opStack)
            self.curSegmap.modifyLeaf(self.curLeafId, self.leafSA, mode='minus')
            self.leafSA.clear()
            self.dataModel.saveSegmap(self.curSegmap, self.curImageName)
            self.view.canvasPanel.setMask(self.dataModel.npyToBitmap(self.curSegmap.segmapImage))
            #self.view.canvasPanel.Refresh()
            self.refreshCanvas()
            self.opStack.clear()
            pass


    def refreshCanvas(self):
        image = self.dataModel.npyToBitmap(self.curImage)
        mask = self.dataModel.npyToBitmap(self.curSegmap.segmapImage)
        self.view.canvasPanel.setImage(image)
        self.view.canvasPanel.setMask(mask)
        self.logger.debug("Refresh Canvas")
        if self.curSelectedType == 'sorghum':
            focusMask = self.dataModel.npyToBitmap(self.curSegmap.getSorghumMaskById(self.curSelectedId))
            self.view.canvasPanel.setFocusMask(focusMask)
        elif self.curSelectedType == 'leaf':
            focusMask = self.dataModel.npyToBitmap(self.curSegmap.getLeafMaskById(self.curSelectedId))
            self.view.canvasPanel.setFocusMask(focusMask)
        self.view.canvasPanel.Refresh()
    def refreshTree(self):
        self.view.sorghumTreeCtrl.DeleteChildren(self.view.sorghumTreeRoot)
        for sorghum in self.curSegmap.sorghumList:
            parentSorghum = self.view.sorghumTreeCtrl.AppendItem(self.view.sorghumTreeRoot, 'Sorghum_%d' % (sorghum.sorghumId), data=['sorghum', sorghum.sorghumId])
            for leafId in sorghum.leafIdList:
                self.view.sorghumTreeCtrl.AppendItem(parentSorghum, 'Leaf_%d' % (leafId), data=['leaf', sorghum.sorghumId, leafId])


    def addSorghumTree(self, id, type):
        if type == 'sorghum':
            pass
        elif type == 'leaf':
            pass
        else:
            self.logger.error('SorghumTree item add error, no type: \'%s\'', type)
    def removeSorghumTree(self, id, type):
        if type == 'sorghum':
            pass
        elif type == 'leaf':
            pass
        else:
            self.logger.error('SorghumTree item remove error, no type: \'%s\'', type)
    def OnToolChange(self, evt):
        self.curTool = evt.GetId()
        self.logger.debug('Tool changed. Tool Code: %d', self.curTool)
        self.opStack.clear()
        if self.curTool == self.TOOL_STEM_NEW:
            self.view.SetStatusText("Please click point #1 ")

    def OnThresholdSliderChange(self, evt):
        self.curThreshold = int(self.view.thresholdSlider.GetValue()/5)
        self.view.thresholdTextCtrl.SetValue(str(self.view.thresholdSlider.GetValue()))
        #self.logger.debug('Threshold changed. Threshold: %d', self.curThreshold)

    def OnThresholdTextChange(self, evt):
        self.curThreshold = int(self.view.thresholdTextCtrl.GetValue()/5)
        self.view.thresholdSlider.SetValue(int(self.view.thresholdTextCtrl.GetValue()))
        #self.logger.debug('Threshold changed. Threshold: %d', self.curThreshold)

    def OnFileChange(self, evt):
        self.curImageIdx= evt.GetSelection()
        self.logger.debug('File changed to: %d', self.curImageIdx)
        self.curImageName = self.dataModel.imageNameList[self.curImageIdx]
        self.curImage = self.dataModel.getImageByIdx(self.curImageIdx)
        self.curSegmap = Segmap(self.dataModel.getSegmapByIdx(self.curImageIdx),  self.dataModel.loadDependcy(self.curImageName))
        self.refreshTree()
        if self.view.sorghumTreeCtrl.ItemHasChildren(self.view.sorghumTreeCtrl.GetRootItem()):
            self.view.sorghumTreeCtrl.SelectItem(self.view.sorghumTreeCtrl.GetFirstChild(self.view.sorghumTreeCtrl.GetRootItem())[0])
        else:
            self.view.sorghumTreeCtrl.SelectItem(self.view.sorghumTreeCtrl.GetRootItem())
        self.refreshCanvas()

    def OnTreeRightDown(self, evt):
        self.logger.debug("Item changed")
        item = evt.GetItem()
        itemData = self.view.sorghumTreeCtrl.GetItemData(item)
        if itemData[0] == 'key':
            self.logger.debug('changing item to: root')
            self.curSorghumId = None
            return
        if itemData[0] == 'sorghum':
            self.logger.debug('Changing item to: (sorghumId: %s)', itemData[1])
            self.curSorghumId = itemData[1]
            if self.view.sorghumTreeCtrl.ItemHasChildren(item):
                firstChild = self.view.sorghumTreeCtrl.GetFirstChild(item)[0]
                self.logger.debug("First Child: %s", firstChild)
                firstLeafId = self.view.sorghumTreeCtrl.GetItemData(firstChild)[2]
            else :
                self.curLeafId = None
            self.curSelectedType = 'sorghum'
            self.curSelectedId = itemData[1]
        if itemData[0] == 'leaf':
            self.logger.debug('Changing item to: (sorghumId: %s, leafId: %s)', itemData[1], itemData[2])
            self.curSorghumId = itemData[1]
            self.curLeafId = itemData[2]
            self.curSelectedType = 'leaf'
            self.curSelectedId = itemData[2]
        self.refreshCanvas()
        self.logger.debug('Change item to: (sorghumId: %s, leafId: %s)', self.curSorghumId, self.curLeafId)
        self.logger.debug('sorghum: %s, sorghumId: %s, sorghum children: %s', self.curSegmap.getSorghumById(self.curSorghumId), self.curSegmap.getSorghumById(self.curSorghumId).sorghumId, self.curSegmap.getSorghumById(self.curSorghumId).leafIdList)
        self.logger.debug('leafIdListId: %s', id(self.curSegmap.getSorghumById(self.curSorghumId)))


    def OnTreeKeyDown(self, evt):
        DEL = 127
        keyCode = evt.GetKeyCode()
        self.logger.debug('%s', keyCode)
        if keyCode == 127:
            delItem = self.view.sorghumTreeCtrl.GetFocusedItem()
            if delItem == self.view.sorghumTreeRoot:
                self.logger.info("Cannot delete Tree Root!")
                return
            itemData = self.view.sorghumTreeCtrl.GetItemData(delItem)
            self.logger.debug('Delete type: %s', itemData[0])
            if itemData[0] == 'sorghum':
                self.curSegmap.deleteSorghum(itemData[1])
            elif itemData[0] == 'leaf':
                self.curSegmap.deleteLeaf(itemData[2])
            self.refreshCanvas()
            self.dataModel.saveSegmap(self.curSegmap, self.curImageName)
            self.view.sorghumTreeCtrl.Delete(delItem)

