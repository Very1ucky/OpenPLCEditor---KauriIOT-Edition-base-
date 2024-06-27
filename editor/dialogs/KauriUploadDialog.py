import threading
import serial.tools.list_ports
from kauri_parser import builder
import util.paths as paths

import wx
import wx.xrc

import time
import os
import platform
import json

# -------------------------------------------------------------------------------
#                            Kauri Upload Dialog
# -------------------------------------------------------------------------------

class KauriUploadDialog(wx.Dialog):
    """Dialog to configure upload parameters"""

    base_folder = paths.AbsParentDir(__file__)


    def __init__(self, parent, md5, resource_name, ticktime, build_path):
        """ 
        Constructor
        @param parent: Parent wx.Window of dialog for modal
        @param st_code: Compiled PLC program as ST code.
        """
        
        self.build_path = build_path
        self.ticktime = ticktime
        self.resource_name = resource_name
        
        self.md5 = md5
        self.last_update = 0
        self.update_subsystem = True
        current_dir = paths.AbsDir(__file__)
#
        if platform.system() == 'Windows':
            wx.Dialog.__init__ ( self, parent, id = wx.ID_ANY, title = u"Transfer Program to PLC", pos = wx.DefaultPosition, size = wx.Size( 793,453 ), style = wx.DEFAULT_DIALOG_STYLE )
        elif platform.system() == 'Linux':
            wx.Dialog.__init__ ( self, parent, id = wx.ID_ANY, title = u"Transfer Program to PLC", pos = wx.DefaultPosition, size = wx.Size( 820,590 ), style = wx.DEFAULT_DIALOG_STYLE )
        elif platform.system() == 'Darwin':
            wx.Dialog.__init__ ( self, parent, id = wx.ID_ANY, title = u"Transfer Program to PLC", pos = wx.DefaultPosition, size = wx.Size( 800,453 ), style = wx.DEFAULT_DIALOG_STYLE )
        
        # load Hals automatically and initialize the board_type_comboChoices
        self.loadHals()
        board_type_comboChoices = []
        '''
        for board in self.hals:
            board_name = ""
            if self.hals[board]['version'] == "0":
                board_name = board + ' [NOT INSTALLED]'
            else:
                board_name = board + ' [' + self.hals[board]['version'] + ']'

            board_type_comboChoices.append(board_name)
        '''
        for board in self.hals.keys():
            board_type_comboChoices.append(board)
            
            
        board_type_comboChoices.sort()
        

        self.SetSizeHints( minSize = wx.Size(-1, -1), maxSize = wx.Size(-1, -1), incSize = wx.DefaultSize )

        bSizer2 = wx.BoxSizer( wx.VERTICAL )

        self.m_listbook2 = wx.Listbook( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LB_LEFT )
        m_listbook2ImageSize = wx.Size( 100,100 )
        m_listbook2Index = 0
        m_listbook2Images = wx.ImageList( m_listbook2ImageSize.GetWidth(), m_listbook2ImageSize.GetHeight() )

        self.m_listbook2.AssignImageList( m_listbook2Images )
        self.m_panel5 = wx.Panel( self.m_listbook2, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
        bSizer21 = wx.BoxSizer( wx.VERTICAL )

        fgSizer1 = wx.FlexGridSizer( 0, 2, 0, 0 )
        fgSizer1.SetFlexibleDirection( wx.BOTH )
        fgSizer1.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )

        self.m_staticText1 = wx.StaticText( self.m_panel5, wx.ID_ANY, u"Board Type", wx.DefaultPosition, wx.Size( 80,-1 ), 0 )
        self.m_staticText1.Wrap( -1 )
        fgSizer1.Add( self.m_staticText1, 0, wx.ALIGN_CENTER|wx.BOTTOM|wx.LEFT|wx.TOP, 15 )

        self.board_type_combo = wx.ComboBox( self.m_panel5, wx.ID_ANY, u"Kauri PLC", wx.DefaultPosition, wx.Size( 410,-1 ), board_type_comboChoices, 0 )
        fgSizer1.Add( self.board_type_combo, 0, wx.ALIGN_CENTER|wx.BOTTOM|wx.TOP, 15 )
        self.board_type_combo.Bind(wx.EVT_COMBOBOX, self.onBoardChange)

        self.radio_serial = wx.RadioButton( self.m_panel5, wx.ID_ANY, u"Serial - RTU", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.radio_serial.Bind(wx.EVT_RADIOBUTTON, self.onUIChange)
        fgSizer1.Add( self.radio_serial, 0, wx.ALL, 5 )

        self.radio_ethernet = wx.RadioButton( self.m_panel5, wx.ID_ANY, u"Ethernet - TCP", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.radio_ethernet.Bind(wx.EVT_RADIOBUTTON, self.onUIChange)
        fgSizer1.Add( self.radio_ethernet, 0, wx.ALL, 5 )

        self.m_staticText2 = wx.StaticText( self.m_panel5, wx.ID_ANY, u"COM Port", wx.DefaultPosition, wx.Size( 80,-1 ), 0 )
        self.m_staticText2.Wrap( -1 )
        fgSizer1.Add( self.m_staticText2, 0, wx.ALIGN_CENTER|wx.ALIGN_TOP|wx.BOTTOM|wx.LEFT, 15 )

        self.com_port_combo = wx.ComboBox( self.m_panel5, wx.ID_ANY, u"COM1", wx.DefaultPosition, wx.Size( 410,-1 ), [""], 0 )
        self.reloadComboChoices(None) # Initialize the com port combo box
        fgSizer1.Add( self.com_port_combo, 0, wx.ALIGN_CENTER|wx.BOTTOM, 15 )
        self.com_port_combo.Bind(wx.EVT_COMBOBOX_DROPDOWN, self.reloadComboChoices)

        self.m_staticText2 = wx.StaticText( self.m_panel5, wx.ID_ANY, u"IP:port", wx.DefaultPosition, wx.Size( 80,-1 ), 0 )
        self.m_staticText2.Wrap( -1 )
        fgSizer1.Add( self.m_staticText2, 0, wx.ALIGN_CENTER|wx.ALIGN_TOP|wx.BOTTOM|wx.LEFT, 15 )
        
        self.ip_port_input = wx.TextCtrl( self.m_panel5, wx.ID_ANY, "192.168.001.000:502", wx.DefaultPosition, wx.Size( 410,-1 ), 0 )
        fgSizer1.Add( self.ip_port_input, wx.ALL, 5 )
        

        bSizer21.Add( fgSizer1, 1, wx.EXPAND, 5 )

        self.check_compile = wx.CheckBox( self.m_panel5, wx.ID_ANY, u"Compile Only", wx.DefaultPosition, wx.DefaultSize, 0 )
        bSizer21.Add( self.check_compile, 0, wx.LEFT, 15 )
        self.check_compile.Bind(wx.EVT_CHECKBOX, self.onUIChange)
        
        self.debug_after_transfer = wx.CheckBox( self.m_panel5, wx.ID_ANY, u"Debug after transfer", wx.DefaultPosition, wx.DefaultSize, 0 )
        bSizer21.Add( self.debug_after_transfer, 0, wx.LEFT, 15 )
        self.debug_after_transfer.Bind(wx.EVT_CHECKBOX, self.onUIChange)

        self.m_staticline2 = wx.StaticLine( self.m_panel5, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_HORIZONTAL )
        bSizer21.Add( self.m_staticline2, 0, wx.EXPAND |wx.ALL, 5 )

        self.m_staticText3 = wx.StaticText( self.m_panel5, wx.ID_ANY, u"Compilation output", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText3.Wrap( -1 )
        bSizer21.Add( self.m_staticText3, 0, wx.ALL, 5 )

        self.output_text = wx.TextCtrl( self.m_panel5, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.Size( -1, 150 ), wx.TE_MULTILINE|wx.TE_READONLY|wx.TE_WORDWRAP|wx.VSCROLL )
        self.output_text.SetFont( wx.Font( 10, 75, 90, 90, False, "Consolas" ) )
        self.output_text.SetBackgroundColour( wx.BLACK )
        self.output_text.SetForegroundColour( wx.WHITE )
        self.output_text.SetDefaultStyle(wx.TextAttr(wx.WHITE))
        #self.output_text.AppendText

        bSizer21.Add( self.output_text, 0, wx.ALL|wx.EXPAND, 5 )

        self.upload_button = wx.Button( self.m_panel5, wx.ID_ANY, u"Transfer to PLC", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.upload_button.SetMinSize( wx.Size( 150,30 ) )
        self.upload_button.Bind(wx.EVT_BUTTON, self.OnUpload)

        bSizer21.Add( self.upload_button, 0, wx.ALIGN_CENTER|wx.ALL, 5 )

        self.m_panel5.SetSizer( bSizer21 )
        self.m_panel5.Layout()
        bSizer21.Fit( self.m_panel5 )
        self.m_listbook2.AddPage( self.m_panel5, u"Transfer", True )
        m_listbook2Bitmap = wx.Bitmap(os.path.join(current_dir, "..", "images", "transfer_plc.png"), wx.BITMAP_TYPE_ANY )
        if ( m_listbook2Bitmap.IsOk() ):
            m_listbook2Images.Add( m_listbook2Bitmap )
            self.m_listbook2.SetPageImage( m_listbook2Index, m_listbook2Index )
            m_listbook2Index += 1

        self.m_panel6 = wx.Panel( self.m_listbook2, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
        bSizer3 = wx.BoxSizer( wx.VERTICAL )

        self.m_staticText9 = wx.StaticText( self.m_panel6, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText9.Wrap( -1 )
        self.m_staticText9.SetMinSize( wx.Size( -1,40 ) )

        bSizer3.Add( self.m_staticText9, 0, wx.ALL, 5 )

        gSizer1 = wx.GridSizer( 0, 2, 0, 0 )

        bSizer3.Add( gSizer1, 1, wx.EXPAND, 5 )


        self.m_panel6.SetSizer( bSizer3 )
        self.m_panel6.Layout()
        bSizer3.Fit( self.m_panel6 )

        self.m_panel7 = wx.Panel( self.m_listbook2, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
        bSizer4 = wx.BoxSizer( wx.VERTICAL )

        self.check_modbus_serial = wx.CheckBox( self.m_panel7, wx.ID_ANY, u"Enable Modbus RTU (Serial)", wx.DefaultPosition, wx.DefaultSize, 0 )
        bSizer4.Add( self.check_modbus_serial, 0, wx.ALL, 10 )
        self.check_modbus_serial.Bind(wx.EVT_CHECKBOX, self.onUIChange)

        fgSizer2 = wx.FlexGridSizer( 0, 4, 0, 0 )
        fgSizer2.SetFlexibleDirection( wx.BOTH )
        fgSizer2.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )

        self.m_staticText10 = wx.StaticText( self.m_panel7, wx.ID_ANY, u"Interface:", wx.DefaultPosition, wx.Size( -1,-1 ), 0 )
        self.m_staticText10.Wrap( -1 )
        self.m_staticText10.SetMinSize( wx.Size( 60,-1 ) )

        fgSizer2.Add( self.m_staticText10, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )

        serial_iface_comboChoices = [ u"Serial1", u"Serial2", u"Serial3" ]
        self.serial_iface_combo = wx.ComboBox( self.m_panel7, wx.ID_ANY, u"Serial", wx.DefaultPosition, wx.DefaultSize, serial_iface_comboChoices, wx.CB_READONLY )
        self.serial_iface_combo.SetSelection( 0 )
        self.serial_iface_combo.SetMinSize( wx.Size( 180,-1 ) )
        self.serial_iface_combo.Bind(wx.EVT_COMBOBOX, self.onUIChange)

        fgSizer2.Add( self.serial_iface_combo, 0, wx.ALL, 5 )

        self.m_staticText11 = wx.StaticText( self.m_panel7, wx.ID_ANY, u"Baud:", wx.DefaultPosition, wx.Size( -1,-1 ), 0 )
        self.m_staticText11.Wrap( -1 )
        self.m_staticText11.SetMinSize( wx.Size( 60,-1 ) )

        fgSizer2.Add( self.m_staticText11, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )

        baud_rate_comboChoices = [ u"9600", u"14400", u"19200", u"38400", u"57600", u"115200", u"256000"]
        self.baud_rate_combo = wx.ComboBox( self.m_panel7, wx.ID_ANY, u"115200", wx.DefaultPosition, wx.DefaultSize, baud_rate_comboChoices, wx.CB_READONLY )
        self.baud_rate_combo.SetSelection( 5 )
        self.baud_rate_combo.SetMinSize( wx.Size( 180,-1 ) )

        fgSizer2.Add( self.baud_rate_combo, 0, wx.ALL, 5 )

        self.m_staticText12 = wx.StaticText( self.m_panel7, wx.ID_ANY, u"Slave ID:", wx.DefaultPosition, wx.Size( -1,-1 ), 0 )
        self.m_staticText12.Wrap( -1 )
        self.m_staticText12.SetMinSize( wx.Size( 60,-1 ) )

        fgSizer2.Add( self.m_staticText12, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )

        self.slaveid_txt = wx.TextCtrl( self.m_panel7, wx.ID_ANY, u"0", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.slaveid_txt.SetMinSize( wx.Size( 180,-1 ) )

        fgSizer2.Add( self.slaveid_txt, 0, wx.ALL, 5 )

        self.serial_enable_programming = wx.CheckBox( self.m_panel7, wx.ID_ANY, u"Enable programming", wx.DefaultPosition, wx.DefaultSize, 0 )
        fgSizer2.Add( self.serial_enable_programming, 0, wx.ALL, 5 )
        
        self.serial_enable_debugging = wx.CheckBox( self.m_panel7, wx.ID_ANY, u"Enable debugging", wx.DefaultPosition, wx.DefaultSize, 0 )
        fgSizer2.Add( self.serial_enable_debugging, 0, wx.ALL, 5 )

        self.m_staticText23 = wx.StaticText( self.m_panel7, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText23.Wrap( -1 )
        self.m_staticText23.SetMaxSize( wx.Size( -1,15 ) )

        fgSizer2.Add( self.m_staticText23, 0, 0, 5 )


        bSizer4.Add( fgSizer2, 0, wx.EXPAND, 5 )

        self.m_staticline21 = wx.StaticLine( self.m_panel7, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_HORIZONTAL )
        bSizer4.Add( self.m_staticline21, 0, wx.ALL|wx.BOTTOM|wx.EXPAND|wx.TOP, 5 )

        self.enable_web_functions = wx.CheckBox( self.m_panel7, wx.ID_ANY, u"Enable network functions", wx.DefaultPosition, wx.DefaultSize, 0 )
        bSizer4.Add( self.enable_web_functions, 0, wx.ALL, 10 )
        self.enable_web_functions.Bind(wx.EVT_CHECKBOX, self.onUIChange)
        
        fgSizer3 = wx.FlexGridSizer( 0, 2, 0, 0 )
        fgSizer3.SetFlexibleDirection( wx.BOTH )
        fgSizer3.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )

        # self.m_staticText14 = wx.StaticText( self.m_panel7, wx.ID_ANY, u"Interface:", wx.DefaultPosition, wx.DefaultSize, 0 )
        # self.m_staticText14.Wrap( -1 )
        # self.m_staticText14.SetMinSize( wx.Size( 60,-1 ) )

        # fgSizer3.Add( self.m_staticText14, 0, wx.ALL, 5 )

        # tcp_iface_comboChoices = [ u"Ethernet", u"WiFi" ]
        # self.tcp_iface_combo = wx.ComboBox( self.m_panel7, wx.ID_ANY, u"Ethernet", wx.DefaultPosition, wx.DefaultSize, tcp_iface_comboChoices, wx.CB_READONLY )
        # self.tcp_iface_combo.SetSelection( 0 )
        # self.tcp_iface_combo.SetMinSize( wx.Size( 440,-1 ) )
        # self.tcp_iface_combo.Bind(wx.EVT_COMBOBOX, self.onUIChange)

        # fgSizer3.Add( self.tcp_iface_combo, 0, wx.ALL|wx.EXPAND, 5 )

        self.m_staticText15 = wx.StaticText( self.m_panel7, wx.ID_ANY, u"MAC:", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText15.Wrap( -1 )
        self.m_staticText15.SetMinSize( wx.Size( 60,-1 ) )

        fgSizer3.Add( self.m_staticText15, 0, wx.ALL, 5 )

        self.mac_txt = wx.TextCtrl( self.m_panel7, wx.ID_ANY, u"AA:AA:AA:AA:AA:AA", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.mac_txt.SetMinSize( wx.Size( 440,-1 ) )

        fgSizer3.Add( self.mac_txt, 0, wx.ALL|wx.EXPAND, 5 )


        bSizer4.Add( fgSizer3, 0, wx.EXPAND, 5 )

        fgSizer35 = wx.FlexGridSizer( 0, 4, 0, 0 )
        fgSizer35.SetFlexibleDirection( wx.BOTH )
        fgSizer35.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
        
        self.use_dhcp = wx.CheckBox( self.m_panel7, wx.ID_ANY, u"Using DHCP server", wx.DefaultPosition, wx.DefaultSize, 0 )
        fgSizer35.Add( self.use_dhcp, 0, wx.ALL, 5 )
        self.use_dhcp.Bind(wx.EVT_CHECKBOX, self.onUIChange)
        
        bSizer4.Add( fgSizer35, 0, wx.EXPAND, 5 )

        fgSizer4 = wx.FlexGridSizer( 0, 4, 0, 0 )
        fgSizer4.SetFlexibleDirection( wx.BOTH )
        fgSizer4.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )

        self.m_staticText17 = wx.StaticText( self.m_panel7, wx.ID_ANY, u"IP:", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText17.Wrap( -1 )
        self.m_staticText17.SetMinSize( wx.Size( 60,-1 ) )

        fgSizer4.Add( self.m_staticText17, 0, wx.ALL, 5 )

        self.ip_txt = wx.TextCtrl( self.m_panel7, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
        self.ip_txt.SetMinSize( wx.Size( 180,-1 ) )

        fgSizer4.Add( self.ip_txt, 0, wx.ALL, 5 )

        self.m_staticText19 = wx.StaticText( self.m_panel7, wx.ID_ANY, u"Gateway:", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText19.Wrap( -1 )
        self.m_staticText19.SetMinSize( wx.Size( 60,-1 ) )

        fgSizer4.Add( self.m_staticText19, 0, wx.ALL, 5 )

        self.gateway_txt = wx.TextCtrl( self.m_panel7, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
        self.gateway_txt.SetMinSize( wx.Size( 180,-1 ) )

        fgSizer4.Add( self.gateway_txt, 0, wx.ALL, 5 )

        self.m_staticText20 = wx.StaticText( self.m_panel7, wx.ID_ANY, u"Subnet:", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText20.Wrap( -1 )
        self.m_staticText20.SetMinSize( wx.Size( 60,-1 ) )

        fgSizer4.Add( self.m_staticText20, 0, wx.ALL, 5 )

        self.subnet_txt = wx.TextCtrl( self.m_panel7, wx.ID_ANY, u"255.255.255.0", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.subnet_txt.SetMinSize( wx.Size( 180,-1 ) )

        fgSizer4.Add( self.subnet_txt, 0, wx.ALL, 5 )

        # self.m_staticText21 = wx.StaticText( self.m_panel7, wx.ID_ANY, u"Wi-Fi SSID:", wx.DefaultPosition, wx.DefaultSize, 0 )
        # self.m_staticText21.Wrap( -1 )
        # self.m_staticText21.SetMinSize( wx.Size( 60,-1 ) )

        # fgSizer4.Add( self.m_staticText21, 0, wx.ALL, 5 )
        
        

        # self.wifi_ssid_txt = wx.TextCtrl( self.m_panel7, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
        # self.wifi_ssid_txt.SetMinSize( wx.Size( 180,-1 ) )

        # fgSizer4.Add( self.wifi_ssid_txt, 0, wx.ALL, 5 )

        # self.m_staticText22 = wx.StaticText( self.m_panel7, wx.ID_ANY, u"Password:", wx.DefaultPosition, wx.DefaultSize, 0 )
        # self.m_staticText22.Wrap( -1 )
        # self.m_staticText22.SetMinSize( wx.Size( 60,-1 ) )

        # fgSizer4.Add( self.m_staticText22, 0, wx.ALL, 5 )

        # self.wifi_pwd_txt = wx.TextCtrl( self.m_panel7, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.TE_PASSWORD )
        # self.wifi_pwd_txt.SetMinSize( wx.Size( 180,-1 ) )

        # fgSizer4.Add( self.wifi_pwd_txt, 0, wx.ALL, 5 )

        self.m_staticText24 = wx.StaticText( self.m_panel7, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText24.Wrap( -1 )
        fgSizer4.Add( self.m_staticText24, 0, wx.ALL, 5 )
        
        bSizer4.Add( fgSizer4, 1, wx.EXPAND, 5 )
        
        self.check_modbus_tcp = wx.CheckBox( self.m_panel7, wx.ID_ANY, u"Enable Modbus TCP", wx.DefaultPosition, wx.DefaultSize, 0 )
        bSizer4.Add( self.check_modbus_tcp, 0, wx.ALL, 10 )
        self.check_modbus_tcp.Bind(wx.EVT_CHECKBOX, self.onUIChange)
        
        fgSizer5 = wx.FlexGridSizer( 0, 4, 0, 0 )
        fgSizer5.SetFlexibleDirection( wx.BOTH )
        fgSizer5.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
        
        self.eth_enable_programming = wx.CheckBox( self.m_panel7, wx.ID_ANY, u"Enable programming", wx.DefaultPosition, wx.DefaultSize, 0 )
        fgSizer5.Add( self.eth_enable_programming, 0, wx.ALL, 5 )
        
        self.eth_enable_debugging = wx.CheckBox( self.m_panel7, wx.ID_ANY, u"Enable debugging", wx.DefaultPosition, wx.DefaultSize, 0 )
        fgSizer5.Add( self.eth_enable_debugging, 0, wx.ALL, 5 )
        bSizer4.Add( fgSizer5, 1, wx.EXPAND, 5 )

        

        gSizer2 = wx.GridSizer( 0, 2, 0, 0 )

        #self.m_button4 = wx.Button( self.m_panel7, wx.ID_ANY, u"Restore Defaults", wx.DefaultPosition, wx.DefaultSize, 0 )
        #self.m_button4.SetMinSize( wx.Size( 150,30 ) )

        #gSizer2.Add( self.m_button4, 0, wx.ALIGN_CENTER|wx.ALL, 5 )

        #self.m_button5 = wx.Button( self.m_panel7, wx.ID_ANY, u"Save Changes", wx.DefaultPosition, wx.DefaultSize, 0 )
        #self.m_button5.SetMinSize( wx.Size( 150,30 ) )

        #gSizer2.Add( self.m_button5, 0, wx.ALIGN_CENTER|wx.ALL, 5 )


        #bSizer4.Add( gSizer2, 1, wx.EXPAND, 5 )


        self.m_panel7.SetSizer( bSizer4 )
        self.m_panel7.Layout()
        bSizer4.Fit( self.m_panel7 )
        self.m_listbook2.AddPage( self.m_panel7, u"Communications", False )
        m_listbook2Bitmap = wx.Bitmap( os.path.join(current_dir, "..", "images", "comm.png"), wx.BITMAP_TYPE_ANY )
        if ( m_listbook2Bitmap.IsOk() ):
            m_listbook2Images.Add( m_listbook2Bitmap )
            self.m_listbook2.SetPageImage( m_listbook2Index, m_listbook2Index )
            m_listbook2Index += 1


        bSizer2.Add( self.m_listbook2, 1, wx.EXPAND |wx.ALL, 0 )


        self.SetSizer( bSizer2 )
        self.Layout()

        self.Centre( wx.BOTH )

        self.loadSettings()
        self.onUIChange()

    def __del__( self ):
        pass

    def reloadComboChoices(self, event):
         self.com_port_combo.Clear()
         self.com_port_combo_choices = {comport.description:comport.device for comport in serial.tools.list_ports.comports()}
         self.com_port_combo.SetItems(list(self.com_port_combo_choices.keys()))

    def onBoardChange(self, e):
        # Update board specified data
        sel_board = self.board_type_combo.GetValue()
        ser_ports_count = self.hals[sel_board]["serials_count"]
        serial_ints_list = []
        for serial_int_pos in range(ser_ports_count):
            serial_ints_list.append(f"Serial{serial_int_pos+1}")
        self.serial_iface_combo.Clear()
        self.serial_iface_combo.AppendItems(serial_ints_list)
        self.serial_iface_combo.SetSelection(0)
        
        self.check_modbus_serial.Enable(self.hals[sel_board]["is_mb_serial_en"])
        self.check_modbus_tcp.Enable(self.hals[sel_board]["is_mb_tcp_en"])


    def onUIChange(self, e=None):
        
        # Update Comms
        if (self.check_modbus_serial.GetValue() is False):
            self.serial_iface_combo.Enable(False)
            self.baud_rate_combo.Enable(False)
            self.slaveid_txt.Enable(False)
            self.serial_enable_programming.Enable(False)
            self.serial_enable_debugging.Enable(False)
        elif (self.check_modbus_serial.GetValue() is True):
            self.serial_iface_combo.Enable(True)
            if self.serial_iface_combo.GetValue() == u"Serial1":
                self.baud_rate_combo.Enable(False)
                self.slaveid_txt.Enable(False)
                self.serial_enable_programming.Enable(False)
                self.serial_enable_programming.SetValue(True)
                self.baud_rate_combo.SetValue(u"115200")
                self.slaveid_txt.SetLabelText(u"1")
            else:
                self.baud_rate_combo.Enable(True)
                self.slaveid_txt.Enable(True)
                self.serial_enable_programming.Enable(True)
            self.serial_enable_debugging.Enable(True)

        if (self.check_compile.GetValue() is False):
            self.debug_after_transfer.Enable(True)
            
            self.radio_ethernet.Enable(True)
            self.radio_serial.Enable(True)
            if self.debug_after_transfer.GetValue() is True:
                self.upload_button.SetLabel("Transfer to PLC and debug")
            else:
                self.upload_button.SetLabel("Transfer to PLC")
        elif (self.check_compile.GetValue() is True):
            self.debug_after_transfer.Enable(False)
            self.debug_after_transfer.SetValue(False)
            
            self.radio_ethernet.Enable(False)
            self.radio_serial.Enable(False)
            
            self.upload_button.SetLabel("Compile")
        if (self.enable_web_functions.GetValue() is False):
            self.mac_txt.Enable(False)
            self.use_dhcp.Enable(False)
            self.ip_txt.Enable(False)
            self.gateway_txt.Enable(False)
            self.subnet_txt.Enable(False)
            self.check_modbus_tcp.Enable(False)
            self.check_modbus_tcp.SetValue(False)
        elif (self.enable_web_functions.GetValue() is True):
            self.mac_txt.Enable(True)
            self.use_dhcp.Enable(True)
            if (self.use_dhcp.GetValue() is True):
                self.ip_txt.Enable(False)
                self.gateway_txt.Enable(False)
                self.subnet_txt.Enable(False)
            else:
                self.ip_txt.Enable(True)
                self.gateway_txt.Enable(True)
                self.subnet_txt.Enable(True)
            self.check_modbus_tcp.Enable(True)
                
        if (self.check_modbus_tcp.GetValue() is False):
            self.eth_enable_programming.Enable(False)
            self.eth_enable_debugging.Enable(False)
        elif (self.check_modbus_tcp.GetValue() is True):
            self.eth_enable_programming.Enable(True)
            self.eth_enable_debugging.Enable(True)
            
        # Update radio button fields access
        if (self.radio_serial.GetValue() is True):
            self.com_port_combo.Enable(self.radio_serial.Enabled)
            self.ip_port_input.Enable(False)
        elif (self.radio_ethernet.GetValue() is True):
            self.com_port_combo.Enable(False)
            self.ip_port_input.Enable(self.radio_ethernet.Enabled)
        else:
            self.com_port_combo.Enable(False)
            self.ip_port_input.Enable(False)
        

    def startBuilder(self):

        # Get platform and source_file from hals
        board_type = self.board_type_combo.GetValue()
        
        defs = self.generateDefinitionsFile()

        if self.com_port_combo.Enabled and self.com_port_combo.GetValue() in self.com_port_combo_choices:
            transfer_data = self.com_port_combo_choices[self.com_port_combo.GetValue()]
        elif self.ip_port_input.Enabled:
            transfer_data = self.ip_port_input.GetValue()
        else:
            transfer_data = None
        
        plc_builder = builder.PlcProgramBuilder()
        compiler_thread = threading.Thread(target=plc_builder.build, args=(board_type, defs, self.resource_name, self.build_path, self.radio_serial.GetValue() and not self.radio_ethernet.GetValue(), transfer_data, self.output_text))
        compiler_thread.start()
        compiler_thread.join()
        wx.CallAfter(self.upload_button.Enable, True)   
        if (self.update_subsystem):
            self.update_subsystem = False
            self.last_update = time.time()
        self.saveSettings()
        
        if self.debug_after_transfer.GetValue() and plc_builder.build_failed is False:
            self.EndModal(2)

    def OnUpload(self, event):
        self.upload_button.Enable(False)
        builder_thread = threading.Thread(target=self.startBuilder)
        builder_thread.start()
    
    def generateDefinitionsFile(self) -> dict:
        
        defs_dict = {"MD5": self.md5, 
                     "MODBUS_SERIAL": {"ENABLED": self.check_modbus_serial.GetValue(),
                                       "INTERFACE": str(self.serial_iface_combo.GetValue()[-1]),
                                       "BAUD_RATE": str(self.baud_rate_combo.GetValue()),
                                       "SLAVE_ID": str(self.slaveid_txt.GetValue()),
                                       "IS_PROG_EN": self.serial_enable_programming.GetValue(),
                                       "IS_DEB_EN": self.serial_enable_debugging.GetValue()},
                     "NET_FEATURES": {"ENABLED": self.enable_web_functions.GetValue(),
                                      "MAC": str(self.mac_txt.GetValue()).split(":"),
                                      "EN_DHCP": self.use_dhcp.GetValue(),
                                      "IP": str(self.ip_txt.GetValue()).split("."),
                                      "GATEWAY": str(self.gateway_txt.GetValue()).split("."),
                                      "SUBNET": str(self.subnet_txt.GetValue()).split("."),},
                     "MODBUS_TCP": {"ENABLED": self.check_modbus_tcp.GetValue(),
                                    "IS_PROG_EN": self.eth_enable_programming.GetValue(),
                                    "IS_DEB_EN": self.eth_enable_debugging.GetValue()},
                     "TICKTIME": self.ticktime}
        
        return defs_dict

    def saveSettings(self):
        settings = {}
        settings['board_type'] = self.board_type_combo.GetValue()
        settings['serial_transfer_en'] = self.radio_serial.GetValue()
        settings['com_port'] = self.com_port_combo.GetValue()
        settings['ip_port'] = self.ip_port_input.GetValue()
        settings['mb_serial'] = self.check_modbus_serial.GetValue()
        settings['serial_iface'] = self.serial_iface_combo.GetValue()
        settings['baud'] = self.baud_rate_combo.GetValue()
        settings['slaveid'] = self.slaveid_txt.GetValue()
        settings['serial_mb_prog_en'] = self.serial_enable_programming.GetValue()
        settings['serial_mb_deb_en'] = self.serial_enable_debugging.GetValue()
        settings['en_net'] = self.enable_web_functions.GetValue()
        settings['en_dhcp'] = self.use_dhcp.GetValue()
        settings['mb_tcp'] = self.check_modbus_tcp.GetValue()
        settings['mac'] = self.mac_txt.GetValue()
        settings['ip'] = self.ip_txt.GetValue()
        settings['gateway'] = self.gateway_txt.GetValue()
        settings['subnet'] = self.subnet_txt.GetValue()
        settings['tcp_mb_prog_en'] = self.eth_enable_programming.GetValue()
        settings['tcp_mb_deb_en'] = self.eth_enable_debugging.GetValue()
        settings['last_update'] = self.last_update
        

        #write settings to disk
        jsonStr = json.dumps(settings)
        f = open(os.path.join(self.base_folder, "kauri_parser", 'settings.json'), 'w')
        f.write(jsonStr)
        f.flush()
        f.close()


    def loadSettings(self):
        #read settings from disk
        if (os.path.exists(os.path.join(self.base_folder, "kauri_parser", 'settings.json'))):
            f = open(os.path.join(self.base_folder, "kauri_parser", 'settings.json'), 'r')
            jsonStr = f.read()
            f.close()

            settings = json.loads(jsonStr)

            #Check if should update subsystem
            if ('last_update' in settings.keys()):
                self.last_update = settings['last_update']
                if (time.time() - float(self.last_update) > 604800.0): #604800 is the number of seconds in a week (7 days)
                    self.update_subsystem = True
                    self.last_update = time.time()
                else:
                    self.update_subsystem = False
            else:
                self.update_subsystem = True
                self.last_update = time.time()

            wx.CallAfter(self.board_type_combo.SetValue, settings['board_type'])
            wx.CallAfter(self.com_port_combo.SetValue, settings['com_port'])
            wx.CallAfter(self.ip_port_input.SetValue, settings['ip_port'])
            wx.CallAfter(self.radio_serial.SetValue, settings['serial_transfer_en'])
            wx.CallAfter(self.radio_ethernet.SetValue, not settings['serial_transfer_en'])
            wx.CallAfter(self.check_modbus_serial.SetValue, settings['mb_serial'])
            wx.CallAfter(self.serial_iface_combo.SetValue, settings['serial_iface'])
            wx.CallAfter(self.baud_rate_combo.SetValue, settings['baud'])
            wx.CallAfter(self.slaveid_txt.SetValue, settings['slaveid'])
            wx.CallAfter(self.serial_enable_programming.SetValue, settings['serial_mb_prog_en'])
            wx.CallAfter(self.serial_enable_debugging.SetValue, settings['serial_mb_deb_en'])
            wx.CallAfter(self.enable_web_functions.SetValue, settings['en_net'])
            wx.CallAfter(self.use_dhcp.SetValue, settings['en_dhcp'])
            wx.CallAfter(self.check_modbus_tcp.SetValue, settings['mb_tcp'])
            wx.CallAfter(self.mac_txt.SetValue, settings['mac'])
            wx.CallAfter(self.ip_txt.SetValue, settings['ip'])
            wx.CallAfter(self.gateway_txt.SetValue, settings['gateway'])
            wx.CallAfter(self.subnet_txt.SetValue, settings['subnet'])
            wx.CallAfter(self.eth_enable_programming.SetValue, settings['tcp_mb_prog_en'])
            wx.CallAfter(self.eth_enable_debugging.SetValue, settings['tcp_mb_deb_en'])

            wx.CallAfter(self.onUIChange, None)
            
            sel_board = self.board_type_combo.GetValue()
            if sel_board in self.hals.keys():
                self.check_modbus_serial.Enable(self.hals[sel_board]["is_mb_serial_en"])
                self.check_modbus_tcp.Enable(self.hals[sel_board]["is_mb_tcp_en"])
        else:
            settings = {}
            settings['board_type'] = ""
            settings['com_port'] = ""
            settings['serial_transfer_en'] = True
            settings['ip_port'] = "192.168.001.000:502"
            settings['mb_serial'] = False
            settings['serial_iface'] = ""
            settings['baud'] = ""
            settings['slaveid'] = ""
            settings['serial_mb_prog_en'] = False
            settings['serial_mb_deb_en'] = False
            settings['en_net'] = False
            settings['en_dhcp'] = False
            settings['mb_tcp'] = False
            settings['tcp_iface'] = ""
            settings['mac'] = "AA:AA:AA:AA:AA:AA"
            settings['ip'] = "000.000.000.000"
            settings['gateway'] = "000.000.000.000"
            settings['subnet'] = "000.000.000.000"
            settings['tcp_mb_prog_en'] = False
            settings['tcp_mb_deb_en'] = False
            settings['last_update'] = self.last_update
            

            #write settings to disk
            jsonStr = json.dumps(settings)

            f = open(os.path.join(self.base_folder, "kauri_parser", 'settings.json'), 'w')
            f.write(jsonStr)
            f.flush()
            f.close()
            self.loadSettings()
    
    def loadHals(self):
        # load hals list from json file, or construct it
        
        f = open(os.path.join(self.base_folder, "kauri_parser", 'hals.json'), 'r')
        jsonStr = f.read()
        f.close()
        self.hals = json.loads(jsonStr)
        
            

    def saveHals(self):
        jsonStr = json.dumps(self.hals)

        f = open(os.path.join(self.base_folder, "kauri_parser", 'hals.json'), 'w')
        f.write(jsonStr)
        f.flush()
        f.close()