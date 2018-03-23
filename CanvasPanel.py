import wx
from wx.lib.floatcanvas import NavCanvas, FloatCanvas
import numpy
from scipy import misc

import wx

class CanvasPanel(wx.ScrolledCanvas):
    def __init__(self, *args, **kw):
        #wx.Panel.__init__(self, *args, **kw)
        wx.ScrolledCanvas.__init__(self, *args, **kw)
        self.mask = None
        self.mainImage = None
        self.focusMask = None
        self.SetScrollRate(20, 20)
        self.maxWidth  = 3000
        self.maxHeight = 3000
        self.SetVirtualSize((self.maxWidth, self.maxHeight))
        self.Bind(wx.EVT_SIZE, self.OnSize)
        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Bind(wx.EVT_LEFT_DOWN, self.OnLeftDown)
        self.Bind(wx.EVT_ERASE_BACKGROUND, self.OnEraseBackground)
        self.Bind(wx.EVT_MOTION, self.OnSize)
        #self.bmp = wx.Bitmap(28,28,32)
        #print(self.mask.IsOk())
        #self.bmp = self.MakeMask(self.mask, 32)
    def SetScale(self, xs, ys):
        super().SetScale(xs, ys)
        maxWidth = self.maxWidth  * xs
        maxHeight = self.maxHeight * ys
        self.SetVirtualSize(maxWidth, maxHeight)
    #def LoadImage(self, filename):
    #    Image = wx.Image(filename)
    #    self.Canvas.AddScaledBitmap(Image, (0,0), Height = Image.GetAlpha())
    def setImage(self, image):
        self.mainImage = image
        self.maxWidth = round(image.GetWidth()*1.2)
        self.maxHeight = round(image.GetHeight()*1.2)
    def setFocusMask(self, mask):
        self.focusMask = mask
    def setMask(self, mask):
        self.mask = mask
    def OnPaint(self, evt):
        print("OnPAint")
        dc = wx.PaintDC(self)
        dc = wx.BufferedDC(dc)
        self.PrepareDC(dc)
        #dc.SetUserScale(3.0, 3.0)
        dc.SetBackground(wx.Brush("WHITE"))
        dc.Clear()
        dc.SetBrush(wx.Brush("GREY", wx.BRUSHSTYLE_CROSSDIAG_HATCH))
        windowsize = self.GetSize()
        dc.DrawRectangle(0, 0, self.maxWidth, self.maxHeight)
        image = self.mainImage.AdjustChannels(1.0, 1.0, 1.0, 1.0)
        bitmap = wx.Bitmap(image)
        dc.DrawBitmap(bitmap, 0, 0, True)
        regionMask = wx.Mask(wx.Bitmap(self.mask),wx.Colour(0,0,0))
        image = self.mask.AdjustChannels(20.0, 255.0, 255.0, .5)
        maskBitmap = wx.Bitmap(image)
        #dc.DrawBitmap(maskBitmap, 0, 0, True)

        self.GetScaleX()
        scaledWidth = round(image.GetWidth()*self.GetScaleX())
        scaledHeight = round(image.GetHeight()*self.GetScaleY())
        image.Rescale(scaledWidth, scaledHeight)
        clipRegion = wx.Region(wx.Bitmap(image), wx.Colour(0, 0, 0))
        if clipRegion.IsEmpty():
            return
        clipRegion.Offset(dc.LogicalToDeviceX(0), dc.LogicalToDeviceY(0))
        dc.SetDeviceClippingRegion(clipRegion)
        #dc.SetClippingRegion(,0, maskBitmap.GetHeight(), maskBitmap.GetWidth())

        dc.DrawBitmap(maskBitmap,0,0, True)


        image = self.focusMask.AdjustChannels(1.0, 1.0, 1.0, 0.5)
        bitmap = wx.Bitmap(image)
        dc.DrawBitmap(bitmap, 0, 0, True)
        dc.DestroyClippingRegion()

        #test
        #dc.DrawBitmap(maskBitmap.GetMask().GetBitmap(), 0,0,True)
        #dc.DrawBitmap(wx.Bitmap(self.mainImage),-1,-1,True)
        #dc.DrawBitmap(wx.Bitmap(self.mask), 25, 25, True)
    def OnLeftDown(self, evt):
        print(evt.GetPosition())
        if evt.Dragging():
            print('DRAGGING')
        return

    def OnLeftUp(self, evt):
        return

    def OnMouseMove(self, evt):
        return

    def OnSize(self, evt):
        self.Refresh()
    def OnEraseBackground(self, evt):
        pass
    def MakeMask(self, bitmap, alpha = 32):
        pixelData = wx.AlphaPixelData(bitmap)
        pixels = pixelData.GetPixels()
        for y in range(28):
            pixels.MoveTo(pixelData, 0, y)
            for x in range(28):
                pixels.Set(255,0,0,alpha)
                pixels.nextPixel()
        return bitmap

    def CalcGlobalPosition(self, posX, posY):
        x, y = self.CalcUnscrolledPosition(posX, posY)
        x = round(x / self.GetScaleX())
        y = round(y / self.GetScaleY())
        return (x, y)


if __name__ == '__main__':
    app = wx.App(redirect=False)
    frm = wx.Frame(None, title="wx.Overlay Test", size=(450, 450))
    # frm.SetDoubleBuffered(True)
    pnl = CanvasPanel(frm)
    frm.Show()
    app.MainLoop()