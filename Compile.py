import lark

cpt = 0

op2asm = {"+": "add rax, rbx", "-": "sub rax, rbx"}

global allVar
allVar = dict()
global allPar
allPar = dict()

def createDict(ast):
    if (ast.data == "programme_vide") :
        return
    #SI le programme contient au moins une fonction
    else :
        #Pour toutes les fonctions
        for func in ast.children:
            varDict = {}
            
            param = [elt.value for elt in func.children[1].children]
            paramDict = {}
            #On crée la liste associé à la fonction
            varliste = getLocalVar(func)
            var = 1
            #Et on l'ajoute au dictionnaire
            for elt in varliste :
                if elt not in param :
                    varDict[elt] = - 8 * var
                    var += 1
            var = 2
            for elt in param :
                paramDict[elt] = 8 * var
                var +=1
            allVar[func.children[0].value] = varDict
            allPar[func.children[0].value] = paramDict
    print(allPar)
    print(allVar)
def getLocalVar(ast):
    
    varliste = list()
    
    for child in ast.children :
        try :
            if child.data == "com_asgt" :
                if child.children[0].value not in varliste :
                    varliste.append(child.children[0].value)
            elif (child.data == "com_sequence" or child.data == "com_while" or child.data == "com_if"): 
                varliste = varliste + getLocalVar(child)
        except Exception as e:
            continue
    return varliste

def compile(ast):
    """
    Convention : main est la dernière fonction
    """
    createDict(ast)
    #ast = ast.children[0]
    asmString = ""
    asmString = asmString + "extern printf, atol ;déclaration des fonctions externes\n"
    asmString = asmString + "global start ; declaration start\n"
    for child in ast.children:
        asmString += "global " + child.children[0].value + " ; declarations func\n"
    asmString = asmString + "section .data ; section des données\n"
    asmString = asmString + "long_format: db '%lld',10, 0 ; format pour les int64_t\n"
    asmString = asmString + "argc : dq 0 ; copie de argc\n" # arguments de la fonction main
    asmString = asmString + "argv : dq 0 ; copie de argv\n" 
    #asmString = asmString + asmVar
    asmString = asmString + "section .text ; instructions\n"
    asmString = asmString + start_declaration(ast.children[-1]) # section du début
    for child in ast.children: # plus qu'à compiler les fonctions
        asmString += func_declaration(child)
    #asmString += main_declaration(ast.children[-1].children[0])
    
    return asmString

def start_declaration(ast):
    """
    rdi : argc
    rsi : argv
    faut les donner a main et setup sa pile pour passer en convention 32bits. 
    """
    asmVar = "start: \n"
    asmVar += "push rbp\n" # ?
    asmVar += "mov rbp, rsp\n" # ?
    asmVar += "mov [argc], rdi\n"  # On met à l'adresse de argc la valeur de rdi
    asmVar += "mov [argv], rsi\n"
    asmVar += initMainVar(ast.children[1]) + "\n"
    asmVar += "call main\n"
    asmVar += f"add rsp, {8 * len(allPar['main'])}\n"
    asmVar += "pop rbp\n"
    asmVar += "ret\n"
    return asmVar

def initMainVar(ast):
    asmVar = ""
    if ast.data != "liste_vide":
        index = 0
        for child in ast.children:
            asmVar += "mov rbx, [argv]\n" # stock l'adresse de argv dans rbx
            asmVar += f"mov rdi, [rbx + { 8*(index+1)}]\n" # on met l'adresse de argv (= rbx) + 8*index dans rdi
            asmVar += "xor rax, rax\n" # on met rax à 0 car il contiendra la valeur de la variable
            asmVar += "call atol\n" # string to long
            asmVar += f"mov [rbp - {16 + len(allPar['main'])*8 - allPar['main'][child.value]}], rax\n" # on met la valeur de rax dans la variable
            asmVar += "push rax\n"
            index += 1
    return asmVar

def initVar(ast, funcName): # init parameters
    asmVar = ""
    if ast.data != "liste_vide":
        index = 0
        for child in ast.children:
                #asmVar += f"mov [{allPar[funcName][child.value]}], rax\n" # on met la valeur de rax dans la variable
                asmVar += f"mov [rbp +{16+8*index}], rax\n" # on met la valeur de rax dans la variable
                asmVar += "push rax\n"
                index += 1
                print("funcName : ", funcName)
                print("child.value : ", child.value)
    return asmVar

def func_declaration(ast): 
    """
    créer dict (python) des variables qui seront dedans
    rsp : pointeurs du haut de la pile 
    resulats fct : est dans rax; on fait un push rax

    quand on fait call f : rajoute adresse de (prochaine instruction) en haut de la pile et saute a l'adresse de f 
    """
    asmVar = ""
    asmVar += "%s : \n" % (ast.children[0].value)
    
    asmVar += "push rbp; Set up the stack. Save rbp\n"
    asmVar += "mov rbp, rsp\n" # on met rbp à rsp

    vars = allVar[ast.children[0].value]
    params = allPar[ast.children[0].value]
    for _ in range(len(vars)):
        asmVar += "push 0\n"
    
    asmVar += compilCommand(ast.children[2], vars, params)
    asmVar += compilReturn(ast.children[3], vars, params)

    """
    
    # pour chaque push 0 correpondant aux variables locales de la fonction, faut faire un add rsp, 8
    asmVar += f"add rsp, {8 * (len(vars))}"
    asmVar += "pop rbp\n" # prend haut de la pile et le met dans rbp"""
    asmVar += "xor rax, rax\n"
    asmVar += "ret\n"
    return asmVar
    

def compilReturn(ast, vars, params):
    asm = compilExpression(ast, vars, params)
    asm += "mov rsi, rax \n"
    asm += "mov rdi, long_format \n"
    asm += "xor rax, rax \n"
    asm += "call printf \n"
    return asm

def compilCommand(ast, vars, params):
    asmVar = ""
    if ast.data == "com_while":
        asmVar = compilWhile(ast, vars, params)
    elif ast.data == "com_if":
        asmVar = compilIf(ast, vars, params)
    elif ast.data == "com_sequence":
        asmVar = compilSequence(ast, vars, params)
    elif ast.data == "com_asgt":
        asmVar = compilAsgt(ast, vars, params)
    elif ast.data == "com_printf":
        asmVar = compilPrintf(ast, vars, params)
    return asmVar

def compilFunc(ast, vars, params):
    asmVar = initVar(ast.children[1], ast.children[0].value)
    asmVar += "call %s \n" % (ast.children[0].value)
    asmVar += f"add rsp, {8 * len(vars)}\n"
    asmVar += "pop rbp\n"
    return asmVar

def compilWhile(ast, vars, params):
    global cpt
    cpt += 1
    return f""" 
            loop{cpt} : {compilExpression(ast.children[0], vars, params)}
                cmp rax, 0
                jz fin{cpt}
                {compilCommand(ast.children[1], vars, params)}
                jmp loop{cpt}
            fin{cpt} :
        """

def compilIf(ast, vars, params):
    global cpt
    cpt += 1
    return f""" 
            {compilExpression(ast.children[0], vars, params)}
            cmp rax, 0
            jz fin{cpt}
            {compilCommand(ast.children[1], vars, params)}
            fin{cpt} :
        """

def compilSequence(ast, vars, params):
    asm = ""
    for child in ast.children :
        asm +=compilCommand(child, vars, params)
    return asm

def compilAsgt(ast, vars, params):
    asm = f"{compilExpression(ast.children[1], vars, params)}\n"
    if ast.children[0].value in vars :
        asm += f"mov [rbp {vars[ast.children[0].value]}], rax \n"
    elif ast.children[0].value in params :
        asm += f"mov [rbp + {params[ast.children[0].value]}], rax \n"

    return asm

def compilPrintf(ast, vars, params):
    asm = compilExpression(ast.children[0], vars, params)
    asm += "mov rsi, rax \n"
    asm += "mov rdi, long_format \n"
    asm += "xor rax, rax \n"
    asm += "call printf \n"
    return asm

def compilExpression(ast, vars, params):
    if ast.data == "exp_variable":
        if ast.children[0].value in vars :
            return f"mov rax, [rbp {vars[ast.children[0].value]}]\n"
        elif ast.children[0].value in params :
            return f"mov rax, [rbp + {params[ast.children[0].value]}]\n"
        else : 
            print(ast)
    elif ast.data ==  "exp_nombre":
        return f"mov rax, {ast.children[0].value}\n"
    elif ast.data == "exp_binaire": 
        return f"""
                {compilExpression(ast.children[2], vars, params)}
                push rax
                {compilExpression(ast.children[0], vars, params)}
                pop rbx
                {op2asm[ast.children[1].value]}
                """
    elif ast.data == "exp_func":
        return f"{compilFunc(ast, vars, params)}\n"
    
    return ""