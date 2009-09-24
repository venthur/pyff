# Copyright (C) 2009  Matthias Treder
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

""" 
Implements a matrix layout. A matrix is defined by its
size (width,height) and the number of rows and columns.
The positions are defined row-wise, starting in the top
left corner. 
"""

class MatrixLayout(object):
    
    def __init__(self, size=(200, 200), rows=6, cols=6):
        self.positions = []
        self.rows = rows
        self.cols = cols
        width, height = size
        # Determine positions
        distx = width / (cols - 1)    # x distance between elements
        disty = height / (rows - 1)   # y distance between elements
        
        for r in range(rows):
            for c in range(cols):
                x = round(distx * c - width / 2)
                y = round(disty * r - height / 2)
                self.positions.append((x, y))

    def get_rows_cols(self):
        """
        Just a handy method.
        It returns a list of lists. Each (sub)list contains the indices
        of the elements in one single row or column. The order in which
        the rows/columns are given is: First, the rows are given, starting
        at the top; then, the columns are given, starting left.
        You can call this method from your VisualP300 speller implementation
        to define your groups very easily. 
        """
        rows_cols = []
        # Get rows
        for r in range(self.rows):
            rows_cols.append(range(r * self.cols, (r + 1) * self.cols))
        # Get columns
        for c in range(self.cols):
            column = []
            for r in range(self.rows):
                column.append(c + r * self.cols)
            rows_cols.append(column)
        return rows_cols
             
        

# Test
#m = MatrixLayout(rows=4,cols=4)
#for i in range( len(m.positions) ):
#    print m.positions[i]
#print m.get_rows_cols()