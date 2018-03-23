import numpy as np
from lxml import etree
from operator import attrgetter
import SegTool
import logging
class Segmap():
    def __init__(self, segmapImage, sorghumList = [], leafList = []):
        self.logger = logging.getLogger('Segmap')
        self.logger.setLevel(logging.DEBUG)
        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)
        self.logger.addHandler(ch)

        if len(segmapImage.shape) == 2:
            self.segmapImage = np.dstack([segmapImage, segmapImage, segmapImage])
            self.height, self.width = segmapImage.shape
        elif len(segmapImage.shape) == 3:
            self.segmapImage = np.array(segmapImage)
            self.height, self.width, _ = segmapImage.shape
        else:
            self.logger.error('Wrong length of shape')

        self.sorghumMap = self.segmapImage[:,:,0]
        self.stemMap = self.segmapImage[:,:,2]
        self.leafMap = self.segmapImage[:,:,1]
#        self.alphaCh = segmapImage[:,:,3]
        self.sorghumList = sorghumList
        self.leafIdList = leafList
        self.sorghumTreeRoot = etree.Element('sorghum_root')
        self.solveDependcy()

    def solveDependcy(self):
        self.logger.debug("solving dependcy..")
        leafIdList = []
        for sorghum in self.sorghumList:
            leafIdList = np.concatenate((leafIdList, sorghum.leafIdList)).astype('int')
            self.logger.debug('adding leaflist: %s', sorghum.leafIdList)
        self.leafIdList = list(leafIdList)
        pass

    # TODO When change the segmap, check if the point value is zero or not
    # if it's not zero dont change the value in ALL map
    def newSorghum(self, selectedArea, id = 0):
        if id != 0:
            selectedArea.setId(id)
        else:
            if len(self.sorghumList) == 0:
                selectedArea.setId(1)
            else:
                selectedArea.setId(max(self.sorghumList, key=attrgetter('sorghumId')).sorghumId + 1)
        self.logger.debug('sA.id = %d', selectedArea.id)
        sorghumValidMap = ~self.sorghumMap.astype('bool')
        selectedArea.areaMask = selectedArea.areaMask * sorghumValidMap
        self.sorghumMap = self.sorghumMap + selectedArea.areaMask
        self.stemMap = self.stemMap + selectedArea.areaMask
        self.sorghumList.append(Sorghum(selectedArea.id))
        self.updateSegmapImage()
        self.logger.debug('sorghumIdList Len: %d', len(self.sorghumList))

    # Alias of newSorghum
    newStem = newSorghum

    def deleteSorghum(self, sorghumId):
        delMap = ~(self.sorghumMap == sorghumId)
        self.sorghumMap = self.sorghumMap * delMap
        self.stemMap = self.stemMap * delMap
        self.leafMap = self.leafMap * delMap
        self.updateSegmapImage()
        delSorghum = next(sorghum for sorghum in self.sorghumList if sorghum.sorghumId == sorghumId)
        for leafId in delSorghum.leafIdList:
            self.leafIdList.remove(leafId)
        self.sorghumList.remove(delSorghum)
        #for sorghum in self.sorghumList:
        #    if sorghum.sorghumId == sorghumId:
        #        self.sorghumList.remove(sorghum)


    def newLeaf(self, parentSorghumId, selectedArea, id=0):
        if parentSorghumId > len(self.sorghumList):
            self.logger.error('ParentSorghumId exceed. ParentId: %d SorghumList len: %d', parentSorghumId, len(self.sorghumList))
        if id != 0:
            selectedArea.setId(id)
        else :
            if len(self.leafIdList) == 0:
                id = 1
            else:
                id = max(self.leafIdList) + 1
            '''
            # get leaf id
            parentSorghum = [x for x in self.sorghumList if x.sorghumId == parentSorghumId]
            if len(parentSorghum) == 0:
                self.logger.error('NO Sorghum ID: %d', parentSorghumId)
                pass
            if len(parentSorghum) > 1:
                self.logger.error('Multiple(%d) Sorghum with ID: %d', len(parentSorghum), parentSorghumId)
                for sorghum in parentSorghum:
                    self.logger.debug("%d", sorghum.sorghumId)
                #pass
            if len(parentSorghum[0].leafIdList) == 0:
                selectedArea.setId(1)
            else:
                # THIS IS NOT GLOBAL MAX LEAFID!!!!!
                selectedArea.setId(max(parentSorghum[0].leafIdList) + 1)
            '''
        selectedArea.setId(id)
        self.logger.debug('Adding new leaf with leafId=%s', selectedArea.id)
        # validMap is the map of zeros of the sorghumMap
        validMap = ~self.sorghumMap.astype('bool')
        selectedArea.areaMask = selectedArea.areaMask * validMap
        self.leafMap = self.leafMap + selectedArea.areaMask
        # Update  sorghumMap
        leafId = selectedArea.id
        selectedArea.setId(parentSorghumId)
        self.sorghumMap = self.sorghumMap + selectedArea.areaMask
        selectedArea.setId(leafId)
        # update segmapImage
        self.updateSegmapImage()
        self.logger.debug('Segmap.newLeaf: parentSorghumId: %s', parentSorghumId)
        next(sorghum for sorghum in self.sorghumList if sorghum.sorghumId == parentSorghumId).addLeaf(leafId)
        #self.sorghumList[parentSorghumId - 1].leafIdList.append(id)
        self.leafIdList.append(leafId)
        return leafId

    def deleteLeaf(self, leafId):
        delMap = ~(self.leafMap == leafId)
        self.leafMap = self.leafMap * delMap
        self.sorghumMap = self.sorghumMap * delMap
        self.updateSegmapImage()
        for sorghum in self.sorghumList:
            if leafId in sorghum.leafIdList:
                sorghum.leafIdList.remove(leafId)
        self.leafIdList.remove(leafId)
    def getLeafMaskById(self, leafId):
        mask = (self.leafMap == leafId) * 255
        return mask.astype('uint8')
    def getSorghumMaskById(self, sorghumId):
        mask = (self.sorghumMap == sorghumId) * 255
        return mask.astype('uint8')
    def modifySorghum(self, id, modifiedArea):
        pass

    def modifyLeaf(self, id, modifiyArea, mode):
        parentId = self.getLeafParent(id)
        if parentId == None:
            self.logger.error('Leaf with id=%d has no parent. Exit modifyLeaf.')
            return None
        if mode == 'add':
            # intersection between zero-map and modifyArea to get the region need to change
            self.logger.debug('Modifying Leaf Area leafId=%s, mode = %s', id, mode)
            validMap = ~self.sorghumMap.astype('bool')
            modifiyArea.setId(id)
            modifiyArea.areaMask = modifiyArea.areaMask * validMap
            self.leafMap = self.leafMap + modifiyArea.areaMask
            # Update sorghumMap
            modifiyArea.setId(parentId)
            self.sorghumMap = self.sorghumMap + modifiyArea.areaMask
            modifiyArea.setId(id)
            # update SegmapImage
            self.updateSegmapImage()
            self.logger.debug('DONE modifying Leaf Area leafId=%s, mode = %s', id, mode)
        elif mode == 'minus':
            # intersection between id-map and modify Area to get the region need to change
            # TODO: 1. change validMap
            #       2. change set value (by * boolmap)
            self.logger.debug('Modifying Leaf Area leafId=%s, mode = %s', id, mode)
            validMap = self.leafMap == id
            self.logger.debug('minus validMap non-zero count: %s', np.count_nonzero(validMap))
            modifiyArea.setId(id)
            self.logger.debug('minus modifyA non-zero count: %s', np.count_nonzero(modifiyArea.areaMask))
            modifiyArea.areaMask = modifiyArea.areaMask * validMap
            self.leafMap = self.leafMap - modifiyArea.areaMask
            # Update sorghumMap
            modifiyArea.setId(parentId)
            self.sorghumMap = self.sorghumMap - modifiyArea.areaMask
            modifiyArea.setId(id)
            # update SegmapImage
            self.updateSegmapImage()
            self.logger.debug('DONE modifying Leaf Area leafId=%s, mode = %s', id, mode)
        else:
            self.logger.error('Wrong leaf modify mode: %s', mode)

    def updateSegmapImage(self):
        self.logger.debug('type before dstack: %s', self.segmapImage.dtype)
        self.segmapImage = np.dstack((self.sorghumMap, self.leafMap, self.stemMap)).astype('uint8')
        self.logger.debug('type after dstack: %s', self.segmapImage.dtype)

    def getIdOnPos(self, x, y, type='sorghum'):
        if x > self.height or y > self.width:
            self.logger.debug("Segmap.getIdOnPos input exceed.")
            return None
        if type == 'sorghum':
            return self.sorghumMap[x,y]
        elif type == 'stem':
            return self.stemMap[x,y]
        elif type == 'leaf':
            return self.leafMap[x,y]
        else:
            self.logger.error('Segmap.getIdOnPos wrong type.')
    def getLeafParent(self, leafId):
        parentSorghum = [ x for x in self.sorghumList if leafId in x.leafIdList ]
        if len(parentSorghum) == 0:
            self.logger.error('Leaf with id=%d has no parent.', leafId)
            return None
        elif len(parentSorghum) != 1:
            self.logger.warning('Leaf with id=%s has more than one parent (%d parents): %s. Using the first parent.', leafId, len(parentSorghum), parentSorghum )
        parentId = parentSorghum[0].sorghumId
        return parentId
    def getSorghumById(self, sorghumId):
        sorghum = [sorghum for sorghum in self.sorghumList if sorghum.sorghumId == sorghumId]
        return sorghum[0]
    def getLeafMapById(self, leafId):
        pass
    def getSorghumMapById(self, sorghumId):
        pass
    def getStemMapById(self, sorghumId):
        pass



class Sorghum():
    def __init__(self, sorghumId,  leafIdList = [], sorghumMap = None, stemMap = None, leafMap = None):
        self.sorghumId = sorghumId
        self.stemId = sorghumId
        self.leafIdList = list(leafIdList)
        self.sorghumMap = sorghumMap
        self.stemMap = stemMap
        self.leafMap = leafMap
    def addLeaf(self, leafId):
        print('adding leaf w/ id %s for %s' % (leafId, self.sorghumId))
        self.leafIdList.append(leafId)

    def delLeaf(self, leafId):
        print('delete leaf w/ id %s for %s' % (leafId, self.sorghumId))
        self.leafIdList.remove(leafId)

