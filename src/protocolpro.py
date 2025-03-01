#!/usr/bin/env python3
################################################################################
#                    ____            _                  _                      #
#                   |  _ \ _ __ ___ | |_ ___   ___ ___ | |                     #
#                   | |_) | '__/ _ \| __/ _ \ / __/ _ \| |                     #
#                   |  __/| | | (_) | || (_) | (_| (_) | |                     #
#                   |_|   |_|  \___/ \__\___/ \___\___/|_|                     #
#                                                                              #
#         == ASCII and Unicode Header Generator for Network Protocols ==       #
#                                                                              #
################################################################################
#                                                                              #
#  Written by:                                                                 #
#                                                                              #
#     Luis MartinGarcia.                                                       #
#       -> E-Mail: luis.mgarc@gmail.com                                        #
#       -> WWWW:   http://www.luismg.com                                       #
#       -> GitHub: https://github.com/luismartingarcia                         #
#                                                                              #
################################################################################
#                                                                              #
#  This file is part of Protocol.                                              #
#                                                                              #
#  Copyright (C) 2014 Luis MartinGarcia (luis.mgarc@gmail.com)                 #
#                                                                              #
#  This program is free software: you can redistribute it and/or modify        #
#  it under the terms of the GNU General Public License as published by        #
#  the Free Software Foundation, either version 3 of the License, or           #
#  (at your option) any later version.                                         #
#                                                                              #
#  This program is distributed in the hope that it will be useful,             #
#  but WITHOUT ANY WARRANTY; without even the implied warranty of              #
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the               #
#  GNU General Public License for more details.                                #
#                                                                              #
#  You should have received a copy of the GNU General Public License           #
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.       #
#                                                                              #
#  Please check file LICENSE.txt for the complete version of the license,      #
#  as this disclaimer does not contain the full information. Also, note        #
#  that although Protocol is licensed under the GNU GPL v3 license, it may     #
#  be possible to obtain copies of it under different, less restrictive,       #
#  alternative licenses. Requests will be studied on a case by case basis.     #
#  If you wish to obtain Protocol under a different license, please contact    #
#  the email address mentioned above.                                          #
#                                                                              #
################################################################################
#                                                                              #
# Description:                                                                 #
#                                                                              #
#  Protocol is a command-line tool that provides quick access to the most      #
#  common network protocol headers in ASCII (RFC-like) format. It also has the #
#  ability to create ASCII headers for custom protocols defined by the user    #
#  through a very simple syntax.                                               #
#                                                                              #
################################################################################

# STANDARD LIBRARY IMPORTS
import sys
from datetime import date

# INTERNAL IMPORTS
from constants import (
    APPLICATION_NAME, APPLICATION_VERSION,
    APPLICATION_AUTHOR, APPLICATION_AUTHOR_EMAIL,
    OP_FAILURE, OP_SUCCESS
)
import specs


# CLASS DEFINITIONS
class ProtocolException(Exception):
    """
    This class represents exceptions raised by the Protocol class
    """

    def __init__(self, errmsg):
        self.errmsg = errmsg

    def __str__(self):
        return str(self.errmsg)


class Protocol():
    """
    This class represents a network protocol header. Objects are constructed by
    passing a textual protocol specification. Once that is done, instances
    can be printed by converting them to a str type.
    """

    def __init__(self, spec):
        """
        Class constructor.
        @param spec is the textual specification that describes the protocol.
        """
        # unicode
        self.u_top_hdr_char_start = "┌"         # Character for start of the top border line
        self.u_top_hdr_char_end = "┐"           # Character for end of the top border line
        self.u_bottom_hdr_char_start = "└"      # Character for start of the bottom border line
        self.u_bottom_hdr_char_end = "┘"        # Character for end of the bottom border line
        self.u_hdr_char_start = "├"             # Character for start of the border line
        self.u_hdr_char_end = "┤"               # Character for end of the border line
        self.u_hdr_char_fill = "─"              # Fill character for border positions
        self.u_hdr_char_sep = "│"               # Field separator character
        self.u_hdr_connector_down = '┬'
        self.u_hdr_connector_up = '┴'
        self.u_hdr_connector_cross = '┼'

        # ASCII
        self.hdr_char_start = "+"               # Character for start of the border line
        self.hdr_char_end = "+"                 # Character for end of the border line
        self.hdr_char_fill_odd = "+"            # Fill character for border odd positions
        self.hdr_char_fill_even = "-"           # Fill character for border even positions
        self.hdr_char_sep = "|"                 # Field separator character

        self.bits_per_line = 32                 # Number of bits per line
        self.do_print_top_tens = True           # True: print top numbers for bit tens
        self.do_print_top_units = True          # True: print top numbers for bit units
        self.do_ascii = True                    # True: print ASCII box characters
        self.do_unicode = False                 # False: print unicode box characters
        self.field_list = []                    # Header fields to be printed out
        self.parse_spec(spec)                   # Parse the received spec and populate self.field_list

    def parse_spec(self, spec):
        """
        Parses a textual protocol spec and stores the relevant internal state
        so such spec can be later converted to a nice ASCII diagram.
        @return the list of protocol fields, as a dictionary containing
        keys 'len' and 'text'. The list is returned for completeness but no
        caller is expected to store or use such list.
        @raise ProtocolException in case the supplied spec is not valid
        """
        if "?" in spec:
            parts = spec.split("?")
            fields = parts[0]
            opts = parts[1]
            if spec.count("?") > 1:
                raise ProtocolException(
                    "FATAL: Character '?' may only be used as an option separator."
                )
        else:
            fields = spec
            opts = None

        # Parse field spec
        items = fields.split(",")
        for item in items:
            try:
                text, bits = item.split(":")
                bits = int(bits)
                if bits <= 0:
                    raise ProtocolException(
                        "FATAL: Fields must be at least one bit long (%s)" % spec
                    )
            except ProtocolException:
                raise
            except:
                raise ProtocolException(
                    "FATAL: Invalid field_list specification (%s)" % spec
                )
            self.field_list.append({"text": text, "len": bits})

        # Parse options
        if opts is not None:
            opts = opts.split(",")
            for opt in opts:
                try:
                    var, value = opt.split("=")
                    if var.lower() == "bits":
                        self.bits_per_line = int(value)
                        if self.bits_per_line <= 0:
                            raise ProtocolException(
                                "FATAL: Invalid value for 'bits' option (%s)" % value
                            )
                    elif var.lower() == "numbers":
                        if value.lower() in ["0", "n", "no", "none", "false"]:
                            self.do_print_top_tens = False
                            self.do_print_top_units = False
                        elif value.lower() in ["1", "y", "yes", "none", "true"]:
                            self.do_print_top_tens = True
                            self.do_print_top_units = True
                        else:
                            raise ProtocolException(
                                "FATAL: Invalid value for 'numbers' option (%s)" % value
                            )
                    elif var.lower() in [
                        "oddchar", "evenchar", "startchar", "endchar", "sepchar"
                    ]:
                        if len(value) > 1 or len(value) <= 0:
                            raise ProtocolException(
                                "FATAL: Invalid value for '%s' option (%s)" % (var, value)
                            )
                        else:
                            if var.lower() == "oddchar":
                                self.hdr_char_fill_odd = value
                            elif var.lower() == "evenchar":
                                self.hdr_char_fill_even = value
                            elif var.lower() == "startchar":
                                self.hdr_char_start = value
                            elif var.lower() == "endchar":
                                self.hdr_char_end = value
                            elif var.lower() == "sepchar":
                                self.hdr_char_sep = value
                except ProtocolException:
                    raise
                except:
                    raise ProtocolException("FATAL: Invalid options specification (%s)" % opt)

        return self.field_list

    def _get_top_numbers(self):
        """
        @return a string representing the bit units and bit tens on top of the
        protocol header. Note that a proper string is only returned if one or
        both self.do_print_top_tens and self.do_print_top_units is True.
        The returned string is not \n terminated, but it may contain a newline
        character in the middle.
        """
        lines = ["", ""]
        if self.do_print_top_tens is True:
            lines[0] += " "
            for i in range(0, self.bits_per_line):
                if i % 8 == 0 and ((i+8)>=self.bits_per_line):
                    #lines[0] += "{:<16}".format(str(i))
                    lines[0] += "{:<8}{:>8}".format(str(i),str(self.bits_per_line-1))
                elif i % 8 == 0:
                    lines[0] += "{:<16}".format(str(i))
            lines[0] += "\n"
        if self.do_print_top_units is True:
            for i in range(0, self.bits_per_line):
                lines[1] += " %s" % (i%8)
            # lines[1] += "\n"
        result = "".join(lines)
        return result if len(result) > 0 else None

    def _get_horizontal(self, width=None, textline=None, fields=None, bottom=False, offset=0):
        """
        @return the horizontal border line that separates field rows.
        @param width controls how many field bits the line should cover. By
        default, if no width is supplied, the line covers the hole length of
        the header.
        """
        if width is None:
            width = self.bits_per_line
        elif width <= 0:
            return ""

        # if above first text line then at the top
        if textline == 1:
            top = True
        else:
            top = False

        # first character of the line
        if self.do_unicode:
            if top is True or offset > 0:
                a = "%s" % self.u_top_hdr_char_start
            elif bottom is True:
                if width < self.bits_per_line:
                    a = "%s" % self.u_hdr_char_start
                else:
                    a = "%s" % self.u_bottom_hdr_char_start
            else:
                a = "%s" % self.u_hdr_char_start
        else:
            a = "%s" % self.hdr_char_start

        if self.do_unicode:
            # create the baseline
            chars = []
            for i in range(2 * (width-1)):
                chars.append(self.u_hdr_char_fill)

            # look at fields to determine where up or down connections are made
            start_above = set()
            start_below = set()
            for field in fields:
                if field["start"] != 0:
                    if field["line"] == textline:
                        index = 2 * field["start"] - 1
                        if index < len(chars):
                            chars[index] = self.u_hdr_connector_down
                            start_above.add(field["start"])
                    # if field["line"] == textline - 1 and field["MF"] is False:
                    if field["line"] == textline - 1:
                        index = 2 * field["start"] - 1
                        if index < len(chars):
                            chars[index] = self.u_hdr_connector_up
                            start_below.add(field["start"])

            # look for cross connectors
            if top is False and bottom is False:
                positions = start_above.intersection(start_below)
                for position in positions:
                    chars[2 * position - 1] = self.u_hdr_connector_cross

            b = "".join(chars)

        else:
            # if ASCII, alternate +- characters between first and last
            b = (self.hdr_char_fill_even+self.hdr_char_fill_odd)*(width-1)

        # last character of the line
        if self.do_unicode:
            if top is True:
                c = "%s%s" % (self.u_hdr_char_fill, self.u_top_hdr_char_end)
            elif bottom is True:
                c = "%s%s" % (self.u_hdr_char_fill, self.u_bottom_hdr_char_end)
            else:
                # if the field ends here and the next field spans, we need a corner
                # TODO
                c = "%s%s" % (self.u_hdr_char_fill, self.u_hdr_char_end)
        else:
            c = "%s%s" % (self.hdr_char_fill_even, self.hdr_char_end)
        return a+b+c

    def _get_separator(self, line_end=""):
        """
        @return a string containing a protocol field separator. Returned string
        is a single character and matches whatever is stored in self.hdr_char_sep
        """
        if self.do_unicode:
            return self.u_hdr_char_sep
        else:
            return self.hdr_char_sep

    def _process_field_list(self):
        """
        Processes the list of protocol fields that we got from the spec and turns
        it into something that we can print easily (useful for cases when we have
        protocol fields that span more than one line). This is just a helper
        function to make __str__()'s life easier.
        """
        new_fields = []
        bits_in_line = 0
        i = 0
        text_line = 1
        while i < len(self.field_list):
            # Extract all the info we need about the field
            field = self.field_list[i]
            field_text = field['text']
            field['MF'] = False

            available_in_line = self.bits_per_line - bits_in_line

            # If we have enough space on this line to include the current field
            # then just keep it as it is.
            if available_in_line >= field['len']:
                field['line'] = text_line
                field['start'] = bits_in_line
                bits_in_line += field['len']
                field['end'] = bits_in_line - 1
                new_fields.append(field)
                i += 1
                if bits_in_line == self.bits_per_line:
                    bits_in_line = 0
                    text_line += 1
            # Otherwise, split the field into two parts, one blank and one with
            # the actual field text
            else:

                # Case 1: We have a field that is perfectly aligned and it
                # has a length that is multiple of our line length
                if bits_in_line == 0 and field['len'] % self.bits_per_line == 0:
                    field['start'] = 0
                    field['end'] = self.bits_per_line - 1
                    field['line'] = text_line
                    text_line += 1
                    new_fields.append(field)
                    i += 1

                # Case 2: We weren't that lucky and the field is either not
                # aligned or we can't print it using an exact number of full
                # lines
                else:

                    # If we have more space in the current line than in the next,
                    # then put the field text in this one
                    if available_in_line >= field['len']-available_in_line:
                        new_field = {
                            'text': field_text, 'len': available_in_line, "MF": True,
                            'start': bits_in_line, 'end': self.bits_per_line - 1,
                            'line': text_line,
                        }
                        new_fields.append(new_field)
                        field['text'] = ""
                        field['len'] = field['len']-available_in_line
                        field['MF'] = False
                    else:
                        new_field = {
                            'text': "", 'len': available_in_line, "MF": True,
                            'start': bits_in_line, 'end': self.bits_per_line - 1,
                            'line': text_line,
                        }
                        new_fields.append(new_field)
                        field['text'] = field_text
                        field['len'] = field['len']-available_in_line
                        field['MF'] = False
                    bits_in_line = 0
                    text_line += 1
                    continue
        return new_fields

    # Convert to string
    def __str__(self):
        """
        Converts the protocol specification stored in the object to a nice
        ASCII diagram like the ones that appear in RFCs. Conversion supports
        fields of any length, and supports field that span more than one
        line in the diagram.
        @return a string containing the ASCII representation of the protocol
        header.
        """

        # First of all, process our field list. This does some magic to make
        # the algorithm work for fields that span more than one line
        proto_fields = self._process_field_list()
        lines = []
        numbers = self._get_top_numbers()
        if numbers is not None:
            lines.append(numbers)
        textline = 1
        lines.append(self._get_horizontal(textline=textline, fields=proto_fields))

        # Print all protocol fields
        bits_in_line = 0
        current_line = ""
        fields_done = 0
        p = -1
        while p < len(proto_fields)-1:
            p += 1

            # Extract all the info we need about the field
            field = proto_fields[p]
            field_text = field['text']
            field_len = field['len']
            field_mf = field['MF'] is True  # Field has more fragments

            # If the field text is too long, we truncate it, and add a dot
            # at the end.
            if len(field_text) > (field_len*2)-1:
                field_text = field_text[0:(field_len*2)-1]
                if len(field_text) > 1:
                    field_text = field_text[0:-1]+"."

            # If we have space for the whole field in the current line, go
            # ahead and add it
            if self.bits_per_line-bits_in_line >= field_len:
                # If this is the first thing we print on a line, add the
                # starting character
                if bits_in_line == 0:
                    current_line += self._get_separator()

                # Add the whole field
                current_line += str.center(field_text, (field_len*2)-1)

                # Update counters
                bits_in_line += field_len
                fields_done += 1

                # If this is the last character in the line, store the line
                if bits_in_line == self.bits_per_line:
                    current_line += self._get_separator()
                    lines.append(current_line)
                    current_line = ""
                    bits_in_line = 0
                    textline += 1
                    # When we have a fragmented field, we may need to suppress
                    # the floor of the field, so the current line connects
                    # with the one that follows. E.g.:
                    # +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
                    # |            field16            |                               |
                    # +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+                               +
                    # |                             field                             |
                    # +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
                    if field_mf is True:
                        if proto_fields[p+1]['len'] > self.bits_per_line - field_len:

                            # Print some +-+-+ to cover the previous field
                            line_left = self._get_horizontal(
                                self.bits_per_line - field_len,
                                textline=textline,
                                fields=proto_fields,
                                bottom=True
                            )
                            if len(line_left) == 0:
                                if self.do_unicode:
                                    line_left = self.u_hdr_char_start
                                else:
                                    line_left = self.hdr_char_start

                            # Now print some empty space to cover the part that
                            # we can join with the field below.
                            # Case 1: If the next field reaches the end of its
                            # line, then we need to print whitespace until the
                            # end our line
                            if proto_fields[p+1]['len'] >= self.bits_per_line:
                                line_center = " " * ((2*(field_len)-1))
                                if self.do_unicode:
                                    line_right = self.u_hdr_char_end
                                else:
                                    line_right = self.hdr_char_end
                            # Case 2: the field in the next row is not big enough
                            # to cover all the space we'd like to join, so we
                            # just print whitespace to cover as much as we can
                            else:
                                line_center = " " * (
                                    (2*((proto_fields[p+1]['len']-(self.bits_per_line-field_len))))-1
                                )
                                line_right = self._get_horizontal(
                                    self.bits_per_line-proto_fields[p+1]['len'],
                                    textline=textline,
                                    fields=proto_fields,
                                    offset=len(line_left) + len(line_center)
                                )

                            lines.append(line_left+line_center+line_right)
                        else:
                            lines.append(
                                self._get_horizontal(textline=textline, fields=proto_fields)
                            )
                    else:
                        bottom = (p == len(proto_fields) - 1)
                        lines.append(
                            self._get_horizontal(textline=textline,
                                                 fields=proto_fields,
                                                 bottom=bottom)
                        )

                # If this is not the last character of the line but we have no
                # more fields to print, wrap up
                elif fields_done == len(proto_fields):
                    current_line += self._get_separator()
                    lines.append(current_line)
                    lines.append(
                        self._get_horizontal(
                            bits_in_line,
                            textline=textline,
                            fields=proto_fields,
                            bottom=True
                        )
                    )
                else:
                    # Add the separator character
                    if self.do_unicode:
                        current_line += self.u_hdr_char_sep
                    else:
                        current_line += self.hdr_char_sep

            # We don't have enough space for the field on this line.
            else:
                # Case 1: We are at the beginning of a new line and we need to
                # span more than one line
                if bits_in_line == 0:
                    # Case 1a: We have a multiple of the number of bits per line
                    if field_len % self.bits_per_line == 0:
                        # Compute how many lines in total we need to print for this
                        # big field.
                        lines_to_print = int(((field_len/self.bits_per_line)*2)-1)
                        # We print the field text in the central line
                        central_line = int(lines_to_print/2)
                        # Print all those lines
                        for i in range(0, lines_to_print):

                            # Let's figure out which character we need to use
                            # to start and end the current line
                            if i % 2 == 1:
                                if self.do_unicode:
                                    start_line = self.u_hdr_char_start
                                    end_line = self.u_hdr_char_end
                                else:
                                    start_line = self.hdr_char_start
                                    end_line = self.hdr_char_end
                            else:
                                if self.do_unicode:
                                    start_line = self.u_hdr_char_sep
                                    end_line = self.u_hdr_char_sep
                                else:
                                    start_line = self.hdr_char_sep
                                    end_line = self.hdr_char_sep

                            # This is the line where we need to print the field
                            # text.
                            if i == central_line:
                                lines.append(start_line + str.center(field_text, (self.bits_per_line*2)-1) + end_line)
                                textline += 1
                            # This is a line we need to leave blank
                            else:
                                lines.append(start_line + (" " * ((self.bits_per_line*2)-1)) + end_line)
                            # If we just added the last line, add a horizontal separator
                            if i == lines_to_print-1:
                                if p == len(proto_fields) - 1:
                                    bottom = True
                                else:
                                    bottom = False
                                lines.append(
                                    self._get_horizontal(textline=textline, fields=proto_fields, bottom=bottom)
                                )
                        # increment field counter
                        fields_done+=1
                # Case 2: We are not at the beginning of the line and we need
                # to print something that does not fit in the current line
                else:
                    # This should never happen, since our _process_field_list()
                    # divides fields in chunks so we never have the case of
                    # something spanning lines in a weird manner
                    assert(False)

        result = "\n".join(lines)
        return result


class Main():
    """
    This class does all the boring task of a command-line application. It parses
    user input, displays usage, parses input files, etc.
    """

    def __init__(self):
        """
        Class constructor. Nothing fancy.
        """
        self.cmd_line_args = None             # Copy of the user argv
        self.protocols = []                   # List of protocols to print out
        self.bits_per_line = None             # Number of bits per line to print
        self.skip_numbers = None              # True to avoid printing bit units and tens
        self.hdr_char_start = None            # Character for start of the border line
        self.hdr_char_end = None              # Character for end of the border line
        self.hdr_char_fill_odd = None         # Fill character for border odd positions
        self.hdr_char_fill_even = None        # Fill character for border even positions
        self.hdr_char_sep = None              # Field separator character

        self.do_ascii = True                  # ASCII box characters
        self.do_unicode = False               # unicode box characters

    def display_help(self):
        """
        Displays command-line usage help to standard output.
        """
        print("")
        print("%s v%s" % (APPLICATION_NAME, APPLICATION_VERSION))
        print("Copyright (C) 2014-%i, %s (%s)." % (
            date.today().year, APPLICATION_AUTHOR, APPLICATION_AUTHOR_EMAIL)
        )
        print("This software comes with ABSOLUTELY NO WARRANTY.")
        print("")
        self.display_usage()
        print("PARAMETERS:")
        print(" <protocol>          : Name of an existing protocol")
        print(" <spec>              : Field by field specification of non-existing protocol")
        print("OPTIONS:")
        print(" -a, --ascii         : Use ASCII line characters (default)")
        print(" -b, --bits <n>      : Number of bits per line")
        print(" -f, --file          : Read specs from a text file")
        print(" -h, --help          : Displays this help information")
        print(" -n, --no-numbers    : Do not print bit numbers on top of the header")
        print(" -u, --unicode       : Use Unicode box characters")
        print(" -V, --version       : Displays current version")
        print(" --evenchar  <char>  : Character for the even positions of horizontal table borders")
        print(" --oddchar   <char>  : Character for the odd positions of horizontal table borders")
        print(" --startchar <char>  : Character that starts horizontal table borders")
        print(" --endchar   <char>  : Character that ends horizontal table borders")
        print(" --sepchar   <char>  : Character that separates protocol fields")

    def get_usage(self):
        """
        @return a string containing application usage information
        """
        return "Usage: %s {<protocol> or <spec>} [OPTIONS]" % self.cmd_line_args[0]

    def display_usage(self):
        """
        Prints usage information to standard output
        """
        print(self.get_usage())

    def parse_config_file(self, filename):
        """
        This method parses the supplied configuration file and adds any protocols to our
        list of protocols to print.
        @return The number of protocols parsed
        """

        i = 0
        # Read the contents of the whole file
        try:
            with open(filename) as f:
                lines = f.readlines()
                f.close()
        except (FileNotFoundError, PermissionError, OSError):
            print("Error while reading file %s. Please make sure it exists and it's readable." % filename)
            sys.exit(1)

        # Parse protocol specs, line by line
        for line in lines:
            # Sanitize the line
            line = line.strip()

            # If it starts with #, or is an empty line ignore it
            if line.startswith("#") or len(line) == 0:
                continue

            # If we have something else, treat it as a protocol spec
            proto = Protocol(line)
            self.protocols.append(proto)
            i += 1

        return i

    def parse_cmd_line_args(self, argv, is_config_file=False):
        """
        Parses command-line arguments and stores any relevant information
        internally
        """

        # Store a reference to command line args for later use.
        if is_config_file is False:
            self.cmd_line_args = argv

        # Check we have received enough command-line parameters
        if len(argv) == 1 and is_config_file is False:
            print(self.get_usage())
            sys.exit(1)
        else:
            skip_arg = False
            for i in range(1, len(argv)):

                # Useful for args like -c <filename>. This avoids parsing the
                # filename as it if was a command-line flag.
                if skip_arg is True:
                    skip_arg = False
                    continue

                # Spec file
                if argv[i] == "-f" or argv[i] == "--file":
                    # Make sure we have an actual parameter after the flag
                    if (i+1) >= len(argv):
                        return OP_FAILURE, "Expected parameter after %s\n%s" % (argv[i], self.get_usage())
                    skip_arg = True
                    # Parse the config file
                    protos = self.parse_config_file(argv[i+1])
                    if protos <= 0:
                        return OP_FAILURE, "No protocol specifications found in the supplied file (%s)" % argv[i+1]

                # Bits per line
                elif argv[i] == "-b" or argv[i] == "--bits":
                    # Make sure we have an actual parameter after the flag
                    if (i+1) >= len(argv):
                        return OP_FAILURE, "Expected parameter after %s\n%s" % (argv[i], self.get_usage())
                    skip_arg = True
                    # Parse the config file
                    try:
                        self.bits_per_line = int(argv[i+1])
                        if self.bits_per_line <= 0:
                            return OP_FAILURE, "Invalid number of bits per line supplied (%s)" % argv[i+1]
                    except:
                        return OP_FAILURE, "Invalid number of bits per line supplied (%s)" % argv[i+1]

                # Avoid displaying numbers on top of the header
                elif argv[i] == "-n" or argv[i] == "--no-numbers":
                    self.skip_numbers = True

                # Use ASCII line characters
                elif argv[i] == "-a" or argv[i] == "--ascii":
                    self.do_ascii = True
                    self.do_unicode = False

                # Use Unicode box characters
                elif argv[i] == "-u" or argv[i] == "--unicode":
                    self.do_ascii = False
                    self.do_unicode = True

                # Character variations
                elif argv[i] in ["--oddchar", "--evenchar", "--startchar", "--endchar", "--sepchar"]:
                    # Make sure we have an actual parameter after the flag
                    if (i+1) >= len(argv):
                        return OP_FAILURE, "Expected parameter after %s\n%s" % (argv[i], self.get_usage())
                    skip_arg = True

                    # Make sure we got a single character, not more
                    if len(argv[i+1]) != 1:
                        return OP_FAILURE, "A single character is expected after %s\n%s" % (argv[i], self.get_usage())

                    # Now let's store whatever character spec we got
                    if argv[i] == "--oddchar":
                        self.hdr_char_fill_odd = argv[i+1]
                    elif argv[i] == "--evenchar":
                        self.hdr_char_fill_even = argv[i+1]
                    elif argv[i] == "--startchar":
                        self.hdr_char_start = argv[i+1]
                    elif argv[i] == "--endchar":
                        self.hdr_char_end = argv[i+1]
                    elif argv[i] == "--sepchar":
                        self.hdr_char_sep = argv[i+1]

                # Display help
                elif argv[i] == "-h" or argv[i] == "--help":
                    self.display_help()
                    sys.exit(0)

                # Display version
                elif argv[i] == "-V" or argv[i] == "--version":
                    print("%s v%s" % (APPLICATION_NAME, APPLICATION_VERSION))
                    sys.exit(0)

                # Incorrect option supplied
                elif argv[i].startswith("-"):
                    print("ERROR: Invalid option supplied (%s)" % argv[i])
                    sys.exit(1)

                # Protocol name or protocol spec
                else:
                    # If it contains ":" characters, we have a protocol spec
                    if argv[i].count(":") > 0:
                        spec = argv[i]
                    # Otherwise, the user meant to display an existing protocol
                    else:
                        # If we got an exact match, end of story
                        if argv[i] in specs.protocols:
                            spec = specs.protocols[argv[i]]
                        # Otherwise, we may have received a partial match so
                        # we need to figure out which protocol the user meant.
                        # If the specification is ambiguous, we will error
                        else:
                            start_with_the_same = []
                            for spec in specs.protocols:
                                if spec.startswith(argv[i]):
                                    start_with_the_same.append(spec)
                            # If we only have one entry, it means we got some
                            # shortened version of the protocol name but no
                            # ambiguity. In that case, we will use the match.
                            if len(start_with_the_same) == 1:
                                spec = specs.protocols[start_with_the_same[0]]
                            elif len(start_with_the_same) == 0:
                                print("ERROR: supplied protocol '%s' does not exist." % argv[i])
                                sys.exit(1)
                            else:
                                print("Ambiguous protocol specifier '%s'. Did you mean any of these?" % argv[i])
                                for spec in start_with_the_same:
                                    print("  %s" % spec)
                                sys.exit(1)
                    # Finally, based on the spec, instance an actual protocol.
                    # Note that if the spec is incorrect, the Protocol() constructor
                    # will call sys.exit() itself, so there is no need to do
                    # error checking here.
                    try:
                        proto = Protocol(spec)
                        self.protocols.append(proto)
                    except ProtocolException as e:
                        print("ERROR: %s" % str(e))
                        sys.exit(1)

        if len(self.protocols) == 0:
            print("ERROR: Missing protocol")
            sys.exit(1)

        return OP_SUCCESS, None

    def run(self):
        """
        This is Protocol's 'core' method: parses command line argument and prints
        any necessary protocol to standard output
        """

        # Parse command-line arguments
        code, err = self.parse_cmd_line_args(sys.argv)
        if code != OP_SUCCESS:
            print("ERROR: %s" % err)
            sys.exit(1)

        # Print the appropriate protocol headers
        for i in range(0, len(self.protocols)):

            # Modify the properties of the object if the user passed any
            # options that require it
            if self.bits_per_line is not None:
                self.protocols[i].bits_per_line = self.bits_per_line
            if self.skip_numbers is not None:
                if self.skip_numbers is True:
                    self.protocols[i].do_print_top_tens = False
                    self.protocols[i].do_print_top_units = False
                else:
                    self.protocols[i].do_print_top_tens = True
                    self.protocols[i].do_print_top_units = True
            if self.do_unicode is True:
                self.protocols[i].do_unicode = True
                self.protocols[i].do_ascii = False

            # override ASCII default characters, can't override unicode characters
            if self.hdr_char_end is not None:
                self.protocols[i].hdr_char_end = self.hdr_char_end
            if self.hdr_char_start is not None:
                self.protocols[i].hdr_char_start = self.hdr_char_start
            if self.hdr_char_fill_even is not None:
                self.protocols[i].hdr_char_fill_even = self.hdr_char_fill_even
            if self.hdr_char_fill_odd is not None:
                self.protocols[i].hdr_char_fill_odd = self.hdr_char_fill_odd
            if self.hdr_char_sep is not None:
                self.protocols[i].hdr_char_sep = self.hdr_char_sep

            print(self.protocols[i])
            if len(self.protocols) > 1 and i != len(self.protocols)-1:
                print("")


# Main function
def main():
    """
    Main function. Runs the Protocol program.
    """

    # Instance our core class
    program = Main()

    # Do our magic
    program.run()


# THIS IS THE START OF THE EXECUTION
if __name__ == "__main__":
    main()
