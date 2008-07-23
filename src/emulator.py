#!/usr/bin/env python

import struct, sys, os, time, thread, math, random
import ConfigParser, os
from socket import *
import pygame
from pygame.locals import *

CONFIGFILE = 'emulator.ini'

IS_PORT = 12470
CS_PORT = 12489

class udp_simulator:

    def __init__(self):
        self.stopping = 0
        self.quitting = 0
        self.ctrl = 0.0
        self.x = 0
        self.options = []
        self.read_config()
    
    def read_config(self):
        config = ConfigParser.ConfigParser()
        if not config.read(CONFIGFILE):
            print "%s not found, quitting." % CONFIGFILE
            sys.exit(1)
        sections = config.sections()
        self.options = []
        for section in sections:
            if not config.has_option(section, 'feedback'):
                continue
            conf = Config(section)
            conf.fb = config.get(section, 'feedback')
            if config.has_option(section, 'initmsg'):
                conf.initmsg = config.get(section, 'initmsg')
            if config.has_option(section, 'host'):
                conf.host = config.get(section, 'host')
            self.options.append(conf)
        return self.options
    
    def start(self, config):
        self.start_time = time.time()
        self.stopping = 0
        thread.start_new_thread(self.bci_loop, (config, ))

    def start2(self, config):
        self.start_time = time.time()
        self.stopping = 0
        self.bci_loop2(config)
    
    def stop(self):
        self.stopping = 1

        
    def encode_packet(self,value):
        self.ctrl += 1.0
        
        packet = struct.pack('=3i',
        0xb411510, #magic
        len(value), #m
        1)
        
        for d in value:
            packet = packet + struct.pack('=d', d)
        
        return packet
        
        
    def strToList(self, str):
        list = []
        for s in str:
            
            list.append(float(ord(s)))
            
        return list
    
    
    def sendMessage(self, msg):
        packet = self.encode_packet(self.strToList("%s; timecheck=%f;" % (msg, 0.01+time.time()-self.start_time)))
        self.ctrlsocket.sendto(packet, (self.host, IS_PORT))
        
    
    def bci_loop(self, config):
        sendsocket = socket(AF_INET,SOCK_DGRAM)
        ctrlsocket = socket(AF_INET,SOCK_DGRAM)
        self.host = config.host
        self.ctrlsocket = ctrlsocket
        
        print "Starting %s" % config.name
        
        
        self.sendMessage("type = '%s';loop = false; %s; " % (config.fb, config.initmsg))
        time.sleep(1)
        
        print "Playing"
        self.sendMessage("feedback_opt.status='play';")
        try:
            c = 0
            while not self.stopping:
                sample1 = abs(math.sin(c/50.0))
                sample2 = abs(math.sin(c/90.0))
                sample3 = abs(math.sin(c/100.0))
                
                c = c + 1
                
                pkt = self.encode_packet([0, self.ctrl, (time.time()-self.start_time)*1000.0, 0.0, sample1, sample2, sample3])
                sendsocket.sendto(pkt, (config.host, CS_PORT))    
                time.sleep(0.04)
            
            self.sendMessage("run=false; loop=false;")
        finally:
            sendsocket.close()
            ctrlsocket.close()


    def bci_loop2(self, config):
        ctrlsocket = socket(AF_INET,SOCK_DGRAM)
        self.host = config.host
        self.ctrlsocket = ctrlsocket
        
        print "Starting %s" % config.name
        
        self.sendMessage("type = '%s';loop = false; %s; " % (config.fb, config.initmsg))
        time.sleep(1)
        
        ctrlsocket.close()


class Config(object):
    
    def __init__(self, name):
        self.name = name
        self.fb = ""
        self.initmsg = ""
        self.host = "127.0.0.1"


class Interpreter(object):
    
    def __init__(self):
        self.simulator = udp_simulator()
        self.COMMANDS = {
            #Command        method, helpstring, parameter
            'help'      : (self.cmd_help, "Show this help.", None),
            'reload'    : (self.cmd_reload, "Reload the configuration file %s." % CONFIGFILE, None),
            'ls'        : (self.cmd_ls, "List the available configurations.", None),
            'load'      : (self.cmd_load, "Load the configuration and start the feedback.", 'CONFIG'),
            'load2'     : (self.cmd_load2, "Load the configuration and start the feedback (without control signal).", 'CONFIG'),
            'pause'     : (self.cmd_pause, "Pause/Unpause the feedback.", None),
            'stop'      : (self.cmd_stop, 'Stop the feedback.', None),
            'quit'      : (self.cmd_quit, 'Quit the emulator.', None),
            'send'      : (self.cmd_send, 'Send MESSAGE to the feedback.', 'MESSAGE')
            }
        self.GREETING = '''Welcome to the BCI emulator, type "help" to see a list of available commands and their meanings.'''

    def main_loop(self):
        print self.GREETING
        while not self.simulator.quitting:
            print ">",
            cmd = raw_input().strip().split(' ', 1)
        
            if cmd[0] in self.COMMANDS:
                if self.COMMANDS.get(cmd[0])[2]:
                    self.COMMANDS.get(cmd[0])[0](cmd[1])
                else:
                    self.COMMANDS.get(cmd[0])[0]()
            else:
                print "Command not found."
            time.sleep(0.1)
        

    def cmd_help(self):
        print "Available commands:"
        for i in self.COMMANDS:
            syntax = i
            if self.COMMANDS.get(i)[2]:
                syntax = syntax +' '+ self.COMMANDS.get(i)[2]
            print "  %-15s %s" % (syntax, self.COMMANDS.get(i)[1])
            
    def cmd_reload(self):
        print "Reloading configuration."
        self.simulator.read_config()
    
    def cmd_ls(self):
        print "Available configurations:"
        for i in self.simulator.options:
            print "Name .........", i.name
            print "  Feedback ...", i.fb
            print "  Host .......", i.host
            print "  Msg ........", i.initmsg
    
    def cmd_load(self, cmd):
        for i in self.simulator.options:
            if i.name == cmd:
                self.simulator.start(i)
                return
        print "Configuration %s not found." % cmd

    def cmd_load2(self, cmd):
        for i in self.simulator.options:
            if i.name == cmd:
                self.simulator.start2(i)
                return
        print "Configuration %s not found." % cmd
    
    def cmd_pause(self):
        self.simulator.sendMessage("feedback_opt.status='pause';")
    
    def cmd_stop(self):
        print "Stopping the main loop."
        self.simulator.stopping = 1
    
    def cmd_quit(self):
        print "Quitting the emulator."
        self.simulator.quitting = 1
        
    def cmd_send(self, cmd):
        self.simulator.sendMessage(cmd)


if __name__ == "__main__":
    interpreter = Interpreter()
    interpreter.main_loop()
