import lark
import Compile

grammaire = """
%import common.SIGNED_NUMBER  //bibliothèque lark.
%import common.WS
%ignore WS
// %ignore /[ ]/   #ignore les blancs, mais l'arbre ne contient pas l'information de leur existence. problématique du pretty printer. 

VARIABLE : /[a-zA-Z_][a-zA-Z0-9]*/
VARIABLE_FCT : /[a-zA-Z_][a-zA-Z0-9]*/ // Fonctions
NOMBRE : SIGNED_NUMBER
FLOAT : /-?[0-9]*\.[0-9]+/ // Floats, ex: 0.5, 0.0, -0.5
// NOMBRE : /[1-9][0-9]*/
OPBINAIRE: /[+*\/&><]/|">="|"-"|">>"  //lark essaie de faire les tokens les plus long possible

expression: VARIABLE -> exp_variable
| NOMBRE         -> exp_nombre 
| FLOAT         -> exp_float
| expression OPBINAIRE expression -> exp_binaire
| VARIABLE_FCT "(" liste_var ")" -> exp_func // Fonctions

commande : VARIABLE "=" expression ";"-> com_asgt //les exp entre "" ne sont pas reconnues dans l'arbre syntaxique
| "printf" "(" expression ")" ";" -> com_printf
| commande+ -> com_sequence
| "while" "(" expression ")" "{" commande "}" -> com_while
| "if" "(" expression ")" "{" commande "}" "else" "{" commande "}" -> com_if

liste_var :                -> liste_vide
| VARIABLE ("," VARIABLE)* -> liste_normale

fonction : VARIABLE_FCT "(" liste_var ")" "{" commande "return" "(" expression ")" ";" "}" -> function // function

programme :  -> programme_vide        // Fonctions
| fonction (" "* fonction)* -> liste_func     // Fonctions
"""

parser = lark.Lark(grammaire, start = "programme")

t = parser.parse("""
                 test(x) {
                    z = x + 1;
                    return(z);
                 }

                 main(x,y){
                    y = test(y);
                    printf(y);
                    return (y);
                }
                 """)

def pretty_printer_liste_var(t):
    if t.data == "liste_vide" :
        return ""
    return ", ".join([u.value for u in t.children])

def pretty_printer_commande(t):
    if (t.data == "com_asgt"):
        return f"{t.children[0].value} = {pretty_printer_expression(t.children[1])} ;"
    if (t.data == "com_printf"):
        return f"printf ({pretty_printer_expression(t.children[0])}) ;"
    if (t.data == "com_while"):
        return "while (%s){ %s}" % (pretty_printer_expression(t.children[0]), pretty_printer_commande(t.children[1]))
    if (t.data == "com_if"):
        return "if (%s){ %s} else { %s}" % (pretty_printer_expression(t.children[0]), pretty_printer_commande(t.children[1]), pretty_printer_commande(t.children[2]))
    if (t.data == "com_sequence"):
        return "\n".join([pretty_printer_commande(u) for u in t.children])
    
def pretty_printer_expression(t):
    if t.data in ("exp_variable", "exp_nombre", "exp_float"):
        return t.children[0].value
    elif t.data == "exp_func":
        return "%s ( %s )\n" % (t.children[0].value, pretty_printer_liste_var(t.children[1]))
    return f"{pretty_printer_expression(t.children[0])} {t.children[1].value} {pretty_printer_expression(t.children[2])}"

def pretty_printer_function(t):
    return  "%s (%s) { %s return (%s); }\n" % (t.children[0].value,
                                                pretty_printer_liste_var(t.children[1]), 
                                                pretty_printer_commande(t.children[2]),
                                                    pretty_printer_expression( t.children[3]))
def pretty_print(t):
    if (t.data == "liste_func"):
        #return "%s \n %s " % (pretty_print(t.children[0]),pretty_print(t.children[1]))
        return "\n ".join([pretty_printer_function(u) for u in t.children])
    elif (t.data == "programme_vide"):
        return ""
        
        #t_main = t.children[0]
        #return  "main (%s) { %s return (%s); }\n" % (pretty_printer_liste_var(t_main.children[0]), 
                                                #pretty_printer_commande(t_main.children[1]),
                                                #pretty_printer_expression(t_main.children[2]))
"""print(t)
print(pretty_print(t))

Compile.createDict(t)"""