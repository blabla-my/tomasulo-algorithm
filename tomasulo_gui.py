# -*- coding: utf-8 -*-
from tomasulo import *
from tomasulo import _exec
from tomasulo import _write_back
from tkinter import *
from time import sleep
from threading import *

class tomasulo_gui():
    def __init__(self):
        self.window = Tk()
        self.time = 0
        self.nextout = 0
        self.end_sum = 0
        self.read_done = False
        self.exec_thread_on = False
    def window_init(self):
        self.window.title("tomasulo算法模拟")
        self.window.geometry("900x1000+100+100")
        
        #button
        self.read_file_button = Button(self.window, text = '读取',bg='lightgreen',width = 10,command = self.file_read)
        self.read_file_button.grid(row = 1,column = 1,columnspan = 2)
        self.save = Button(self.window, text = '保存', bg = 'lightgreen', width = 10,command = self.click_to_save)
        self.save.grid(row = 2,column = 1, columnspan = 2)
        self.options = Button(self.window, text = '设置', bg = 'lightgreen',width = 10,command = self.optionnal)
        self.options.grid(row=3,column = 1, columnspan = 2)
        self.run = Button(self.window, text = '运行', bg = 'lightgreen' , width=10,command = self.thread_exec_one_sec_step)
        self.run.grid(row = 4,column = 1, columnspan = 2)
        self.one_step = Button(self.window, text = '单步', bg = 'lightgreen', width = 10,command = self.exec_one_step)
        self.one_step.grid(row = 5,column = 1, columnspan = 2)
        self.remake = Button(self.window, text = '重置', bg = 'lightgreen',width = 10,command = self.system_remake)
        self.remake.grid(row = 6,column = 1, columnspan = 2)

        #text
        self.file_read_url = Entry(self.window,width = 50,textvariable = StringVar())
        self.file_read_url.grid(row = 1,column = 2,columnspan = 2, sticky = W, padx = 10)
        self.file_save_url = Entry(self.window,width = 50)
        self.file_save_url.grid(row = 2, column = 2,columnspan = 2, sticky = W, padx = 10)
        self.RS_info = Text(self.window, width = 60, height=40)
        self.RS_info.grid(row = 9,column = 1, rowspan = 2, columnspan = 2, sticky = W, padx = 10)
        self.ins_info = Text(self.window,width = 60, height = 40)
        self.ins_info.grid(row = 9, column = 3, rowspan = 2, columnspan = 2, sticky = E, padx = 10)
        self.Qi_info = Text(self.window, width = 100, height = 4)
        self.Qi_info.grid(row = 12, column = 1, rowspan = 2, columnspan = 5, sticky = W, padx = 10)

        #label
        #self.current_time_label= Label(self.window,text = '当前时钟周期:')
        #self.current_time_label.grid(row = 7,column = 1,columnspan = 1,sticky = W, padx = 20,pady = 10)
        self.RS_info_label = Label(self.window,text = '保留站状态表',)
        self.RS_info_label.grid(row = 8,column = 1,columnspan = 2,sticky = W,padx=20)
        self.ins_info_label = Label(self.window, text = '指令状态表')
        self.ins_info_label.grid(row = 8,column = 3,columnspan = 2,sticky = W,padx=20)
        self.Qi_label = Label(self.window, text = '寄存器状态表')
        self.Qi_label.grid(row = 11,column = 1,sticky = W,padx = 20)
    def _start(self):
        self.window.mainloop()

    def ins_prt(self):
        if self.read_done:
            self.ins_info.delete(1.0,END)
            ins = self.ins
            time = self.time
            self.ins_info.insert(END,'\n------------------------------------------------------------\n\n')
            self.ins_info.insert(END,"seq\tOP\tcontent\t\tout\tbegin\tend\twbck\n")
            for i in range(len(ins)):
                if(ins != ''):
                    self.ins_info.insert(END,'------------------------------------------------------------\n')
                    self.ins_info.insert(END,str(i+1)+'\t')
                    self.ins_info.insert(END,ins[i].OP+'\t')
                    if ins[i].OP == 'L.D':
                        self.ins_info.insert(END,"{},{}({})\t\t".format(ins[i].des,ins[i].Imm,ins[i].rs))
                    else:
                        self.ins_info.insert(END,"{},{},{}\t\t".format(ins[i].des,ins[i].rs,ins[i].rt))
                    self.ins_info.insert(END,str(int(ins[i].out))+'\t')
                    self.ins_info.insert(END,str(int(ins[i].exec_start <= time))+'\t')
                    self.ins_info.insert(END,str(int(ins[i].exec_end <= time))+'\t')
                    self.ins_info.insert(END,str(int(ins[i].write_back <= time))+'\n')
            self.ins_info.insert(END,'\n')
    
    def RS_prt(self):
        if self.read_done:
            self.RS_info.delete(1.0,END)
            self.RS_info.insert(END,"当前时钟周期：{}\n\n".format(self.time))
            self.RS_info.insert(END,'------------------------------------------------------------\n')
            self.RS_info.insert(END,"RSname\tOP\tBusy\tVj\tVk\tQj\tQk\tA\n")
            for r in self.rss[1:]:
                self.RS_info.insert(END,'------------------------------------------------------------\n')
                content_line = "{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\n".format(r.Name,r.OP,true(r.busy),r.Vj,r.Vk,r.Qj,r.Qk,r.A)
                self.RS_info.insert(END,content_line)
                
            self.RS_info.insert(END,'------------------------------------------------------------\n')

    def Qi_prt(self):
        if self.read_done:
            self.Qi_info.delete(1.0,END)
            self.Qi_info.insert(END,"-----------------------------------------------------------------\nRegs\t")
            for k in Qi.keys():
                self.Qi_info.insert(END,k+'\t')
            self.Qi_info.insert(END,"\nQi\t")
            for k in Qi.keys():
                self.Qi_info.insert(END,str(Qi[k])+'\t')
            self.Qi_info.insert(END,'\n-----------------------------------------------------------------------')

    def file_read(self):
        url = self.file_read_url.get()
        print(url)
        if url == '':
            url = 'codes.txt'
        self.ins = get_ins(url)
        if self.ins != '':
            self.ins_info.delete(1.0,END)
            self.read_done = True
            self.rss = set_rss()
            self.Qi = Qi
            self.ins_prt()
            self.RS_prt()
            self.Qi_prt()
            self.file_read_url.delete(0,END)
            self.file_read_url.insert(END,'read from {}'.format(url))
        else:
            self.file_read_url.insert(END,'file doesn\'t exit')
    
    def click_to_save(self):
        if self.read_done:
            file_name = "result_at_"+str(self.time)+".txt"
            save_file = open(file_name,'w')
            content = self.RS_info.get(1.0,END) + self.ins_info.get(1.0,END) + self.Qi_info.get(1.0,END)
            save_file.write(content)
            save_file.close()
            self.file_save_url.delete(0,END)
            self.file_save_url.insert(END,'save successfully, in file: {}'.format(file_name))

    def exec_one_step(self):
        if self.time == 0:
            if ins_out(self.ins[self.nextout],self.rss,self.Qi,self.nextout):
                self.nextout += 1
                self.time += 1
                self.ins[0].out = True
                self.RS_prt()
                self.ins_prt()
                self.Qi_prt()
        elif self.end_sum < len(self.ins):
            self.time += 1
            rs = check_exec(self.rss)
            _exec(rs,self.rss,self.time,self.ins)
            
            rs = check_write_back(self.rss,self.time)
            _write_back(rs,self.rss,self.Qi)
            self.end_sum += len(rs)
            if self.nextout<len(self.ins) and ins_out(self.ins[self.nextout],self.rss,self.Qi,self.nextout):
                self.ins[self.nextout].out = True
                self.nextout += 1
            self.RS_prt()
            self.ins_prt()
            self.Qi_prt()
    
    def system_remake(self):
        if self.exec_thread_on:
            self.exec_thread_on = False
        else:
            for i in range(1,len(self.rss)):
                self.rss[i].clear()
                self.rss[i].this_second_writeback = False
            for k in self.Qi.keys():
                Qi[k] = 0
            for i in range(len(self.ins)):
                self.ins[i].clear()
            self.time = 0
            self.nextout = 0
            self.end_sum = 0
            self.RS_prt()
            self.ins_prt()
            self.Qi_prt()

    def thread_exec_one_sec_step(self):
        self.t = Thread(target = self.exec_one_sec_step, args = ())
        self.t.setDaemon(True)
        self.exec_thread_on = True
        self.t.start()

    def exec_one_sec_step(self):
        if self.time == 0:
            self.time += 1
            ins_out(self.ins[self.nextout],self.rss,self.Qi,self.nextout)
            self.ins[self.nextout].out = True
            self.nextout +=1
            self.RS_prt()
            self.ins_prt()
            self.Qi_prt()
        
        while self.end_sum < len(self.ins):
            if self.exec_thread_on:
                sleep(1)
            else:
                self.system_remake()
                break
            self.time += 1
            rs = check_exec(self.rss)
            _exec(rs,self.rss,self.time,self.ins)
            
            rs = check_write_back(self.rss,self.time)
            _write_back(rs,self.rss,self.Qi)
            self.end_sum += len(rs)
            if self.nextout<len(self.ins) and ins_out(self.ins[self.nextout],self.rss,self.Qi,self.nextout):
                self.ins[self.nextout].out = True
                self.nextout += 1
            self.RS_prt()
            self.ins_prt()
            self.Qi_prt()
    
    def optionnal(self):
        self.opt_window = Tk()
        self.opt_window.geometry('300x400+400+300')
        RSnum_label = Label(self.opt_window,text = '保留站数量:')
        RSnum_label.grid(row = 1, rowspan = 6,pady = 10, sticky = N)
        OP_delay_lable = Label(self.opt_window,text = '指令延迟:')
        OP_delay_lable.grid(row = 7, rowspan = 10 ,pady = 10, sticky = N)

        Label(self.opt_window,text = 'L.D: ').grid(row=1,column = 2,rowspan = 2, padx = 15, pady = 10, sticky = E)
        Label(self.opt_window,text = 'ADD.D/SUB.D: ').grid(row=3,rowspan = 2,column = 2,padx = 15, pady = 10, sticky = E)
        Label(self.opt_window,text = 'MUL.D/DIV.D: ').grid(row=5,rowspan = 2,column = 2, padx = 15,pady = 10, sticky = E)
        Label(self.opt_window,text = 'L.D: ').grid(row=7,rowspan = 2,column = 2, padx = 15,pady = 10, sticky = E)
        Label(self.opt_window,text = 'ADD.D: ').grid(row=9,rowspan = 2,column = 2, padx = 15,pady = 10, sticky = E)
        Label(self.opt_window,text = 'SUB.D: ').grid(row=11,rowspan = 2,column = 2, padx = 15,pady = 10, sticky = E)
        Label(self.opt_window,text = 'MUL.D: ').grid(row=13,rowspan = 2,column = 2, padx = 15,pady = 10, sticky = E)
        Label(self.opt_window,text = 'DIV.D: ').grid(row=15,rowspan = 2,column = 2, padx = 15,pady = 10, sticky = E)
        
        LDnum = Entry(self.opt_window, width = 10)
        LDnum.grid(row=1,column = 3,rowspan = 2,pady = 10)
        LDnum.insert(END,str(RS.LDnums))
        ADDnum = Entry(self.opt_window, width = 10)
        ADDnum.grid(row=3,column = 3,rowspan = 2,pady = 10)
        ADDnum.insert(END,str(RS.ADDnums))
        MULnum = Entry(self.opt_window, width = 10)
        MULnum.grid(row=5,column = 3,rowspan = 2,pady = 10)
        MULnum.insert(END,str(RS.MULDnums))

        LD = Entry(self.opt_window, width = 10)
        LD.grid(row=7,column = 3,rowspan = 2,pady = 10)
        LD.insert(END, str(RS.Delay['L.D']))
        ADD = Entry(self.opt_window, width = 10)
        ADD.grid(row=9,column = 3,rowspan = 2,pady = 10)
        ADD.insert(END, str(RS.Delay['ADD.D']))
        SUB = Entry(self.opt_window, width = 10)
        SUB.grid(row=11,column = 3,rowspan = 2,pady = 10)
        SUB.insert(END, str(RS.Delay['SUB.D']))
        MUL = Entry(self.opt_window, width = 10)
        MUL.grid(row=13,column = 3,rowspan = 2,pady = 10)
        MUL.insert(END, str(RS.Delay['MUL.D']))
        DIV = Entry(self.opt_window, width = 10)
        DIV.grid(row=15,column = 3,rowspan = 2,pady = 10)
        DIV.insert(END, str(RS.Delay['DIV.D']))

        Button(self.opt_window,text = '保存', bg='lightgreen', width = 10,command = lambda: self.option_set(nums=[LDnum,ADDnum,MULnum],delays=[LD,ADD,SUB,MUL,DIV])).grid(row = 17,column = 1, columnspan = 3)
        self.opt_window.mainloop()

    def option_set(self,nums,delays):
        LDnums = int(nums[0].get())
        ADDnums = int(nums[1].get())
        MULnums = int(nums[2].get())
        set_nums_of_Reserve_Stations(LDnums,ADDnums,MULnums)

        LD = int(delays[0].get())
        ADD = int(delays[1].get())
        SUB = int(delays[2].get())
        MUL = int(delays[3].get())
        DIV = int(delays[4].get())
        set_delay_of_OP(LD,ADD,SUB,MUL,DIV)

        self.rss = set_rss()


