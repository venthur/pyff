#!/usr/bin/env python

# GUI.py -
# Copyright (C) 2007-2011  Bastian Venthur
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

from lib import bcinetwork
from lib import bcixml


NORMAL_COLOR = QtCore.Qt.black
MODIFIED_COLOR = QtCore.Qt.gray

class BciGui(QtGui.QMainWindow, Ui_MainWindow):

    def __init__(self, protocol='bcixml'):
        QtGui.QMainWindow.__init__(self)
        self.setupUi(self)

#        self.model = TableModel(self.tableView)
#        self.tableView.setModel(self.model)

        self.model = TableModel(self)
        self.proxymodel = QtGui.QSortFilterProxyModel(self)
        self.proxymodel.setSourceModel(self.model)
        self.proxymodel.setFilterKeyColumn(- 1)
        self.proxymodel.setDynamicSortFilter(True)
        self.tableView.setModel(self.proxymodel)
        self.tableView.verticalHeader().setVisible(False)
        self.tableView.horizontalHeader().setResizeMode(1, QtGui.QHeaderView.Stretch)
        self.tableView.sortByColumn(0, QtCore.Qt.AscendingOrder)
        self.tableView.setSortingEnabled(True)


        # connect toolbuttons to actions
        self.toolButton_clearFilter.setDefaultAction(self.actionClearFilter)
        # put the combobox into the toolbar before the sendinit action
        self.comboBox_feedback = QtGui.QComboBox(self.toolBar)
        self.comboBox_feedback.setSizePolicy(QtGui.QSizePolicy.Expanding,
                                             QtGui.QSizePolicy.Preferred)
        self.toolBar.insertWidget(self.actionSendInit, self.comboBox_feedback)

        # connect actions to methods
        #QtCore.QObject.connect(self.actionOpen, QtCore.SIGNAL("triggered()"), self.clicked)
        QtCore.QObject.connect(self.actionChangeFeedbackController, QtCore.SIGNAL("triggered()"), self.changeFeedbackController)
        QtCore.QObject.connect(self.actionClearFilter, QtCore.SIGNAL("triggered()"), self.clearFilter)
        QtCore.QObject.connect(self.actionOpen, QtCore.SIGNAL("triggered()"), self.open)
        QtCore.QObject.connect(self.actionPause, QtCore.SIGNAL("triggered()"), self.pause)
        QtCore.QObject.connect(self.actionPlay, QtCore.SIGNAL("triggered()"), self.play)
        QtCore.QObject.connect(self.actionQuit, QtCore.SIGNAL("triggered()"), self.quit)
        QtCore.QObject.connect(self.actionStop, QtCore.SIGNAL("triggered()"), self.stop)
        QtCore.QObject.connect(self.actionSave, QtCore.SIGNAL("triggered()"), self.save)
        QtCore.QObject.connect(self.actionSaveAs, QtCore.SIGNAL("triggered()"), self.saveas)
        QtCore.QObject.connect(self.actionSendModified, QtCore.SIGNAL("triggered()"), self.sendModified)
        QtCore.QObject.connect(self.actionSendAll, QtCore.SIGNAL("triggered()"), self.sendAll)
        QtCore.QObject.connect(self.actionSendInit, QtCore.SIGNAL("triggered()"), self.sendinit)
        QtCore.QObject.connect(self.actionGet, QtCore.SIGNAL("triggered()"), self.get)

        QtCore.QObject.connect(self.lineEdit, QtCore.SIGNAL("textChanged(const QString&)"), self.filter)
        QtCore.QObject.connect(self.model, QtCore.SIGNAL("dataChanged(const QModelIndex&, const QModelIndex&)"), self.dataChanged)
        self.feedbacks = []
        self.protocol = protocol
        self.setFeedbackController(bcinetwork.LOCALHOST, bcinetwork.FC_PORT)


    def __del__(self):
        self.fc.stop()
        self.fc.quit_feedback_controller()

    def dataChanged(self):
        self.sendModified()

    def play(self):
        self.fc.play()

    def pause(self):
        self.fc.pause()

    def stop(self):
        self.fc.stop()

    def quit(self):
        self.fc.quit()



    def get(self):
        d = self.fc.get_variables()
        entries = []
        for name, value in d.iteritems():
            e = Entry(name, value)
            entries.append(e)
        # FIXME: this will clear the whole table and just put in the new
        # entries (ignoring the entries of the other players.
        self.model.setElements(entries)


    def sendinit(self):
        feedback = unicode(self.comboBox_feedback.currentText())
        self.fc.send_init(feedback)
        d = self.fc.get_variables()
        entries = []
        for name, value in d.iteritems():
            e = Entry(name, value)
            entries.append(e)
        self.model.setElements(entries)


    def sendModified(self):
        signal = self.makeSignal(True)
        self.fc.send_signal(signal)


    def sendAll(self):
        signal = self.makeSignal()
        self.fc.send_signal(signal)


    def makeSignal(self, modifiedOnly=False):
        """Create an Interaction Signal from the Variables in the Table."""
        data = {}
        for elem in self.model.entry:
            if not modifiedOnly or (modifiedOnly and elem.modified):
                data[elem.name] = elem.value
                # FIXME: should
                elem.modified = False
        signal = bcixml.BciSignal(data, None, bcixml.INTERACTION_SIGNAL)
        return signal


    def open(self):
        filename = QtGui.QFileDialog.getOpenFileName(filter = "Configuration Files (*.json)")
        filename = unicode(filename)
        self.fc.load_configuration(filename)


    def save(self):
        filename = QtGui.QFileDialog.getSaveFileName(filter = "Configuration Files (*.json)")
        filename = unicode(filename)
        self.fc.save_configuration(filename)

    def saveas(self):
        pass


    def changeFeedbackController(self):
        try:
            ip, port = self.getFeedbackControllerAddress()
            self.setFeedbackController(ip, port)
        except:
            self.logger.error("Unable to connect to Feedback Controller under %s:%s" % (ip, port))


    def getFeedbackControllerAddress(self):
        text, ok = QtGui.QInputDialog.getText(self, "Add Feedback Controller", "Please enter the address[:port] of the Feedback Controller.\n\nThe adress can be a hostname or numeric, the port is optional.")
        if not ok:
            raise Exception

        ip, port = bcinetwork.LOCALHOST, bcinetwork.FC_PORT
        ipport = text.split(":")
        if len(ipport) >= 1:
            ip = ipport[0]
        if len(ipport) >= 2:
            port = ipport[1]
        return ip, port


    def setFeedbackController(self, ip, port):
        # ask feedback controller under given ip for available feedbacks
        bcinet = bcinetwork.BciNetwork(ip, port, bcinetwork.GUI_PORT, self.protocol)
        feedbacks = bcinet.getAvailableFeedbacks()

        if not feedbacks:
            QtGui.QMessageBox.warning(self,
                "Ooops!",
                "The Feedback Controller under the given adress: %s did not respond or has no feedbacks available!\n\nIt was not added to the list of available Feedback Controllers." % unicode(ip) + ":" + unicode(port))
            return
        else:
            feedbacks.sort()
            self.feedbacks = feedbacks
            self.fc = bcinet
            self.update_feedback_box()
            self.statusbar.showMessage("Feedback Controller: %s:%s" % (ip, port))


    def update_feedback_box(self):
        self.comboBox_feedback.clear()
        self.comboBox_feedback.addItems(self.feedbacks)


    def clearFilter(self):
        self.lineEdit.clear()


    def filter(self, text):
        text = unicode(text)
        self.proxymodel.setFilterRegExp(QtCore.QRegExp(text, QtCore.Qt.CaseInsensitive, QtCore.QRegExp.FixedString))


class TableModel(QtCore.QAbstractTableModel):

    def __init__(self, parent=None):
        QtCore.QAbstractTableModel.__init__(self, parent)
        self.entry = []
        self.entryCount = 0

        self.header = ["Name", "Value", "Type"]
#        for i in xrange(len(self.header)):
#            self.setHeaderData(i, QtCore.Qt.Horizontal, QtCore.QVariant("foo"))#self.header[i]))


    def rowCount(self, parent):
        return len(self.entry)

    def columnCount(self, parent):
        return len(self.header)

    def data(self, index, role):
        if not index.isValid():
            return QtCore.QVariant()
        if role == QtCore.Qt.ForegroundRole:
            c = MODIFIED_COLOR if self.entry[index.row()].modified else NORMAL_COLOR
            return QtCore.QVariant(QtGui.QColor(c))
        if role != QtCore.Qt.DisplayRole:
            return QtCore.QVariant()
        return QtCore.QVariant(unicode(self.entry[index.row()][index.column()]))

    def headerData(self, section, orientation, role):
        if role != QtCore.Qt.DisplayRole:
            return QtCore.QVariant()
        if orientation == QtCore.Qt.Horizontal:
            return QtCore.QVariant(self.header[section])
        else:
            return QtCore.QVariant(int(section))

    def setData(self, index, value, role):
        """Is called whenever the user modified a value in the table."""
        if not index.isValid():
            return False
        #if not self.entry[index.row()].isValid(value.toString()):
        #    return False
        #self.entry[index.row()][index.column()] = unicode(value.toString())
        self.entry[index.row()].setValue(unicode(value.toString()))
        self.entry[index.row()].modified = True
        self.emit(QtCore.SIGNAL("dataChanged(const QModelIndex &, const QModelIndex &)"), index, index)
        return True

    def flags(self, index):
        r = QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled
        if index.column() == 1:
            r = r | QtCore.Qt.ItemIsEditable
        return r

    # Own methods:
    def addElement(self, entry):
        self.entryCount += 1
        pos = len(self.entry)
        self.beginInsertRows(QtCore.QModelIndex(), pos, pos + 1)
        self.entry.append(entry)
        self.endInsertRows()
        self.emit(QtCore.SIGNAL("layoutChanged()"))


    def setElements(self, entries):
        self.beginRemoveRows(QtCore.QModelIndex(), 0, len(self.entry)-1)
        self.entry = []
        self.endRemoveRows()
        self.beginInsertRows(QtCore.QModelIndex(), 0, len(entries)-1)
        self.entryCount = len(entries)
        for i in entries:
            self.entry.append(i)
        self.endInsertRows()
        self.emit(QtCore.SIGNAL("layoutChanged()"))


class Entry(object):
    """
    Represents an entry in the table, containing: name, value, the important
    flag and probably other fields.
    """

    def __init__(self, name, value):
        self.name = name
        self.value = value
        self.type = type(value)#bcixml.XmlEncoder()._XmlEncoder__get_type(value)
        self.modified = False

    def __getitem__(self, i):
        if i == 0:
            return self.name
        elif i == 1:
            return self.value
        elif i == 2:
            return self.type
        else:
            return "ERROR!"

    def __setitem__(self, i, value):
        if i == 0:
            self.name = value
        elif i == 1:
            self.value = value
        else:
            return "ERROR!"

    def __len__(self):
        return 3

    def __str__(self):
        return str(self.name) + str(self.value) + str(self.type)

    def isValid(self, value):
        try:
            t = self.type(value)
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


def main(protocol='bcixml'):
    loglevel = logging.DEBUG
    logging.basicConfig(level=loglevel, format='%(name)-12s %(levelname)-8s %(message)s')

    app = QtGui.QApplication(sys.argv)
    gui = BciGui(protocol)
    gui.show()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
