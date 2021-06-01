Qi = {'F'+str(2*i):0 for i in range(7)}
class RS:                   #reserve station
    LDnums = 2
    ADDnums = 3
    MULDnums = 2
    Delay = {
        'L.D':2,
        'ADD.D':3,
        'SUB.D':3,
        'DIV.D':41,
        'MUL.D':11
    }
    def __init__(self):
        self.Name = ''
        self.Qj = 0
        self.Qk = 0
        self.Vj = ''
        self.Vk = ''
        self.A = ''
        self.busy = False
        self.OP = ''
        self.OPtype = 0
        self.delay = 0
        self.write_back_time = 0
        self.res = ''
        self.current_ins = -1
        self.this_second_writeback = False
    def clear(self):
        self.Qj = self.Qk = self.delay = self.write_back_time = 0
        self.current_ins = -1
        self.busy = False
        self.Vj = self.Vk = self.A = self.OP = self.res = ''

class Ins:                  #instructions
    Regs = {'F'+str(2*i):'' for i in range(7)}                  
    def __init__(self):
        self.OP = ''
        self.OPtype= 0
        self.des = ''
        self.rs = ''
        self.rt = ''
        self.Imm = ''
        self.out = False
        self.exec_start = 9999
        self.exec_end = 9999
        self.write_back = 9999
    def clear(self):
        self.out = False
        self.exec_start = 9999
        self.exec_end = 9999
        self.write_back = 9999

def ins_out(ins,rss,Qi,cur_ins):
    if ins == '':
        return False
    for i in range(1,len(rss)):
        if rss[i].this_second_writeback:
            rss[i].this_second_writeback = False
        elif rss[i].busy == False and rss[i].OPtype == ins.OPtype:
            if ins.rs in ins.Regs.keys() and (ins.rt in ins.Regs.keys() or ins.rt == '') :  
                if Qi[ins.rs] == 0:
                    rss[i].Qj = 0
                    rss[i].Vj = Ins.Regs[ins.rs]
                    if rss[i].Vj == '':
                        rss[i].Vj = ins.rs
                else:
                    rss[i].Qj = Qi[ins.rs]
                if ins.rt != '':
                    if Qi[ins.rt] == 0:
                        rss[i].Qk = 0
                        rss[i].Vk = Ins.Regs[ins.rt]
                        if rss[i].Vk == '':
                            rss[i].Vk = "Regs[{}]".format(ins.rt)
                    else:
                        rss[i].Qk = Qi[ins.rt]
                else:
                    rss[i].Qk = 0
                    rss[i].Vk = ''
                rss[i].A = ins.Imm
                rss[i].busy = True
                rss[i].OP = ins.OP
                Qi[ins.des] = i
                rss[i].current_ins = cur_ins
                return True
            else:           #rs and rt are not Float registers, record their names directly
                rss[i].OP = ins.OP
                rss[i].Vj = ins.rs
                rss[i].Vk = ins.rt
                rss[i].Qj = rss[i].Qk = 0
                rss[i].A = ins.Imm
                rss[i].busy = True
                Qi[ins.des] = i
                rss[i].current_ins = cur_ins
                return True
    return False     


def check_exec(rss):
    sub_rss = []
    for i in range(1,len(rss)):
        if rss[i].busy == True and rss[i].write_back_time == 0 and rss[i].Qj == 0 and rss[i].Qk == 0:
            sub_rss.append(i)
    return sub_rss

def _exec(sub_rss,rss,time,ins):
    for i in sub_rss:
        rss[i].delay = RS.Delay[rss[i].OP]
        ins[rss[i].current_ins].exec_start = time
        ins[rss[i].current_ins].exec_end = time + rss[i].delay
        ins[rss[i].current_ins].write_back = time + rss[i].delay +1
        rss[i].write_back_time = time + rss[i].delay + 1
        if rss[i].OP == 'L.D':
            rss[i].A = "{}+{}".format(rss[i].A,rss[i].Vj)
            rss[i].res = "Mem[{}]".format(rss[i].A)
        elif rss[i].OP == 'ADD.D':
            rss[i].res = "({})+({})".format(rss[i].Vj,rss[i].Vk)
        elif rss[i].OP == 'SUB.D':
            rss[i].res = "({})-({})".format(rss[i].Vj,rss[i].Vk)
        elif rss[i].OP == 'MUL.D':
            rss[i].res = "({})*({})".format(rss[i].Vj,rss[i].Vk)
        elif rss[i].OP == 'DIV.D':
            rss[i].res = "({})/({})".format(rss[i].Vj,rss[i].Vk)
        
def check_write_back(rss,time):
    sub_rss = []
    for i in range(1,len(rss)):
        if rss[i].busy == True and rss[i].write_back_time == time:
            sub_rss.append(i)
            rss[i].this_second_writeback = True
    return sub_rss

def _write_back(rs,rss,Qi):
    for i in rs:
        for j in range(1,len(rss)):
            if j != i :
                if rss[j].Qj == i:
                    rss[j].Qj = 0
                    rss[j].Vj = rss[i].res
                if rss[j].Qk == i:
                    rss[j].Qk =0
                    rss[j].Vk = rss[i].res
        for key in Qi.keys():
            if Qi[key] == i:
                Qi[key] = 0
                Ins.Regs[key] = rss[i].res
        rss[i].clear()
        
def true(a):
    if a:
        return 'true'
    else:
        return 'false'

def line_to_ins(line):
    if line == '\n':
        return ''
    l = line.split('\n')[0].split(' ')
    #print(l)
    ins = Ins()
    ins.OP = l[1]
    #print(ins.OP)
    pars = l[2].split(',')
    #print(pars)
    if ins.OP == 'L.D':
        ins.OPtype = 1
        ins.des = pars[0]
        rs = pars[1].split('(')
        ins.Imm = rs[0]
        ins.rs = rs[1].split(')')[0]
    else:
        if ins.OP == 'ADD.D' or ins.OP == 'SUB.D':
            ins.OPtype = 2
        if ins.OP == 'MUL.D' or ins.OP == 'DIV.D':
            ins.OPtype = 3
        ins.des = pars[0]
        ins.rs = pars[1]
        ins.rt = pars[2]

    return ins

def set_nums_of_Reserve_Stations(LDnums=2,ADDnums=3,MULDnums=2):
    RS.LDnums = LDnums
    RS.ADDnums = ADDnums
    RS.MULDnums = MULDnums

def set_delay_of_OP(LD,ADD,SUB,MUL,DIV):
    RS.Delay['L.D'] = LD
    RS.Delay['ADD.D'] = ADD
    RS.Delay['SUB.D'] = SUB
    RS.Delay['MUL.D'] = MUL
    RS.Delay['DIV.D'] = DIV

def get_ins(URL='codes.txt'):
    instruction_file = open(URL)
    codes = instruction_file.readlines()
    ins = list()
    for c in codes:
        instruction = line_to_ins(c)
        if type(instruction) == Ins:
            ins.append(instruction)
    return ins

def set_rss():
    RSnum = RS.LDnums + RS.ADDnums + RS.MULDnums
    rss = ['']
    for i in range(RSnum):
        rss.append(RS())
    for i in range(1,RSnum+1):
        if i<=RS.LDnums:
            rss[i].OPtype = 1
            rss[i].Name = "L.D{}".format(i)
        if i>RS.LDnums and i<=RS.LDnums + RS.ADDnums:
            rss[i].OPtype = 2
            rss[i].Name = "ADD.D{}".format(i-RS.LDnums)
        if i>RS.LDnums + RS.ADDnums and i<=RS.LDnums + RS.ADDnums + RS.MULDnums:
            rss[i].OPtype = 3
            rss[i].Name = "MULT.D{}".format(i-RS.ADDnums-RS.LDnums)
    return rss