#!/usr/bin/env python

# mygui.py -
# Copyright (C) 2007-2008  Bastian Venthur
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

import sys
import logging

from PyQt4 import QtCore, QtGui
from gui.gui import Ui_MainWindow
import bcinetwork
import bcixml

class BciGui(QtGui.QMainWindow, Ui_MainWindow):
    
    def __init__(self):
        QtGui.QMainWindow.__init__(self)
        self.setupUi(self)
        
#        self.model = TableModel(self.tableView)
#        self.tableView.setModel(self.model)

        self.model = TableModel(self)
        self.proxymodel = QtGui.QSortFilterProxyModel(self)
        self.proxymodel.setSourceModel(self.model)
        self.proxymodel.setFilterKeyColumn(-1)
        self.tableView.setModel(self.proxymodel)
        self.tableView.verticalHeader().setVisible(False)
        self.tableView.horizontalHeader().setResizeMode(1, QtGui.QHeaderView.Stretch)

        
        # connect toolbuttons to actions
        self.toolButton_addFeedbackController.setDefaultAction(self.actionAddFeedbackController)
        self.toolButton_clearFilter.setDefaultAction(self.actionClearFilter)
        self.toolButton_pause.setDefaultAction(self.actionPause)
        self.toolButton_play.setDefaultAction(self.actionPlay)
        self.toolButton_quit.setDefaultAction(self.actionQuit1)
        self.toolButton_send.setDefaultAction(self.actionSend)
        self.toolButton_sendinit.setDefaultAction(self.actionSendInit)
        self.toolButton_get.setDefaultAction(self.actionGet)
        
        # connect actions to methods
        #QtCore.QObject.connect(self.actionOpen, QtCore.SIGNAL("triggered()"), self.clicked)
        QtCore.QObject.connect(self.actionAddFeedbackController, QtCore.SIGNAL("triggered()"), self.addFeedbackController)
        QtCore.QObject.connect(self.actionClearFilter, QtCore.SIGNAL("triggered()"), self.clearFilter)
        QtCore.QObject.connect(self.actionOpen, QtCore.SIGNAL("triggered()"), self.open)
        QtCore.QObject.connect(self.actionPause, QtCore.SIGNAL("triggered()"), self.pause)
        QtCore.QObject.connect(self.actionPlay, QtCore.SIGNAL("triggered()"), self.play)
        QtCore.QObject.connect(self.actionQuit, QtCore.SIGNAL("triggered()"), self.quit)
        QtCore.QObject.connect(self.actionQuit1, QtCore.SIGNAL("triggered()"), self.quitFeedbackController)
        QtCore.QObject.connect(self.actionSave, QtCore.SIGNAL("triggered()"), self.save)
        QtCore.QObject.connect(self.actionSaveAs, QtCore.SIGNAL("triggered()"), self.saveas)
        QtCore.QObject.connect(self.actionSend, QtCore.SIGNAL("triggered()"), self.send)
        QtCore.QObject.connect(self.actionSendInit, QtCore.SIGNAL("triggered()"), self.sendinit)
        QtCore.QObject.connect(self.actionGet, QtCore.SIGNAL("triggered()"), self.get)
        
        QtCore.QObject.connect(self.lineEdit, QtCore.SIGNAL("textEdited(const QString&)"), self.filter)
        QtCore.QObject.connect(self.comboBox_player, QtCore.SIGNAL("currentIndexChanged(int)"), self.playerChanged)
        
        self.feedbacks = []
        self.bcinetworks = []
        self.players = 0
        self.bcinetwork2player = {} # assigns a playerhame (1,2,...) to each bcinetwork
        

    def play(self):
        for i in self.__who():
            i.play()
    
    def pause(self):
        for i in self.__who():
            i.pause()
    
    def get(self):
        for i in self.__who():
            d = i.get_variables()
            entries = []
            for name, value in d.iteritems():
                e = Entry(name, value, False, self.bcinetwork2player[i])
                entries.append(e)
            # FIXME: this will clear the whole table and just put in the new
            # entries (ignoring the entries of the other players.
            self.model.setElements(entries)
    
    def sendinit(self):
        feedback = unicode(self.comboBox_feedback.currentText())
        for i in self.__who():
            i.send_init(feedback)
            d = i.get_variables()
            entries = []
            for name, value in d.iteritems():
                e = Entry(name, value, False, self.bcinetwork2player[i])
                entries.append(e)
            self.model.setElements(entries)
            
    
    def send(self):
        for i in self.__who():
            signal = self.makeSignal(self.bcinetwork2player[i])
            i.send_signal(signal)
            
    
    def makeSignal(self, who):
        """Create an Interaction Signal from the Variables in the Table."""
        data = {}
        for elem in self.model.entry:
            if elem.player == who:
                data[elem.name] = elem.value
        signal = bcixml.BciSignal(data, None, bcixml.INTERACTION_SIGNAL)
        return signal

    
    def quitFeedbackController(self):
        for i in self.__who():
            i.quit()

        
    def __who(self):
        """
        Returns a list of bcinetworks which are currently selected via
        the comboBox_player.
        """
        # 1 means invalid selection
        # 0 means all players
        # x means player x-1
        i = self.comboBox_player.currentIndex()
        if i < 0:
            return None
        elif i == 0:
            return self.bcinetworks
        else:
            return self.bcinetworks[i-1]
    
    
    def open(self):
        pass
    
    def save(self):
        pass
    
    def saveas(self):
        pass
    
    def quit(self):
        pass
    
    
    def addFeedbackController(self):
        text, ok = QtGui.QInputDialog.getText(self, "Add Feedback Controller", "Please enter the address[:port] of the Feedback Controller.\n\nThe adress can be a hostname or numeric, the port is optional.")
        if not ok:
            return
        
        ip, port = bcinetwork.LOCALHOST, bcinetwork.FC_PORT
        ipport = text.split(":")
        if len(ipport) >= 1:
            ip = ipport[0]
        if len(ipport) >= 2:
            port = ipport[1]
            
        # ask feedback controller under given ip for available feedbacks
        bcinet = bcinetwork.BciNetwork(ip, port, bcinetwork.GUI_PORT)
        feedbacks = bcinet.getAvailableFeedbacks()
        
        if not feedbacks:
            QtGui.QMessageBox.warning(self, 
                "Ooops!", 
                "The Feedback Controller under the given adress: %s did not respond or has no feedbacks available!\n\nIt was not added to the list of available Feedback Controllers." % str(ip)+":"+str(port))
            return
        else:
            self.players += 1
#            feedbacks.append(str(self.players))
            feedbacks.sort()
            self.feedbacks.append(feedbacks)
            self.comboBox_player.clear()
            self.comboBox_player.addItem("All Players")
            for i in xrange(self.players):
                self.comboBox_player.addItem("Player %s" % str(i+1))
            self.bcinetworks.append(bcinet)
            self.bcinetwork2player[bcinet] = self.players

        
    def playerChanged(self, index):
        if index < 0:
            pass
        elif index == 0:
            l = []
            if self.players == 0:
                l = []
            elif self.players == 1:
                l = self.feedbacks[0]
            else:
                s = set(self.feedbacks[0])
                for i in xrange(1, self.players):
                    s = s.intersection(self.feedbacks[i])
                l = list(s)
            self.comboBox_feedback.clear()
            l.sort()
            self.comboBox_feedback.addItems(l)
        else:
            self.comboBox_feedback.clear()
            self.comboBox_feedback.addItems(self.feedbacks[index-1])
        
        
    
    def clearFilter(self):
        self.lineEdit.clear()

    
    def filter(self, text):
        text = unicode(text)
        self.proxymodel.setFilterRegExp(QtCore.QRegExp(text, QtCore.Qt.CaseInsensitive, QtCore.QRegExp.FixedString))
        

class TableModel(QtCore.QAbstractTableModel):
    
    def __init__(self, parent = None):
        QtCore.QAbstractTableModel.__init__(self, parent)
        self.entry = []
        self.entriesPerPlayer = dict()
        
        self.header = ["Name", "Value", "Type", "Hidden", "Player"]
#        for i in xrange(len(self.header)):
#            self.setHeaderData(i, QtCore.Qt.Horizontal, QtCore.QVariant("foo"))#self.header[i]))
            
    
    def rowCount(self, parent):
        return len(self.entry)
    
    def columnCount(self, parent):
        return len(self.header)
    
    def data(self, index, role):
        if not index.isValid() or role != QtCore.Qt.DisplayRole:
            return QtCore.QVariant()
        return QtCore.QVariant(str(self.entry[index.row()][index.column()]))
    
    def headerData(self, section, orientation, role):
        if role != QtCore.Qt.DisplayRole:
            return QtCore.QVariant()
        if orientation == QtCore.Qt.Horizontal:
            return QtCore.QVariant(self.header[section])
        else:
            return QtCore.QVariant(int(section))
        
    def setData(self, index, value, role):
        if not index.isValid():
            return False
        #if not self.entry[index.row()].isValid(value.toString()):
        #    return False 
        #self.entry[index.row()][index.column()] = unicode(value.toString())
        self.entry[index.row()].setValue(str(value.toString()))
        self.emit(QtCore.SIGNAL("dataChanged(const QModelIndex &, const QModelIndex &)"), index, index)
        return True
        
    def flags(self, index):
        r = QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled
        if index.column() == 1:
            r = r | QtCore.Qt.ItemIsEditable
        return r
    
    # Own methods:
    def addElement(self, entry):
        player = entry.player
        if not self.entriesPerPlayer.has_key(player):
            self.entriesPerPlayer[player] = 1
        else:
            self.entriesPerPlayer[player] += 1
        pos = len(self.entry)
        self.beginInsertRows(QtCore.QModelIndex(), pos, pos+1)
        self.entry.append(entry)
        self.endInsertRows()
    
    def setElements(self, entries):
        self.entry = []
        self.beginInsertRows(QtCore.QModelIndex(), 0, len(entries))
        for i in entries:
            player = i.player
            if not self.entriesPerPlayer.has_key(player):
                self.entriesPerPlayer[player] = 1
            else:
                self.entriesPerPlayer[player] += 1
            self.entry.append(i)
        self.endInsertRows()
        self.emit(QtCore.SIGNAL("layoutChanged()"))

        

class Entry(object):
    """
    Represents an entry in the table, containing: name, value, the important
    flag and probably other fields.
    """
    
    def __init__(self, name, value, important, player):
        self.name = name
        self.value = value
        self.important = important
        self.player = player
        self.type = type(value)#bcixml.XmlEncoder()._XmlEncoder__get_type(value)
        
    def __getitem__(self, i):
        if i == 0:
            return self.name
        elif i == 1:
            return self.value
        elif i == 2:
            return self.type
        elif i == 3:
            return self.important
        elif i == 4:
            return self.player
        else:
            return "ERROR!"
        
    def __setitem__(self, i, value):
        if i == 0:
            self.name = value
        elif i == 1:
            self.value = value
        elif i == 3:
            self.important = value
        elif i == 4:
            self.player = value
        else:
            return "ERROR!"
        
    def __len__(self):
        return 4
        
    def __str__(self):
        return str(self.name) + str(self.value) + str(self.important) + str(self.player)

    def isValid(self, value):
        try:
            t = self.type(value)
            #print type(t)
        except:
            return False
        return True
    
    def setValue(self, value):
        oldValue = self.value
        try:
            newValue = eval(value)
            if self.type == type(newValue):
                self.value = newValue
        except:
            self.value = oldValue
    

if __name__ == "__main__":
    loglevel = logging.DEBUG
    logging.basicConfig(level=loglevel, format='%(name)-12s %(levelname)-8s %(message)s')
    
    app = QtGui.QApplication(sys.argv)
    gui = BciGui()
    gui.show()
    
    sys.exit(app.exec_())
