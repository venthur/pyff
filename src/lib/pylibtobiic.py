# pylibtobiic.py -
# Copyright (C) 2010 Andrew Ramsay 
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

# 	This is a Python port of TOBI "interface C"
# 	Initially based on v0.0.1
# 	Updated to 0.0.3 (25/10/2010)

from xml.dom.minidom import Document
from xml.dom.minidom import parseString

ICTYPES_ENTRY_UNDEF 		= "undef"
ICTYPES_ENTRY_PROB 			= "prob"
ICTYPES_ENTRY_DIST 			= "dist"
ICTYPES_ENTRY_CLBL 			= "clbl"
ICTYPES_ENTRY_RCOE 			= "rcoe"

ICTYPES_LABEL_UNDEF 		= "undef"
ICTYPES_LABEL_BIOSIG 		= "biosig"
ICTYPES_LABEL_CLASS 		= "class"
ICTYPES_LABEL_CUSTOM 		= "custom"

ICMESSAGE_VERSION 			= "0.0.3.0"
ICMESSAGE_ROOTNODE 			= "messagec"
ICMESSAGE_VERSIONNODE		= "version"
ICMESSAGE_CLASSNODE 		= "class"
ICMESSAGE_CLASSISIFERNODE 	= "classifier"
ICMESSAGE_LABELNODE			= "label"
ICMESSAGE_NAMENODE			= "name"
ICMESSAGE_DESCNODE			= "description"
ICMESSAGE_LTYPENODE			= "ltype"
ICMESSAGE_VTYPENODE			= "vtype"

ICCLASS_CHVALUE_SIZE 	= 64
ICCLASS_CHLABEL_SIZE 	= 64

ICCLASSIFIER_CHNAME_SIZE  	 	= 128
ICCLASSIFIER_CHDESC_SIZE 		= 128

#
# 	ICSetClass
#
class ICSetClass:
	def __init__(self):
		self.map = {}

	def Add(self, pclass):
		if self.map.has_key(pclass.GetLabel()):
			return None

		self.map[pclass.GetLabel()] = pclass
		return pclass

	def Remove(self, lclass):
		if not isinstance(lclass, basestring):
			lclass = lclass.GetLabel()

		if not self.map.has_key(lclass):
			return None

		r = self.map[lclass]
		del self.map[lclass]
		return r
	
	def Get(self, lclass):
		if not isinstance(lclass, basestring):
			lclass = lclass.GetLabel()

		if not self.map.has_key(lclass):
			return None

		return self.map[lclass]

	def Has(self, lclass):
		if not isinstance(lclass, basestring):
			lclass = lclass.GetLabel()

		return self.map.has_key(lclass)

	def Empty(self):
		return (len(self.map) == 0)

	def Clear(self):
		self.map.clear()

	def Destroy(self):
		self.Clear()

# 
# 	ICSetClassifier
#
class ICSetClassifier:
	def __init__(self):
		self.map = {}

	def Add(self, pclr):
		if self.map.has_key(pclr.GetName()):
			return None

		self.map[pclr.GetName()] = pclr
		return pclr

	def Remove(self, nclr):
		if not isinstance(nclr, basestring):
			nclr = nclr.GetName()

		if not self.map.has_key(nclr):
			return None

		r = self.map[nclr]
		del self.map[nclr]
		return r

	def Get(self, nclr):
		if not isinstance(nclr, basestring):
			nclr = nclr.GetName()

		if not self.map.has_key(nclr):
			return None

		return self.map[nclr]

	def Has(self, nclr):
		if not isinstance(nclr, basestring):
			nclr = nclr.GetName()

		return self.map.has_key(nclr)

	def Empty(self):
		return (len(self.map) == 0)

	def Clear(self):
		self.map.clear()

	def Destroy(self):
		self.Clear()

#
# 	ICMessage
#
class ICMessage:
	def __init__(self):
		self.classifiers = ICSetClassifier()

	def GetClassifier(self, name):
		return self.classifiers.Get(name)

	def GetClass(self, name, label):
		return self.classifiers.Get(name).classes.Get(label)

	def GetValue(self, name, label):
		return self.classifiers.Get(name).classes.Get(label).GetValue()

	def SetValue(self, name, label, value):
		return self.classifiers.Get(name).classes.Get(label).SetValue(value)

	def Dump(self):
		if self.classifiers.Empty():
			print "[ICMessage::Dump] Eternal sunshine of an empty message"
			return

		print "[ICMessage::Dump] Dumping internal structure"
		for k in self.classifiers.map.keys():
			v = self.classifiers.Get(k)
			print "+ Classifier %s [\"%s\", ValueType=%d LabelType=%d]" % (v.GetName(), v.GetDescription(), v.GetValueType(), v.GetLabelType())

			for k2 in v.classes.map.keys():
				v2 = v.classes.map[k2]
				print "   --> Class Value=%.6f Label=%s" % (v2.GetValue(), v2.GetLabel())

# 
# 	ICClass
#
class ICClass:
	def __init__(self, label, value = 0.00):
		self.SetLabel(label)
		self.SetValue(value)
		self.classes = ICSetClass()

	def GetValue(self):
		return self._value

	def GetLabel(self):
		return self._label

	def SetValue(self, newvalue = 0.00):
		self._value = newvalue

	def SetLabel(self, newlabel):
		assert(len(newlabel) <= ICCLASS_CHLABEL_SIZE)
		self._label = newlabel

	def GetChValue(self):
		return str(self._value)

	def GetChLabel(self):
		return self._label

# 
# 	ICClassifier
#
class ICClassifier:
	ValueUndef 	= -1 		# 	Undefined class value type
	ValueProb 	= 0 		#  	Probabilities
	ValueDist 	= 1 		# 	Distances
	ValueCLbl 	= 2 		# 	Labels
	ValueRCoe 	= 3 		# 	Regression coefficients

	LabelUndef 	= -1 		# 	Undefined class label type
	LabelBiosig = 0 		# 	Biosig hex labels
	LabelCustom = 1 		# 	Custom labels
	LabelClass = 2

	def __init__(self, name, desc, vtype, ltype):
		self._name = name
		self._desc = desc
		self._vtype = vtype
		self._ltype = ltype
		self.classes = ICSetClass()

	def GetName(self):
		return self._name

	def GetDescription(self):
		return self._desc

	def GetChName(self):
		if len(self._name) > ICCLASSIFIER_CHNAME_SIZE:
			return None

		return self._name

	def GetChDescription(self):
		if len(self._desc) > ICCLASSIFIER_CHDESC_SIZE:
			return None

		return self._desc

	def GetValueType(self):
		return self._vtype

	def GetLabelType(self):
		return self._ltype

	def SetValueType(self, vtype):
		if vtype < ICClassifier.ValueUndef or vtype > ICClassifier.ValueRcoe:
			return False
		self._vtype = vtype
		return True

	def SetLabelType(self, ltype):
		if ltype < ICClassifier.LabelUndef or ltype > ICClassifier.LabelClass:
			return False
		self._ltype = ltype
		return True

	def SetValueTypeString(self, vtypes):
		if vtypes == "ValueUndef":
			self._vtype = ICClassifier.ValueUndef
		elif vtypes == "ValueProb":
			self._vtype = ICClassifier.ValueProb
		elif vtypes == "ValueDist":
			self._vtype = ICClassifier.ValueDist
		elif vtypes == "ValueCLbl":
			self._vtype = ICClassifier.ValueCLbl
		elif vtypes == "ValueRcoe":
			self._vtype = ICClassifier.ValueRCoe
		else:
			return False
		return True

	def SetLabelTypeString(self, ltypes):
		if ltypes == "LabelUndef":
			self._ltype = ICClassifier.LabelUndef
		elif ltypes == "LabelBiosig":
			self._ltype = ICClassifier.LabelBiosig
		elif ltypes == "LabelCustom":
			self._ltype = ICClassifier.LabelCustom
		elif ltypes == "LabelClass":
			self._ltype = ICClassifier.LabelClass
		else:
			return False
		return True

	@staticmethod
	def ValueType(vtype):
		cvtype = ICClassifier.ValueUndef

		if vtype == ICTYPES_ENTRY_PROB:
			cvtype = ICClassifier.ValueProb
		elif vtype == ICTYPES_ENTRY_DIST:
			cvtype = ICClassifier.ValueDist
		elif vtype == ICTYPES_ENTRY_CLBL:
			cvtype = ICClassifier.ValueCLbl
		elif vtype == ICTYPES_ENTRY_RCOE:
			cvtype = ICClassifier.ValueRCoe
		
		return cvtype

	@staticmethod
	def LabelType(ltype):
		cltype = ICClassifier.LabelUndef

		if ltype == ICTYPES_LABEL_CUSTOM:
			cltype = ICClassifier.LabelCustom
		elif ltype == ICTYPES_LABEL_BIOSIG:
			cltype = ICClassifier.LabelBiosig
		elif ltype == ICTYPES_LABEL_CLASS:
			cltype = ICClassifier.LabelClass

		return cltype

	@staticmethod
	def ValueChType(vtype):
		assert(vtype != None)
		cvtype = ICClassifier.ValueUndef

		if vtype == ICTYPES_ENTRY_PROB:
			cvtype = ICClassifier.ValueProb
		elif vtype == ICTYPES_ENTRY_DIST:
			cvtype = ICClassifier.ValueDist
		elif vtype == ICTYPES_ENTRY_CLBL:
			cvtype = ICClassifier.ValueCLbl
		elif vtype == ICTYPES_ENTRY_RCOE:
			cvtype = ICClassifier.ValueRCoe

		return cvtype

	@staticmethod
	def LabelChType(ltype):
		assert(ltype != None)

		cltype = ICClassifier.LabelUndef

		if ltype == ICTYPES_LABEL_CUSTOM:
			cltype = ICClassifier.LabelCustom
		elif ltype == ICTYPES_LABEL_BIOSIG:
			cltype = ICClassifier.LabelBiosig
		elif type == ICTYPES_LABEL_CLASS:
			cltype = ICClassifier.LabelClass

		return cltype

#
# 	ICSerializer
#
class ICSerializer:
	def __init__(self, message, indent=False):
		self._message = message

	def SetMessage(self, message):
		self._message = message

	def Serialize(self):
		if not self._message:
			return None

		# Create an XML document object
		doc = Document()

		# Root node
		root = doc.createElement(ICMESSAGE_ROOTNODE)
		root.setAttribute(ICMESSAGE_VERSIONNODE, ICMESSAGE_VERSION)
		doc.appendChild(root)

		# Classifiers
		for cname in self._message.classifiers.map:
			classifier = self._message.classifiers.Get(cname)
			cnode = doc.createElement(ICMESSAGE_CLASSISIFERNODE)
			cnode.setAttribute(ICMESSAGE_NAMENODE, classifier.GetChName())
			cnode.setAttribute(ICMESSAGE_DESCNODE, classifier.GetChDescription())

			root.appendChild(cnode)

			# Attribute: Value Type
			vtype = classifier.GetValueType()
			pvtype = ICTYPES_ENTRY_UNDEF

			if vtype == ICClassifier.ValueUndef:
				pvtype = ICTYPES_ENTRY_UNDEF
			elif vtype == ICClassifier.ValueProb:
				pvtype = ICTYPES_ENTRY_PROB
			elif vtype == ICClassifier.ValueDist:
				pvtype = ICTYPES_ENTRY_DIST
			elif vtype == ICClassifier.ValueCLbl:
				pvtype = ICTYPES_ENTRY_CLBL
			elif vtype == ICClassifier.ValueRCoe:
				pvtype = ICTYPES_ENTRY_RCOE

			cnode.setAttribute(ICMESSAGE_VTYPENODE, pvtype)

			# Attribute: Label Type
			ltype = classifier.GetLabelType()
			pltype = ICTYPES_LABEL_UNDEF

			if ltype == ICClassifier.LabelUndef:
				pltype = ICTYPES_LABEL_UNDEF
			elif ltype == ICClassifier.LabelBiosig:
				pltype = ICTYPES_LABEL_BIOSIG
			elif ltype == ICClassifier.LabelClass:
				pltype = ICTYPES_LABEL_CLASS
			elif ltype == ICClassifier.LabelCustom:
				pltype = ICTYPES_LABEL_CUSTOM

			cnode.setAttribute(ICMESSAGE_LTYPENODE, pltype)

			# Loop over classes
			for theclassname in classifier.classes.map:
				theclass = classifier.classes.Get(theclassname)
				knode = doc.createElement(ICMESSAGE_CLASSNODE)
				textnode = doc.createTextNode(theclass.GetChValue())
				knode.appendChild(textnode)
				knode.setAttribute(ICMESSAGE_LABELNODE, theclass.GetChLabel())
				cnode.appendChild(knode)

		return doc.toxml()

	def Deserialize(self, msg):
		initialize = self._message.classifiers.Empty()

		try:
			doc = parseString(msg)
		except:
			return None

		root = doc.documentElement
	
		# check version
		if not root.hasAttribute(ICMESSAGE_VERSIONNODE) or root.getAttribute(ICMESSAGE_VERSIONNODE) != ICMESSAGE_VERSION:
			return None

		# traverse classifier nodes
		classifier_nodes = root.getElementsByTagName(ICMESSAGE_CLASSISIFERNODE)
		for cnode in classifier_nodes:
			cptr = None
			# get name, description, value and label types
			cname = cnode.getAttribute(ICMESSAGE_NAMENODE)
			if initialize:
				cdesc = cnode.getAttribute(ICMESSAGE_DESCNODE)
				tvtype = cnode.getAttribute(ICMESSAGE_VTYPENODE)
				tltype = cnode.getAttribute(ICMESSAGE_LTYPENODE)

				# convert value and label types
				cvtype = ICClassifier.ValueType(tvtype)
				cltype = ICClassifier.LabelType(tltype)

				# create classifier
				if self._message.classifiers.Has(cname):
					return None

				cptr = ICClassifier(cname, cdesc, cvtype, cltype)
				self._message.classifiers.Add(cptr)
			else:
				cptr = self._message.classifiers.Get(cname)

			# traverse class nodes
			class_nodes = cnode.getElementsByTagName(ICMESSAGE_CLASSNODE)
			for knode in class_nodes:
				klabel = knode.getAttribute(ICMESSAGE_LABELNODE)
				tvalue = knode.firstChild.data

				if initialize:
					if cptr.classes.Has(klabel):
						return None
					print klabel, tvalue
					kptr = ICClass(klabel, float(tvalue))
					cptr.classes.Add(kptr)
				else:
					cptr.classes.Get(klabel).SetValue(float(tvalue))

		return msg
